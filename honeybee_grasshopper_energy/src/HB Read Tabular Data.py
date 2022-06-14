# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Get all the data within a table of a Summary Report using the table name.
_
All of the avaialable tables can be browsed by opening the .html output from the
simulation in a web browser.
-

    Args:
        _sql: The file path of the SQL result file that has been generated from
            an energy simulation.
        _table_name: Text string for the name of a table of a Summary Report.
            Examples include: General, Utility Use Per Conditioned Floor Area,
            and many more options that can be browsed in the .html file.

    Returns:
        values: A data tree represening the table matrix, with each branch (sub-list)
            of the tree representing a row of the table and each index of each
            branch corresponding to a value in a column. The order of outputs
            should reflect how the table appears in the HTML output. Note that
            any energy values in MJ or GJ in the .html output will automatically
            be converted to kWh on import.
        col_names: A list of text for the names of each of the columns in the table.
            These order of this list corresponds directly to the order of items
            each of the values sub-list
        row_names: A list of text for the names of each of the rows of the table.
            Each name in this list corresponds to a branch in the output values
            data tree.
"""

ghenv.Component.Name = 'HB Read Tabular Data'
ghenv.Component.NickName = 'ReadTable'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '6 :: Result'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

import os
import subprocess
import json

try:
    from ladybug.sql import SQLiteResult
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    if os.name == 'nt':  # we are on windows; use IronPython like usual
        sql_obj = SQLiteResult(_sql)  # create the SQL result parsing object
        results = sql_obj.tabular_data_by_name(_table_name)
        values = list_to_data_tree(list(results.values()))
        row_names = list(results.keys())
        col_names = sql_obj.tabular_column_names(_table_name)

    else:  # we are on Mac; sqlite3 module doesn't work in Mac IronPython
        # Execute the honybee CLI to obtain the results via CPython
        cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'result',
                'tabular-data', _sql, _table_name]
        process = subprocess.Popen(cmds, stdout=subprocess.PIPE)
        stdout = process.communicate()
        results = json.loads(stdout[0])
        values = list_to_data_tree(results)
        cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'result',
                'tabular-metadata', _sql, _table_name]
        process = subprocess.Popen(cmds, stdout=subprocess.PIPE)
        stdout = process.communicate()
        metadata_dict = json.loads(stdout[0])
        row_names = metadata_dict['row_names']
        col_names = metadata_dict['column_names']
