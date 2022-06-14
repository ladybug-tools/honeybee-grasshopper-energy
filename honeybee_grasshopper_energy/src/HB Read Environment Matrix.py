# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Read the detailed environmental conditions of a thermal mapping analysis from
the env_conds output by a thermal mapping component.
_
Environemntal conditions include raw inputs to the thermal comfort model, such as
air temperature, MRT, longwave MRT, and shortwave MRT delta.

-
    Args:
        _env_conds: Path to a folder containing the detailed environmental conditions
            output by a thermal mapping component.
        _metric_: Text or an integer for the specific metric to be loaded from the
            environmental conditions. (Default: MRT). Choose from the following.
                * 0 - MRT
                * 1 - Air Temperature
                * 2 - Longwave MRT
                * 3 - Shortwave MRT Delta
                * 4 - Relative Humidity
        _load: Set to True to load the data into Grasshopper.

    Returns:
        comf_mtx: A Matrix object that can be connected to the "HB Visualize Thermal
            Map" component in order to spatially visualize results. This Matrix
            object can also be connected to the "LB Deconstruct Matrix"
            component to obtain detailed point-by-point and hour-by-hour
            values.
            _
            When deconstructed, each sub-list of the matrix (aka. branch of the
            Data Tree) represents one of the sensor grids used for analysis.
            The length of each sub-list matches the number of points in the
            grid. Each value in the sub-list is an hourly data collection
            containing hour-by-hour results for each point.
