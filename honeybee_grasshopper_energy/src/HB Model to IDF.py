# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Write a honeybee Model to an IDF file and then run it through EnergyPlus.

-
    Args:
        model: A honeybee model object possessing all geometry and corresponding
            energy simulation properties.
        _epw_file: Path to an .epw file on your system as a text string.
        _sim_par_: A honeybee Energy SimulationParameter object that describes all
            of the setting for the simulation. If None, some default simulation
            parameters will automatically be used.
        add_str_: THIS OPTION IS JUST FOR ADVANCED USERS OF ENERGYPLUS.
            You can input additional text strings here that you would like
            written into the IDF.  The strings input here should be complete
            EnergyPlus objects that are correctly formatted. This input can be used to
            write objects into the IDF that are not currently supported by Honeybee.
        _folder_: An optional folder on your system, into which your IDF and result
            files will be written.  NOTE THAT DIRECTORIES INPUT HERE SHOULD NOT HAVE
            ANY SPACES OR UNDERSCORES IN THE FILE PATH.
        _write: Set to "True" to translate the model to an IDF file.
            The file path of the resulting file will appear in the idf output of
            this component.  Note that only setting this to "True" and not setting
            run_ to "True" will not automatically run the IDF through EnergyPlus.
        run_: Set to "True" to run your IDF through EnergyPlus once it is written.
            This will ensure that result files appear in their respective outputs.
    
    Returns:
        report: Check here to see a report of the EnergyPlus run.
        idf: The file path of the IDF file that has been generated on your machine.
        sql: The file path of the SQL result file that has been generated on your
            machine. This will be None unless run_ is set to True.
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

ghenv.Component.Name = "HB Model to IDF"
ghenv.Component.NickName = 'ModelToIDF'
ghenv.Component.Message = '0.5.4'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import os

try:
    from ladybug.futil import write_to_file_by_name, nukedir
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.simulation.parameter import SimulationParameter
    from honeybee_energy.run import run_idf
    from honeybee_energy.result.err import Err
    from honeybee_energy.writer import energyplus_idf_version
    from honeybee_energy.config import folders as energy_folders
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
    
    # process the additional strings
    add_str = '/n'.join(add_str_) if add_str_ is not None else ''
    
    # process the simulation folder name and the directory
    _folder_ = folders.default_simulation_folder if _folder_ is None else _folder_
    directory = os.path.join(_folder_, _model.identifier, 'EnergyPlus')
    sch_directory = os.path.join(directory, 'schedules')
    
    # check the model to be sure there are no orphaned faces, apertures, or doors
    assert len(_model.orphaned_faces) == 0, orphaned_warning('Face')
    assert len(_model.orphaned_apertures) == 0, orphaned_warning('Aperture')
    assert len(_model.orphaned_doors) == 0, orphaned_warning('Door')
    
    # create the strings for simulation paramters and model
    ver_str = energyplus_idf_version() if energy_folders.energyplus_version \
        is not None else energyplus_idf_version((9, 2, 0))
    sim_par_str = _sim_par_.to_idf()
    model_str = _model.to.idf(_model, schedule_directory=sch_directory,
                              solar_distribution=_sim_par_.shadow_calculation.solar_distribution)
    idf_str = '\n\n'.join([ver_str, sim_par_str, model_str, add_str])
    
    # delete any existing files in the directory
    nukedir(directory)
    
    # write the final string into an IDF.
    idf = os.path.join(directory, 'in.idf')
    write_to_file_by_name(directory, 'in.idf', idf_str, True)
    
    if run_:
        sql, zsz, rdd, html, err = run_idf(idf, _epw_file)
        if err is not None:
            err_obj = Err(err)
            print(err_obj.file_contents)
            for warn in err_obj.severe_errors:
                give_warning(ghenv.Component, warn)
            for error in err_obj.fatal_errors:
                raise Exception(error)
