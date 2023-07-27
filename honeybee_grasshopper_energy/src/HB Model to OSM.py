# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Write a honeybee Model to an OSM file (OpenStudio Model), which can then be translated
to an IDF file and then run through EnergyPlus.

-
    Args:
        _model: A honeybee model object possessing all geometry and corresponding
            energy simulation properties.
        _epw_file: Path to an .epw file on this computer as a text string.
        _sim_par_: A honeybee Energy SimulationParameter object that describes all
            of the setting for the simulation. If None, some default simulation
            parameters will automatically be used.
        measures_: An optional list of measures to apply to the OpenStudio model
            upon export. Use the "HB Load Measure" component to load a measure
            into Grasshopper and assign input arguments. Measures can be
            downloaded from the NREL Building Components Library (BCL) at
            (https://bcl.nrel.gov/).
        add_str_: THIS OPTION IS JUST FOR ADVANCED USERS OF ENERGYPLUS.
            You can input additional text strings here that you would like
            written into the IDF.  The input here should be complete EnergyPlus
            objects as a single string following the IDF format. This input ca
            be used to write objects into the IDF that are not currently supported
            by Honeybee.
        _folder_: An optional folder on this computer, into which the IDF and result
            files will be written.
        _write: Set to "True" to write out the honeybee jsons (containing the Honeybee
            Model and Simulation Parameters) and write the OpenStudio Workflow
            (.osw) file with instructions for executing the simulation.
        run_: Set to "True" to translate the Honeybee jsons to an OpenStudio Model
            (.osm) and EnergyPlus Input Data File (.idf) and then simulate the
            .idf in EnergyPlus. This will ensure that all result files appear
            in their respective outputs from this component.
            _
            This input can also be the integer "2", which will only translate the
            honeybee jsons to an osm and idf format without running the model
            through EnergyPlus.
            _
            It can also be the integer "3", which will run the whole translation
            and simulation silently (without any batch windows).

    Returns:
        report: Check here to see a report of the EnergyPlus run.
        jsons: The file paths to the honeybee JSON files that describe the Model and
            SimulationParameter. These will be translated to an OpenStudio model.
        osw: File path to the OpenStudio Workflow JSON on this machine. This workflow
            is executed using the OpenStudio command line interface (CLI) and
            it includes measures to translate the Honeybee model JSON as well
            as any other connected measures_.
        osm: The file path to the OpenStudio Model (OSM) that has been generated
            on this computer.
        idf: The file path of the EnergyPlus Input Data File (IDF) that has been
            generated on this computer.
        sql: The file path of the SQL result file that has been generated on this
            computer. This will be None unless run_ is set to True.
        zsz: Path to a .csv file containing detailed zone load information recorded
            over the course of the design days. This will be None unless run_ is
            set to True.
        rdd: The file path of the Result Data Dictionary (.rdd) file that is
            generated after running the file through EnergyPlus.  This file
            contains all possible outputs that can be requested from the EnergyPlus
            model. Use the "HB Read Result Dictionary" component to see what outputs
            can be requested.
        html: The HTML file path containing all requested Summary Reports.
"""

ghenv.Component.Name = 'HB Model to OSM'
ghenv.Component.NickName = 'ModelToOSM'
ghenv.Component.Message = '1.6.4'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

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
    from honeybee_energy.run import to_openstudio_osw, run_osw, run_idf, \
        output_energyplus_files
    from honeybee_energy.result.err import Err
    from honeybee_energy.result.osw import OSW
    from honeybee_energy.config import folders as energy_folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from lbt_recipes.version import check_openstudio_version
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
    from ladybug_rhino.config import units_system
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _write:
    # check the presence of openstudio and check that the version is compatible
    check_openstudio_version()

    # process the simulation parameters
    if _sim_par_ is None:
        _sim_par_ = SimulationParameter()
        _sim_par_.output.add_zone_energy_use()
        _sim_par_.output.add_hvac_energy_use()
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
    clean_name = re.sub(r'[^.A-Za-z0-9_-]', '_', _model.display_name)
    directory = os.path.join(_folder_, clean_name, 'openstudio')

    # duplicate model to avoid mutating it as we edit it for energy simulation
    _model = _model.duplicate()
    # scale the model if the units are not meters
    if _model.units != 'Meters':
        _model.convert_to_units('Meters')
    # remove degenerate geometry within native E+ tolerance of 0.01 meters
    try:
        _model.remove_degenerate_geometry(0.01)
    except ValueError:
        error = 'Failed to remove degenerate Rooms.\nYour Model units system is: {}. ' \
            'Is this correct?'.format(units_system())
        raise ValueError(error)

    # auto-assign stories if there are none since most OpenStudio measures need these
    if len(_model.stories) == 0 and len(_model.rooms) != 0:
        _model.assign_stories_by_floor_height()

    # delete any existing files in the directory and prepare it for simulation
    nukedir(directory, True)
    preparedir(directory)
    sch_directory = os.path.join(directory, 'schedules')
    preparedir(sch_directory)

    # write the model parameter JSONs
    model_dict = _model.to_dict(triangulate_sub_faces=True)
    _model.properties.energy.add_autocal_properties_to_dict(model_dict)
    model_json = os.path.join(directory, '{}.hbjson'.format(clean_name))
    if (sys.version_info < (3, 0)):  # we need to manually encode it as UTF-8
        with open(model_json, 'wb') as fp:
            model_str = json.dumps(model_dict, indent=4, ensure_ascii=False)
            fp.write(model_str.encode('utf-8'))
    else:
        with open(model_json, 'w', encoding='utf-8') as fp:
            model_str = json.dump(model_dict, fp, indent=4, ensure_ascii=False)

    # write the simulation parameter JSONs
    sim_par_dict = _sim_par_.to_dict()
    sim_par_json = os.path.join(directory, 'simulation_parameter.json')
    with open(sim_par_json, 'w') as fp:
        json.dump(sim_par_dict, fp)

    # process any measures input to the component
    measures = None if len(measures_) == 0 or measures_[0] is None else measures_
    no_report_meas = True if measures is None else \
        all(meas.type != 'ReportingMeasure' for meas in measures)
    str_inject = None if no_report_meas or add_str_ == [] or add_str_[0] is None \
        else '\n'.join(add_str_)

    # collect the two jsons for output and write out the osw file
    jsons = [model_json, sim_par_json]
    osw = to_openstudio_osw(
        directory, model_json, sim_par_json, additional_measures=measures,
        epw_file=_epw_file, schedule_directory=sch_directory,
        strings_to_inject=str_inject)

    # run the measure to translate the model JSON to an openstudio measure
    silent = True if run_ == 3 else False
    if run_ > 0 and not no_report_meas:  # everything must run with OS CLI
        if run_ == 1:  # simulate everything at once
            osm, idf = run_osw(osw, measures_only=False, silent=silent)
            sql, zsz, rdd, html, err = output_energyplus_files(os.path.dirname(idf))
        else:  # remove reporting measure and give a warning
            m_to_remove = [m.identifier for m in measures if m.type == 'ReportingMeasure']
            with open(osw, 'r') as op:
                osw_data = json.load(op)
            s_to_remove = []
            for i, step in enumerate(osw_data['steps']):
                if step['measure_dir_name'] in m_to_remove:
                    s_to_remove.append(i)
            for i in reversed(s_to_remove):
                osw_data['steps'].pop(i)
            with open(osw, 'wb') as fp:
                workflow_str = json.dumps(osw_data, indent=4, ensure_ascii=False)
                fp.write(workflow_str.encode('utf-8'))
            msg = 'The following were reporting measures and were not\n' \
                'included in the OSW to avoid running the simulation:\n{}'.format(
                    '\n'.join(m_to_remove))
            give_warning(ghenv.Component, msg)
            print(msg)
            osm, idf = run_osw(osw, silent=silent)
    elif run_ > 0:  # no reporting measure; simulate separately from measure application
        osm, idf = run_osw(osw, silent=silent)
        # process the additional strings
        if len(add_str_) != 0 and add_str_[0] is not None and idf is not None:
            add_str = '\n'.join(add_str_)
            with open(idf, "a") as idf_file:
                idf_file.write(add_str)
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
        elif run_ in (1, 3):  # run the resulting idf throught EnergyPlus
            sql, zsz, rdd, html, err = run_idf(idf, _epw_file, silent=silent)

    # parse the error log and report any warnings
    if run_ in (1, 3) and err is not None:
        err_obj = Err(err)
        print(err_obj.file_contents)
        for warn in err_obj.severe_errors:
            give_warning(ghenv.Component, warn)
        for error in err_obj.fatal_errors:
            raise Exception(error)