"""

ghenv.Component.Name = 'HB Read Environment Matrix'
ghenv.Component.NickName = 'EnvMtx'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '7 :: Thermal Map'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

import subprocess
import os
import shutil
import json

try:
    from ladybug.datatype.temperature import AirTemperature, \
        MeanRadiantTemperature, RadiantTemperature
    from ladybug.datatype.temperaturedelta import RadiantTemperatureDelta
    from ladybug.datatype.fraction import RelativeHumidity
    from ladybug.header import Header
    from ladybug.datacollection import HourlyContinuousCollection, \
        HourlyDiscontinuousCollection
    from ladybug.futil import csv_to_num_matrix
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, objectify_output
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

ENV_CONDS_MAP = {
    '0': 'mrt',
    'mrt': 'mrt',
    'mean radiant temperature': 'mrt',
    '1': 'air_temperature',
    'air temperature': 'air_temperature',
    '2': 'longwave_mrt',
    'longwave mrt': 'longwave_mrt',
    '3': 'shortwave_mrt',
    'shortwave mrt': 'shortwave_mrt',
    'shortwave mrt delta': 'shortwave_mrt',
    '4': 'rel_humidity',
    'relative humidity':  'rel_humidity'
}


def load_matrix(comf_result):
    """Load a matrix of data into an object that can be output in Grasshopper.

    Args:
        comf_result: Path to a folder with CSV data to be loaded into Grasshopper.
    """
    # parse the result_info.json into a data collection header
    with open(os.path.join(comf_result, 'results_info.json')) as json_file:
        data_header = Header.from_dict(json.load(json_file))
    a_per = data_header.analysis_period
    continuous = True if a_per.st_hour == 0 and a_per.end_hour == 23 else False
    if not continuous:
        dates = a_per.datetimes

    # parse the grids_info.json with the correct order of the grid files
    with open(os.path.join(comf_result, 'grids_info.json')) as json_file:
        grid_list = json.load(json_file)

    # loop through the grid CSV files, parse their results, and build data collections
    comf_matrix = []
    for grid in grid_list:
        grid_name = grid['full_id'] if 'full_id' in grid else 'id'
        metadata = {'grid': grid_name}
        grid_file = os.path.join(comf_result, '{}.csv'.format(grid_name))
        data_matrix = csv_to_num_matrix(grid_file)
        grid_data = []
        for i, row in enumerate(data_matrix):
            header = data_header.duplicate()
            header.metadata = metadata.copy()
            header.metadata['sensor_index'] = i
            data = HourlyContinuousCollection(header, row) if continuous else \
                HourlyDiscontinuousCollection(header, row, dates)
            grid_data.append(data)
        comf_matrix.append(grid_data)

    # wrap the maptrix into an object so that it does not slow the Grasshopper UI
    comf_mtx = objectify_output(
        '{} Matrix'.format(data_header.data_type.name), comf_matrix)
    return comf_mtx


def create_result_header(env_conds, sub_path):
    """Create a DataCollection Header for a given metric."""
    with open(os.path.join(env_conds, 'results_info.json')) as json_file:
        base_head = Header.from_dict(json.load(json_file))
    if sub_path == 'mrt':
        return Header(MeanRadiantTemperature(), 'C', base_head.analysis_period)
    elif sub_path == 'air_temperature':
        return Header(AirTemperature(), 'C', base_head.analysis_period)
    elif sub_path == 'longwave_mrt':
        return Header(RadiantTemperature(), 'C', base_head.analysis_period)
    elif sub_path == 'shortwave_mrt':
        return Header(RadiantTemperatureDelta(), 'dC', base_head.analysis_period)
    elif sub_path == 'rel_humidity':
        return Header(RelativeHumidity(), '%', base_head.analysis_period)


def sum_matrices(mtxs_1, mtxs_2, dest_dir):
    """Sum together matrices of two folders."""
    if not os.path.isdir(dest_dir):
        os.makedirs(dest_dir)
    for mtx_file in os.listdir(mtxs_1):
        if mtx_file.endswith('.csv'):
            mtx_file1 = os.path.join(mtxs_1, mtx_file)
            mtx_file2 = os.path.join(mtxs_2, mtx_file)
            matrix_1 = csv_to_num_matrix(mtx_file1)
            matrix_2 = csv_to_num_matrix(mtx_file2)
            data = [[d1 + d2 for d1, d2 in zip(r1, r2)]
                    for r1, r2 in zip(matrix_1, matrix_2)]
            csv_path = os.path.join(dest_dir, mtx_file)
            with open(csv_path, 'w') as csv_file:
                for dat in data:
                    str_data = (str(v) for v in dat)
                    csv_file.write(','.join(str_data) + '\n')
        elif mtx_file == 'grids_info.json':
            shutil.copyfile(
                os.path.join(mtxs_1, mtx_file),
                os.path.join(dest_dir, mtx_file)
            )


if all_required_inputs(ghenv.Component) and _load:
    # get the folders and that correspond with the requested metric
    _metric_ = _metric_ if _metric_ is not None else 'mrt'
    try:
        sub_path = ENV_CONDS_MAP[_metric_.lower()]
    except KeyError:
        raise ValueError(
            'Input metric "{}" is not recognized. Choose from: {}'.format(
                _metric_, '\n'.join(ENV_CONDS_MAP.keys()))
        )
    source_folder = os.path.join(_env_conds, sub_path)
    dest_folder = os.path.join(_env_conds, 'final', sub_path)

    # if the results have already been processed, then load them up
    if os.path.isdir(dest_folder):
        comf_mtx = load_matrix(dest_folder)
    else:  # otherwise, process them into a load-able format
        # make sure the requested metric is valid for the study
        if sub_path == 'mrt':
            source_folders = [os.path.join(_env_conds, 'longwave_mrt'),
                              os.path.join(_env_conds, 'shortwave_mrt')]
            dest_folders = [os.path.join(_env_conds, 'final', 'longwave_mrt'),
                            os.path.join(_env_conds, 'final', 'shortwave_mrt')]
        else:
            assert os.path.isdir(source_folder), \
                'Metric "{}" does not exist for this comfort study.'.format(sub_path)
            source_folders, dest_folders = [source_folder], [dest_folder]
        # restructure the results to align with the sensor grids
        dist_info = os.path.join(_env_conds, '_redist_info.json')
        for src_f, dst_f in zip(source_folders, dest_folders):
            if not os.path.isdir(dst_f):
                os.makedirs(dst_f)
                cmds = [folders.python_exe_path, '-m', 'honeybee_radiance', 'grid',
                        'merge-folder', src_f, dst_f, 'csv',
                        '--dist-info', dist_info]
                shell = True if os.name == 'nt' else False
                process = subprocess.Popen(cmds, stdout=subprocess.PIPE, shell=shell)
                stdout = process.communicate()
                grid_info_src = os.path.join(_env_conds, 'grids_info.json')
                grid_info_dst = os.path.join(dst_f, 'grids_info.json')
                shutil.copyfile(grid_info_src, grid_info_dst)
            data_header = create_result_header(_env_conds, os.path.split(dst_f)[-1])
            result_info_path = os.path.join(dst_f, 'results_info.json')
            with open(result_info_path, 'w') as fp:
                json.dump(data_header.to_dict(), fp, indent=4)
        # if MRT was requested, sum together the longwave and shortwave
        if sub_path == 'mrt':
            sum_matrices(dest_folders[0], dest_folders[1], dest_folder)
            data_header = create_result_header(_env_conds, sub_path)
            result_info_path = os.path.join(dest_folder, 'results_info.json')
            with open(result_info_path, 'w') as fp:
                json.dump(data_header.to_dict(), fp, indent=4)
        # load the resulting matrix into Grasshopper
        comf_mtx = load_matrix(dest_folder)
