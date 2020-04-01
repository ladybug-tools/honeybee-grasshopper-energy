# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
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
        opaque_energy_flow: DataCollections for the heat loss (negative) or
            heat gain (positive) through each building opaque surface (kWh).
        window_energy_flow: DataCollections for the heat loss (negative) or
            heat gain (positive) through each building glazing surface (kWh).
            Note that the value here includes both solar gains and conduction
            losses/gains.
"""

ghenv.Component.Name = 'HB Read Face Result'
ghenv.Component.NickName = 'FaceResult'
ghenv.Component.Message = '0.1.1'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '6 :: Result'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

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


if all_required_inputs(ghenv.Component):
    # create the SQL result parsing object
    sql_obj = SQLiteResult(_sql)
    
    # get all of the results
    face_indoor_temp = sql_obj.data_collections_by_output_name(
        'Surface Inside Face Temperature')
    face_outdoor_temp = sql_obj.data_collections_by_output_name(
        'Surface Outside Face Temperature')
    opaque_energy_flow = sql_obj.data_collections_by_output_name(
        'Surface Average Face Conduction Heat Transfer Energy')
    
    window_loss = sql_obj.data_collections_by_output_name(
        'Surface Window Heat Loss Energy')
    window_gain = sql_obj.data_collections_by_output_name(
        'Surface Window Heat Gain Energy')
    window_energy_flow = []
    if len(window_gain) == len(window_loss):
        window_energy_flow = subtract_loss_from_gain(window_gain, window_loss)
    
    face_energy_flow = opaque_energy_flow + window_energy_flow
