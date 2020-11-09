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
        face_indoor_temp: DataCollections for the indoor surface temperature of
            each surface (C).
        face_outdoor_temp: DataCollections for the outdoor surface temperature
            of each surface (C).
        face_energy_flow: DataCollections for the heat loss (negative) or heat
            gain (positive) through each building surfaces (kWh).
"""

ghenv.Component.Name = 'HB Read Face Result'
ghenv.Component.NickName = 'FaceResult'
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


def subtract_loss_from_gain(gain_load, loss_load):
    """Create a single DataCollection from gains and losses."""
    total_loads = []
    for gain, loss in zip(gain_load, loss_load):
        total_load = gain - loss
        total_load.header.metadata['type'] = \
            total_load.header.metadata['type'].replace('Gain ', '')
        total_loads.append(total_load)
    return total_loads


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
face_indoor_temp_output = 'Surface Inside Face Temperature'
face_outdoor_temp_output = 'Surface Outside Face Temperature'
opaque_energy_flow_output = 'Surface Average Face Conduction Heat Transfer Energy'
window_loss_output = 'Surface Window Heat Loss Energy'
window_gain_output = 'Surface Window Heat Gain Energy'
all_output = [face_indoor_temp_output, face_outdoor_temp_output,
              opaque_energy_flow_output, window_loss_output, window_gain_output]


if all_required_inputs(ghenv.Component):
    if os.name == 'nt':  # we are on windows; use IronPython like usual
        sql_obj = SQLiteResult(_sql)  # create the SQL result parsing object
        # get all of the results
        face_indoor_temp = sql_obj.data_collections_by_output_name(face_indoor_temp_output)
        face_outdoor_temp = sql_obj.data_collections_by_output_name(face_outdoor_temp_output)
        opaque_energy_flow = sql_obj.data_collections_by_output_name(opaque_energy_flow_output)
        window_loss = sql_obj.data_collections_by_output_name(window_loss_output)
        window_gain = sql_obj.data_collections_by_output_name(window_gain_output)

    else:  # we are on Mac; sqlite3 module doesn't work in Mac IronPython
        # Execute the honybee CLI to obtain the results via CPython
        cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'result',
                'data-by-outputs', _sql] + all_output
        process = subprocess.Popen(cmds, stdout=subprocess.PIPE)
        stdout = process.communicate()
        data_coll_dicts = json.loads(stdout[0])
        # get all of the results
        face_indoor_temp = serialize_data(data_coll_dicts[0])
        face_outdoor_temp = serialize_data(data_coll_dicts[1])
        opaque_energy_flow = serialize_data(data_coll_dicts[2])
        window_loss = serialize_data(data_coll_dicts[3])
        window_gain = serialize_data(data_coll_dicts[4])

    # do arithmetic with any of the gain/loss data collections
    window_energy_flow = []
    if len(window_gain) == len(window_loss):
        window_energy_flow = subtract_loss_from_gain(window_gain, window_loss)
    face_energy_flow = opaque_energy_flow + window_energy_flow
