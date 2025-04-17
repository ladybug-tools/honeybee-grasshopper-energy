# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
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
            objects as a single string following the IDF format. This input can
            be used to write objects into the IDF that are not currently supported
            by Honeybee.
        _folder_: An optional folder on this computer, into which the IDF and result
            files will be written.
        _write: Set to "True" to write out the honeybee JSONs (containing the Honeybee
            Model and Simulation Parameters) and write the OpenStudio Model file (OSM).
            This process will also write either an EnergyPlus Input Data File (IDF)
            or an OpenStudio Workflow file (OSW), which can be used to run the
            model through EnergyPlus. Most models can be simulated with just
            and IDF and so no OWS will be written. However, an OSW will be used
            if any measures_ have been connected or if the simulation parameters
            contain an efficiency standard.
        run_: Set to "True" to translate the Honeybee jsons to an OpenStudio Model
            (.osm) and EnergyPlus Input Data File (.idf) and then simulate the
            .idf in EnergyPlus. This will ensure that all result files appear
            in their respective outputs from this component.
            _
            This input can also be the integer "2", which will run the whole translation
            and simulation silently (without any batch windows).

    Returns:
        report: Check here to see a report of the EnergyPlus run.
        jsons: The file paths to the honeybee JSON files that describe the Model and
            SimulationParameter. These will be translated to an OpenStudio model.
        osw: File path to the OpenStudio Workflow JSON on this machine (if necessary
            for simulation). This workflow is executed using the OpenStudio
            command line interface (CLI) and it includes any connected
            measures_. Will be None if no OSW is needed for the simulation.
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
ghenv.Component.Message = '1.8.3'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import os
import re
import json
import subprocess

try:
    from ladybug.futil import preparedir, nukedir, copy_file_tree
    from ladybug.epw import EPW
    from ladybug.stat import STAT
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.config import folders
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.simulation.parameter import SimulationParameter
    from honeybee_energy.measure import Measure
    from honeybee_energy.run import to_openstudio_sim_folder, run_osw, run_idf, \
        output_energyplus_files, _parse_os_cli_failure
    from honeybee_energy.result.err import Err
    from honeybee_energy.config import folders as energy_folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from honeybee_openstudio.openstudio import OSModel
except (ImportError, AssertionError):  # Openstudio C# bindings are not usable
    OSModel = None

try:
    from lbt_recipes.version import check_openstudio_version
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
    from ladybug_rhino.config import units_system
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

ROOM_COUNT_THRESH = 1000  # threshold at which the CLI is used for translation


def measures_to_folder(measures, sim_folder):
    osw_dict = {}  # dictionary that will be turned into the OSW JSON
    osw_dict['steps'] = []
    mea_folder = os.path.join(sim_folder, 'measures')
    # ensure measures are correctly ordered
    m_dict = {'ModelMeasure': [], 'EnergyPlusMeasure': [], 'ReportingMeasure': []}
    for measure in measures:
        assert isinstance(measure, Measure), 'Expected honeybee-energy Measure. ' \
            'Got {}.'.format(type(measure))
        m_dict[measure.type].append(measure)
    sorted_measures = m_dict['ModelMeasure'] + m_dict['EnergyPlusMeasure'] + \
        m_dict['ReportingMeasure']
    # add the measures and the measure paths to the OSW
    for measure in sorted_measures:
        measure.validate()  # ensure that all required arguments have values
        osw_dict['steps'].append(measure.to_osw_dict())  # add measure to workflow
        dest_folder = os.path.join(mea_folder, os.path.basename(measure.folder))
        copy_file_tree(measure.folder, dest_folder)
        test_dir = os.path.join(dest_folder, 'tests')
        if os.path.isdir(test_dir):
            nukedir(test_dir, rmdir=True)
    # write the dictionary to a workflow.osw
    osw_json = os.path.join(mea_folder, 'workflow.osw')
    try:
        with open(osw_json, 'w') as fp:
            json.dump(osw_dict, fp, indent=4)
    except UnicodeDecodeError:  # non-unicode character in the dictionary
        with open(osw_json, 'w') as fp:
            json.dump(osw_dict, fp, indent=4, ensure_ascii=False)
    return mea_folder


