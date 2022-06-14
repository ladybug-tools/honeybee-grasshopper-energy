# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Read the detailed results of a thermal mapping analysis from a folder of CSV
files output by a thermal mapping component.
_
Detailed results include temperature amd thermal condition results. It also
includes metrics that give a sense of how hot or cold condition are like
pmv, utci category, or adaptive comfort degrees from neutral temperature.

-
    Args:
        _comf_result: Path to a folder containing CSV files output by a thermal
            mapping component.
        _load: Set to True to load the data from the CSV files into Grasshopper.

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

ghenv.Component.Name = 'HB Read Thermal Matrix'
ghenv.Component.NickName = 'ThermalMtx'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '7 :: Thermal Map'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import os
import json

try:
    from ladybug.header import Header
    from ladybug.datacollection import HourlyContinuousCollection, \
        HourlyDiscontinuousCollection
    from ladybug.futil import csv_to_num_matrix
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, objectify_output
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _load:
    # parse the result_info.json into a data collection header
    with open(os.path.join(_comf_result, 'results_info.json')) as json_file:
        data_header = Header.from_dict(json.load(json_file))
    a_per = data_header.analysis_period
    continuous = True if a_per.st_hour == 0 and a_per.end_hour == 23 else False
    if not continuous:
        dates = a_per.datetimes

    # parse the grids_info.json with the correct order of the grid files
    with open(os.path.join(_comf_result, 'grids_info.json')) as json_file:
        grid_list = json.load(json_file)

    # loop through the grid CSV files, parse their results, and build data collections
    comf_matrix = []
    for grid in grid_list:
        grid_name = grid['full_id'] if 'full_id' in grid else 'id'
        metadata = {'grid': grid_name}
        grid_file = os.path.join(_comf_result, '{}.csv'.format(grid_name))
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
