# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Parse all of the common Room-level comfort-related results from an SQL result
file that has been generated from an energy simulation.

-
    Args:
        _sql: The file path of the SQL result file that has been generated from
            an energy simulation.
    
    Returns:
        oper_temp: DataCollections for the mean operative temperature of each room (C).
        air_temp: DataCollections for the mean air temperature of each room (C).
        rad_temp: DataCollections for the mean radiant temperature of each room (C).
        rel_humidity: DataCollections for the relative humidity of each room (%).
"""

ghenv.Component.Name = 'HB Read Room Comfort Result'
ghenv.Component.NickName = 'RoomComfortResult'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '6 :: Result'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import os
import subprocess
import json

try:
    from ladybug.datacollection import HourlyContinuousCollection, \
        MonthlyCollection, DailyCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.result.sql import SQLiteResult
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def serialize_data(data_dicts):
    """Reserialize a list of collection dictionaries."""
    if len(data_dicts) == 0:
        return []
    elif data_dicts[0]['type'] == 'HourlyContinuousCollection':
        return [HourlyContinuousCollection.from_dict(data) for data in data_dicts]
    elif data_dicts[0]['type'] == 'MonthlyCollection':
        return [MonthlyCollection.from_dict(data) for data in data_dicts]
    elif data_dicts[0]['type'] == 'DailyCollection':
        return [DailyCollection.from_dict(data) for data in data_dicts]


# List of all the output strings that will be requested
oper_temp_output = 'Zone Operative Temperature'
air_temp_output = 'Zone Mean Air Temperature'
rad_temp_output = 'Zone Mean Radiant Temperature'
rel_humidity_output = 'Zone Air Relative Humidity'
all_output = [oper_temp_output, air_temp_output, rad_temp_output, rel_humidity_output]


if all_required_inputs(ghenv.Component):
    if os.name == 'nt':  # we are on windows; use IronPython like usual
        sql_obj = SQLiteResult(_sql)  # create the SQL result parsing object
        # get all of the results
        oper_temp = sql_obj.data_collections_by_output_name(oper_temp_output)
        air_temp = sql_obj.data_collections_by_output_name(air_temp_output)
        rad_temp = sql_obj.data_collections_by_output_name(rad_temp_output)
        rel_humidity = sql_obj.data_collections_by_output_name(rel_humidity_output)

    else:  # we are on Mac; sqlite3 module doesn't work in Mac IronPython
        # Execute the honybee CLI to obtain the results via CPython
        cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'result',
                'data-by-outputs', _sql] + all_output
        process = subprocess.Popen(cmds, stdout=subprocess.PIPE)
        stdout = process.communicate()
        data_coll_dicts = json.loads(stdout[0])
        # get all of the results
        oper_temp = serialize_data(data_coll_dicts[0])
        air_temp = serialize_data(data_coll_dicts[1])
        rad_temp = serialize_data(data_coll_dicts[2])
        rel_humidity = serialize_data(data_coll_dicts[3])