if all_required_inputs(ghenv.Component) and _write:
    # check the presence of openstudio and check that the version is compatible
    check_openstudio_version()
    assert isinstance(_model, Model), \
        'Expected Honeybee Model for _model input. Got {}.'.format(type(_model))

    # process the simulation parameters
    if _sim_par_ is None:
        sim_par = SimulationParameter()
        sim_par.output.add_zone_energy_use()
        sim_par.output.add_hvac_energy_use()
        sim_par.output.add_electricity_generation()
    else:
        sim_par = _sim_par_.duplicate()  # ensure input is not edited

    # assign design days from the DDY next to the EPW if there are None
    if len(sim_par.sizing_parameter.design_days) == 0:
        msg = None
        folder, epw_file_name = os.path.split(_epw_file)
        ddy_file = os.path.join(folder, epw_file_name.replace('.epw', '.ddy'))
        if os.path.isfile(ddy_file):
            try:
                sim_par.sizing_parameter.add_from_ddy_996_004(ddy_file)
            except AssertionError:
                pass
            if len(sim_par.sizing_parameter.design_days) == 0:
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
            sim_par.sizing_parameter.design_days = des_days
            msg = msg + '\nDesign days were generated from the input _epw_file but this ' \
                '\nis not as accurate as design days from DDYs distributed with the EPW.'
            give_warning(ghenv.Component, msg)
            print(msg)
    if sim_par.sizing_parameter.climate_zone is None:
        stat_file = os.path.join(folder, epw_file_name.replace('.epw', '.stat'))
        if os.path.isfile(stat_file):
            stat_obj = STAT(stat_file)
            sim_par.sizing_parameter.climate_zone = stat_obj.ashrae_climate_zone

    # process the simulation folder name and the directory
    _folder_ = folders.default_simulation_folder if _folder_ is None else _folder_
    clean_name = re.sub(r'[^.A-Za-z0-9_-]', '_', _model.display_name)
    directory = os.path.join(_folder_, clean_name, 'openstudio')

    # delete any existing files in the directory and prepare it for simulation
    nukedir(directory, True)
    preparedir(directory)
    sch_directory = os.path.join(directory, 'schedules')
    preparedir(sch_directory)

    # write the model and simulation parameter to JSONs
    model_json = os.path.join(directory, '{}.hbjson'.format(clean_name))
    with open(model_json, 'wb') as fp:
        model_str = json.dumps(_model.to_dict(), ensure_ascii=False)
        fp.write(model_str.encode('utf-8'))
    sim_par_json = os.path.join(directory, 'simulation_parameter.json')
    with open(sim_par_json, 'w') as fp:
        json.dump(sim_par.to_dict(), fp)
    jsons = [model_json, sim_par_json]

    # determine whether to run the translation with cPython or IronPython
    use_ironpython = False
    if OSModel is not None:
        vent_sim_control = _model.properties.energy.ventilation_simulation_control
        if vent_sim_control.vent_control_type == 'SingleZone':
            if len(_model.rooms) < ROOM_COUNT_THRESH:
                osc_version = tuple(int(v) for v in OSModel().version().str().split('.'))
                if osc_version == energy_folders.openstudio_version:
                    use_ironpython = True

    if use_ironpython:  # translate the model using IronPython methods
        add_str = '\n'.join(add_str_) if len(add_str_) != 0 and \
            add_str_[0] is not None else None
        osm, osw, idf = to_openstudio_sim_folder(
            _model, directory, epw_file=_epw_file, sim_par=sim_par,
            schedule_directory=sch_directory, enforce_rooms=True,
            additional_measures=measures_, strings_to_inject=add_str)
        if run_ > 0:
            silent = True if run_ > 1 else False
            if idf is not None:  # run the IDF directly through E+
                sql, zsz, rdd, html, err = run_idf(idf, _epw_file, silent=silent)
            else:
                osm, idf = run_osw(osw, measures_only=False, silent=silent)
                if idf is None or not os.path.isfile(idf):
                    _parse_os_cli_failure(directory)
                sql, zsz, rdd, html, err = output_energyplus_files(os.path.dirname(idf))
    else:  # translate the model with cPython using OpenStudio CLI
        # write additional strings and measures to a folder
        add_idf = None
        if len(add_str_) != 0 and add_str_[0] is not None:
            add_str = '\n'.join(add_str_)
            add_idf = os.path.join(directory, 'additional_strings.idf')
            with open(add_idf, 'w') as fp:
                fp.write(add_str)
        measure_folder = None
        if len(measures_) != 0 and measures_[0] is not None:
            measure_folder = measures_to_folder(measures_, directory)

        # put together the arguments for the command to be run
        if run_ > 0:  # use the simulate command
            cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'simulate',
                    'model', model_json, _epw_file, '--sim-par-json', sim_par_json,
                    '--folder', directory]
        else:  # use the translate command
            cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'translate',
                    'model-to-sim-folder', model_json, _epw_file, '--sim-par-json',
                    sim_par_json, '--folder', directory]
        if add_idf is not None:
            cmds.append('--additional-idf')
            cmds.append(add_idf)
        if measure_folder is not None:
            cmds.append('--measures')
            cmds.append(measure_folder)
        osm = os.path.join(directory, 'in.osm')
        idf = os.path.join(directory, 'run', 'in.idf')

        # execute the command
        custom_env = os.environ.copy()
        custom_env['PYTHONHOME'] = ''
        shell = False if os.name == 'nt' and run_ == 1 else True
        process = subprocess.Popen(cmds, shell=shell, env=custom_env)
        result = process.communicate()  # freeze the canvas while running

        # check if any part of the translation failed
        osw = os.path.join(directory, 'workflow.osw')
        osw = osw if os.path.isfile(osw) else None
        if not os.path.isfile(osm):
            print(' '.join(cmds))
            raise ValueError('Failed to translate Model to OpenStudio.')
        if run_ > 0:
            if not os.path.isfile(idf):
                print(' '.join(cmds))
                raise ValueError('Failed to translate Model to EnergyPlus.')
            sql, zsz, rdd, html, err = output_energyplus_files(os.path.dirname(idf))

    # parse the error log and report any warnings
    if run_ >= 1 and err is not None:
        err_obj = Err(err)
        print(err_obj.file_contents)
        for warn in err_obj.severe_errors:
            give_warning(ghenv.Component, warn)
        for error in err_obj.fatal_errors:
            raise Exception(error)
