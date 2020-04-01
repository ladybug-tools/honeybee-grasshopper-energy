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
        oper_temp: DataCollections for the mean operative temperature of each room (C).
        air_temp: DataCollections for the mean air temperature of each room (C).
        rad_temp: DataCollections for the mean radiant temperature of each room (C).
        rel_humidity: DataCollections for the relative humidity of each room (%).
"""

ghenv.Component.Name = 'HB Read Room Comfort Result'
ghenv.Component.NickName = 'RoomComfortResult'
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


if all_required_inputs(ghenv.Component):
    # create the SQL result parsing object
    sql_obj = SQLiteResult(_sql)
    
    # get all of the results
    oper_temp = sql_obj.data_collections_by_output_name(
        'Zone Operative Temperature')
    air_temp = sql_obj.data_collections_by_output_name(
        'Zone Mean Air Temperature')
    rad_temp = sql_obj.data_collections_by_output_name(
        'Zone Mean Radiant Temperature')
    rel_humidity = sql_obj.data_collections_by_output_name(
        'Zone Air Relative Humidity')
