# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

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
            written into the IDF.  The strings input here should be complete
            EnergyPlus objects that are correctly formatted. This input can be used to
            write objects into the IDF that are not currently supported by Honeybee.
        _folder_: An optional folder on this computer, into which the IDF and result
            files will be written.  NOTE THAT DIRECTORIES INPUT HERE SHOULD NOT HAVE
            ANY SPACES OR UNDERSCORES IN THE FILE PATH.
        _write: Set to "True" to write out the jsons and the osw for simulation.
        run_: Set to "True" to translate the jsons to an osm and idf file and then
            run the idf through EnergyPlus. This will ensure that all result
            files appear in their respective outputs from this component. This
            input can also be the integer "2", which will only translate the
            jsons to an osm and idf format without running the model through
            EnergyPlus.
    
    Returns:
        report: Check here to see a report of the EnergyPlus run.
        jsons: The file paths to the honeybee JSON files that describe the Model and
            SimulationParameter. These will be translated to an OpenStudio
            model using the honeybee energy_model_measure.
        osw: File path to the OpenStudio Workflow JSON on this machine. This workflow
            is executed using the OpenStudio command line interface (CLI) and
            it includes the honeybee energy_model_measure as well as any other
            connected measures_.
        osm: The file path to the OpenStudio Model (OSM) that has been generated
            on this computer.
        idf: The file path of the IDF file that has been generated on this computer.
        sql: The file path of the SQL result file that has been generated on this
            computer. This will be None unless run_ is set to True.
        zsz: Path to a .csv file containing detailed zone load information recorded
            over the course of the design days. This will be None unless run_ is
            set to True.
        rdd: The file path of the Result Data Dictionary (.rdd) file that is
            generated after running the file through EnergyPlus.  This file
            contains all possible outputs that can be requested from the EnergyPlus
            model.  Use the Read Result Dictionary component to see what outputs
            can be requested.
        html: The HTML file path of the Summary Reports. Note that this will be None
            unless the input _sim_par_ denotes that an HTML report is requested and
            run_ is set to True.
"""

ghenv.Component.Name = "HB Model to OSM"
ghenv.Component.NickName = 'ModelToOSM'
ghenv.Component.Message = '0.5.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import os
import json

try:
    from ladybug.futil import preparedir, nukedir
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
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def orphaned_warning(object_type):
    """Generate an error message for orphaned Faces, Apertures, or Doors."""
    return 'Input _model contains orphaned {}s. These are not permitted in ' \
        'Models for energy simulation.\nIf you have geometry that is not a ' \
        'part of a Room boundary that you want included in the energy simulation, ' \
        'it should be added as shades.'.format(object_type)


if all_required_inputs(ghenv.Component) and _write:
    # process the simulation parameters
    if _sim_par_ is None:
        _sim_par_ = SimulationParameter()
        _sim_par_.output.add_zone_energy_use()

    # assign design days from the EPW if there are not in the _sim_par_
    if len(_sim_par_.sizing_parameter.design_days) == 0:
        folder, epw_file_name = os.path.split(_epw_file)
        ddy_file = os.path.join(folder, epw_file_name.replace('.epw', '.ddy'))
        if os.path.isfile(ddy_file):
            _sim_par_.sizing_parameter.add_from_ddy_996_004(ddy_file)
        else:
            raise ValueError('No _ddy_file_ has been input and no .ddy file was '
                             'found next to the _epw_file.')

    # process the simulation folder name and the directory
    _folder_ = hb_config.folders.default_simulation_folder if _folder_ is None else _folder_
    directory = os.path.join(_folder_, _model.identifier, 'OpenStudio')

    # check the model to be sure there are no orphaned faces, apertures, or doors
    assert len(_model.orphaned_faces) == 0, orphaned_warning('Face')
    assert len(_model.orphaned_apertures) == 0, orphaned_warning('Aperture')
    assert len(_model.orphaned_doors) == 0, orphaned_warning('Door')

    # scale the model if the units are not meters
    if _model.units != 'Meters':
        _model = _model.duplicate()  # duplicate model to avoid mutating the input
        _model.convert_to_units('Meters')

    # delete any existing files in the directory and prepare it for simulation
    nukedir(directory, True)
    preparedir(directory)

    # write the model parameter JSONs
    model_dict = _model.to_dict(triangulate_sub_faces=True)
    model_json = os.path.join(directory, '{}.json'.format(_model.identifier))
    with open(model_json, 'w') as fp:
        json.dump(model_dict, fp)

    # write the simulation parameter JSONs
    sim_par_dict = _sim_par_.to_dict()
    sim_par_json = os.path.join(directory, 'simulation_parameter.json')
    with open(sim_par_json, 'w') as fp:
        json.dump(sim_par_dict, fp)

    # process any measures input to the component
    measures = None if len(measures_) == 0 or measures_[0] is None else measures_
    no_report_meas = True if measures is None else \
        all(meas.type != 'ReportingMeasure' for meas in measures)

    # collect the two jsons for output and write out the osw file
    jsons = [model_json, sim_par_json]
    osw = to_openstudio_osw(directory, model_json, sim_par_json,
                            additional_measures=measures, epw_file=_epw_file)

    # run the measure to translate the model JSON to an openstudio measure
    if run_ > 0 and not no_report_meas:  # everything must run with OS CLI
        osm, idf = run_osw(osw, measures_only=False)
        sql, zsz, rdd, html, err = output_energyplus_files(os.path.dirname(idf))
    elif run_ > 0:  # no reporting measure; simulate separately from measure application
        osm, idf = run_osw(osw)
        # process the additional strings
        if add_str_ != [] and add_str_[0] is not None and idf is not None:
            add_str = '/n'.join(add_str_)
            with open(idf, "a") as idf_file:
                idf_file.write(add_str)
        if idf is None:  # measures failed to run correctly
            raise Exception('Applying measures failed. Check run.log in:'
                            '\n{}'.format(os.path.join(directory, 'run')))
        if run_ == 1:  # run the resulting idf throught EnergyPlus
            sql, zsz, rdd, html, err = run_idf(idf, _epw_file)

    # parse the error log and report any warnings
    if run_ == 1 and err is not None:
        err_obj = Err(err)
        print(err_obj.file_contents)
        for warn in err_obj.severe_errors:
            give_warning(ghenv.Component, warn)
        for error in err_obj.fatal_errors:
            raise Exception(error)
