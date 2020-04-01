# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
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
ghenv.Component.NickName = 'RoomCustomResult'
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
    results = sql_obj.data_collections_by_output_name(_output_names)
