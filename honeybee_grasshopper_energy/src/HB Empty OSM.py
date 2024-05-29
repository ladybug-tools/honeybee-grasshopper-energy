# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create an empty OpenStudio Model (OSM) file with no building geometry.
_
This is useful as a starting point for OSMs to which detailed Ironbug systems
will be added. Such models with only Ironbug HVAC components can simulate
in EnergyPlus if they use the LoadProfile:Plant object to represent the
building loads.
_
They are useful for evaluating the performance of such heating/cooling plants
and, by setting the simulation parameters and EPW file with this component, any
sizing criteria for the plant components can be set.

-
    Args:
        _epw_file: Path to an .epw file on this computer as a text string.
        _sim_par_: A honeybee Energy SimulationParameter object that describes all
            of the setting for the simulation. If None, some default simulation
            parameters will automatically be used.
        _folder_: An optional folder on this computer, into which the IDF and result
            files will be written.
        _write: Set to "True" to create the empty OSM file.

    Returns:
        report: Reports, errors, warnings, etc.
        osw: File path to the OpenStudio Workflow JSON on this machine. This workflow
            is executed using the OpenStudio command line interface (CLI), which
            will create the empty OSM following the input simulation parameter
            specifications.
        osm: The file path to the empty OpenStudio Model (OSM) that has been generated
            on this computer.
        idf: The file path of the empty EnergyPlus Input Data File (IDF) that has been
            generated on this computer.
"""

ghenv.Component.Name = 'HB Empty OSM'
ghenv.Component.NickName = 'EmptyOSM'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

import sys
import os
import re
import json

try:
    from ladybug.futil import preparedir, nukedir
    from ladybug.epw import EPW
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    import honeybee.config as hb_config
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.simulation.parameter import SimulationParameter
    from honeybee_energy.run import to_empty_osm_osw, run_osw
    from honeybee_energy.result.osw import OSW
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from lbt_recipes.version import check_openstudio_version
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _write:
    # check the presence of openstudio
    check_openstudio_version()

    # process the simulation parameters
    if _sim_par_ is None:
        _sim_par_ = SimulationParameter()
        _sim_par_.output.add_zone_energy_use()
        _sim_par_.output.add_hvac_energy_use()
        _sim_par_.output.add_electricity_generation()
    else:
        _sim_par_ = _sim_par_.duplicate()  # ensure input is not edited

    # assign design days from the DDY next to the EPW if there are None
    if len(_sim_par_.sizing_parameter.design_days) == 0:
        msg = None
        folder, epw_file_name = os.path.split(_epw_file)
        ddy_file = os.path.join(folder, epw_file_name.replace('.epw', '.ddy'))
        if os.path.isfile(ddy_file):
            try:
                _sim_par_.sizing_parameter.add_from_ddy_996_004(ddy_file)
            except AssertionError:
                msg = 'No ddy_file_ was input into the _sim_par_ sizing ' \
                    'parameters\n and no design days were found in the .ddy file '\
                    'next to the _epw_file.'
        else:
             msg = 'No ddy_file_ was input into the _sim_par_ sizing parameters\n' \
                'and no .ddy file was found next to the _epw_file.'
        if msg is not None:
            epw_obj = EPW(_epw_file)
            des_days = [epw_obj.approximate_design_day('WinterDesignDay'),
                        epw_obj.approximate_design_day('SummerDesignDay')]
            _sim_par_.sizing_parameter.design_days = des_days
            msg = msg + '\nDesign days were generated from the input _epw_file but this ' \
                '\nis not as accurate as design days from DDYs distributed with the EPW.'
            give_warning(ghenv.Component, msg)
            print(msg)

    # process the simulation folder name and the directory
    _folder_ = hb_config.folders.default_simulation_folder if _folder_ is None else _folder_
    directory = os.path.join(_folder_, 'openstudio')

    # delete any existing files in the directory and prepare it for simulation
    nukedir(directory, True)
    preparedir(directory)

    # write the simulation parameter JSON
    sim_par_dict = _sim_par_.to_dict()
    sim_par_json = os.path.join(directory, 'simulation_parameter.json')
    if (sys.version_info < (3, 0)):  # we need to manually encode it as UTF-8
        with open(sim_par_json, 'wb') as fp:
            sim_par_str = json.dumps(sim_par_dict, ensure_ascii=False)
            fp.write(sim_par_str.encode('utf-8'))
    else:
        with open(sim_par_json, 'w', encoding='utf-8') as fp:
            sim_par_str = json.dump(sim_par_dict, fp, ensure_ascii=False)

    # collect the two jsons for output and write out the osw file
    osw = to_empty_osm_osw(directory, sim_par_json, epw_file=_epw_file)

    # run the measure to translate the JSON
    osm, idf = run_osw(osw, silent=True)
    if idf is None:  # measures failed to run correctly; parse out.osw
        log_osw = OSW(os.path.join(directory, 'out.osw'))
        errors = []
        for error, tb in zip(log_osw.errors, log_osw.error_tracebacks):
            if 'Cannot create a surface' in error:
                error = 'Your Rhino Model units system is: {}. ' \
                    'Is this correct?\n{}'.format(units_system(), error)
            print(tb)
            errors.append(error)
        raise Exception('Failed to run OpenStudio CLI:\n{}'.format('\n'.join(errors)))
