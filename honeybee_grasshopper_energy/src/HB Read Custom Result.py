# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Parse any time series data from an energy simulation SQL result file.

-
    Args:
        _sql: The file path of the SQL result file that has been generated from
            an energy simulation.
        _output_names: A list of EnergyPlus output names as strings (eg.
            'Surface Window System Solar Transmittance'. These data corresponding
            to these outputs will be returned from this component.
    
    Returns:
        results: DataCollections for the output_names.
"""

ghenv.Component.Name = 'HB Read Custom Result'
ghenv.Component.NickName = 'CustomResult'
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


if all_required_inputs(ghenv.Component):
    if os.name == 'nt':  # we are on windows; use IronPython like usual
        sql_obj = SQLiteResult(_sql)  # create the SQL result parsing object
        results = sql_obj.data_collections_by_output_name(_output_names)

    else:  # we are on Mac; sqlite3 module doesn't work in Mac IronPython
        # Execute the honybee CLI to obtain the results via CPython
        cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'result',
                'data-by-outputs', _sql, _output_names]
        process = subprocess.Popen(cmds, stdout=subprocess.PIPE)
        stdout = process.communicate()
        data_dicts = json.loads(stdout[0])
        results = serialize_data(data_dicts[0])
