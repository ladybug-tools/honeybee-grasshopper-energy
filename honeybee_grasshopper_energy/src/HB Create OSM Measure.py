# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Run an OpenStudio Meausre that is intended to create an entire OSM file
(OpenStudio Model). Examples of such measures include the "Create DOE
Prototype Building" measure such as that wich can be downloaded here:
_
https://github.com/NREL/openstudio-model-articulation-gem/tree/develop/lib/
measures/create_DOE_prototype_building

-
    Args:
        _measure: A Measure from the "HB Load Measure" component that is intended to
            generate an OSM from input arguments. Measures can be downloaded
            from the NREL Building Components Library (BCL) at (https://bcl.nrel.gov/).
        add_str_: Optional additional text strings here to be written into the IDF.
            The input here should be complete EnergyPlus objects as a single
            string following the IDF format. This can be used to add addition
            EnergyPlus outputs in the resulting IDF among other features.
        _folder_: An optional folder on this computer, into which the IDF and OSM
            files will be written. If none, a sub-folder within the default
            simulation folder will be used.
        run_: Set to "True" to run the measure and generate the OSM.

    Returns:
        report: Reports, errors, warnings.
        osw: File path to the OpenStudio Workflow JSON on this machine. This workflow
            is executed using the OpenStudio command line interface (CLI) and
            it includes measures to create the OSM from the measure
        osm: The file path to the OpenStudio Model (OSM) that has been generated
            on this computer.
        idf: The file path of the EnergyPlus Input Data File (IDF) that has been
            generated on this computer.
"""

ghenv.Component.Name = 'HB Create OSM Measure'
ghenv.Component.NickName = 'OSMMeasure'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

import sys
import re
import os
import json

try:
    from ladybug.futil import preparedir, nukedir
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.measure import Measure
    from honeybee_energy.run import run_osw
    from honeybee_energy.result.osw import OSW
    from honeybee_energy.config import folders as energy_folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from lbt_recipes.version import check_openstudio_version
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    # check the presence of openstudio and check that the version is compatible
    check_openstudio_version()

    # process the simulation folder name and the directory
    _folder_ = folders.default_simulation_folder if _folder_ is None else _folder_
    clean_name = re.sub(r'[^.A-Za-z0-9_-]', '_', _measure.display_name)
    directory = os.path.join(_folder_, clean_name, 'openstudio')

    # delete any existing files in the directory and prepare it for simulation
    nukedir(directory, True)
    preparedir(directory)

    # create a dictionary representation of the .osw with steps to run
    # the model measure and the simulation parameter measure
    osw_dict = {'steps': []}
    # assign the measure_paths to the osw_dict
    if 'measure_paths' not in osw_dict:
        osw_dict['measure_paths'] = []
    if energy_folders.honeybee_openstudio_gem_path:  # include honeybee-openstudio measure path
        measure_dir = os.path.join(energy_folders.honeybee_openstudio_gem_path, 'measures')
        osw_dict['measure_paths'].append(measure_dir)

    # add the measure to the OSW
    measure_paths = set()  # set of all unique measure paths
    _measure.validate()  # ensure that all required arguments have values
    measure_paths.add(os.path.dirname(_measure.folder))
    osw_dict['steps'].append(_measure.to_osw_dict())  # add measure to workflow

    # load the inject IDF measure if strings_to_inject have bee specified
    str_inject = None if add_str_ == [] or add_str_[0] is None \
        else '\n'.join(add_str_)
    if str_inject is not None and str_inject != '':
        assert energy_folders.inject_idf_measure_path is not None, \
            'Additional IDF strings input but the inject_idf measure is not installed.'
        idf_measure = Measure(energy_folders.inject_idf_measure_path)
        inject_idf = os.path.join(directory, 'inject.idf')
        with open(inject_idf, "w") as idf_file:
            idf_file.write(str_inject)
        units_arg = idf_measure.arguments[0]
        units_arg.value = inject_idf
        measure_paths.add(os.path.dirname(idf_measure.folder))
        osw_dict['steps'].append(idf_measure.to_osw_dict())  # add measure to workflow

    # write the dictionary to a workflow.osw
    for m_path in measure_paths:
       osw_dict['measure_paths'].append(m_path)
    osw_json = os.path.join(directory, 'workflow.osw')
    if (sys.version_info < (3, 0)):  # we need to manually encode it as UTF-8
        with open(osw_json, 'w') as fp:
            workflow_str = json.dumps(osw_dict, indent=4, ensure_ascii=False)
            fp.write(workflow_str.encode('utf-8'))
    else:
        with open(osw_json, 'wb', encoding='utf-8') as fp:
            workflow_str = json.dump(osw_dict, fp, indent=4, ensure_ascii=False)
    osw = os.path.abspath(osw_json)
    osm, idf = run_osw(osw, silent=False)

    # if the measure fails, report it
    if idf is None:  # measures failed to run correctly; parse out.osw
        log_osw = OSW(os.path.join(directory, 'out.osw'))
        errors = []
        for error, tb in zip(log_osw.errors, log_osw.error_tracebacks):
            print(tb)
            errors.append(error)
        raise Exception('Failed to run OpenStudio CLI:\n{}'.format('\n'.join(errors)))
