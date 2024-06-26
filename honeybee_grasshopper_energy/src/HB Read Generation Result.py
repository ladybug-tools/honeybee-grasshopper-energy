# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Parse electricity generation results from an energy simulation SQL result file.

-
    Args:
        _sql: The file path of the SQL result file that has been generated from
            an energy simulation.

    Returns:
        site_totals: Two numbers indicating the following energy values in kWh.
            _
            * Total on-site produced electricity (postive number)
            * Total on-site electricity consumption (negative number)
        utility_totals: Three numbers indicating the following energy values in kWh.
            _
            * Total on-site produced electricity consumed on-site (positive number)
            * Total on-site produced surplus electricity sold to the utility (positive number)
            * Total electricity purchased from the utility (negative number)
        production: A data collection of all on-site produced electricity (kWh). This
            represents the alternating current (AC) electricity coming out of
            the inverter that processes all on-site power production.
        consumption: A data collection of all on-site consumed electricity (kWh). This
            represents the electrcicity consumed by all heating, cooling, lighting
            equipment, fans, pumps, process loads, and water heaters. All of
            this consumed electricity is assumed to be alternating current (AC).
        dc_power: A list of data collections for the direct current (DC) electricity
            produced by each on-site electricity generator (kWh). Each
            photovoltaic object will have a separate data collection.
"""

ghenv.Component.Name = 'HB Read Generation Result'
ghenv.Component.NickName = 'GenerationResult'
ghenv.Component.Message = '1.8.1'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '6 :: Result'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

import os
import subprocess
import json
from collections import OrderedDict

try:
    from ladybug.datacollection import HourlyContinuousCollection, \
        MonthlyCollection, DailyCollection
    from ladybug.sql import SQLiteResult
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.result.generation import generation_summary_from_sql, \
        generation_data_from_sql
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


# The SQLite3 module doesn't work in IronPython on Mac, so we must make a call
# to the Honeybee CLI (which runs on CPython) to get the results.
def get_results_mac(sql_files):
    from collections import OrderedDict
    cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'result',
            'generation-summary']
    cmds.extend(sql_files)
    process = subprocess.Popen(cmds, stdout=subprocess.PIPE, env=custom_env)
    stdout = process.communicate()
    results = json.loads(stdout[0])
    return results


def serialize_data(data_dicts):
    """Reserialize a list of collection dictionaries."""
    if len(data_dicts) == 0 or data_dicts[0] is None:
        return [None] * len(data_dicts)
    elif data_dicts[0]['type'] == 'HourlyContinuous':
        return [HourlyContinuousCollection.from_dict(data) for data in data_dicts]
    elif data_dicts[0]['type'] == 'Monthly':
        return [MonthlyCollection.from_dict(data) for data in data_dicts]
    elif data_dicts[0]['type'] == 'Daily':
        return [DailyCollection.from_dict(data) for data in data_dicts]

DC_OUTPUT = 'Generator Produced DC Electricity Energy'
custom_env = os.environ.copy()
custom_env['PYTHONHOME'] = ''


if all_required_inputs(ghenv.Component):
    dc_power = []
    if os.name == 'nt':  # we are on windows; use IronPython like usual
        result_dict = generation_summary_from_sql(_sql)
        production, consumption = generation_data_from_sql(_sql)
        for sql_f in _sql:
            sql_obj = SQLiteResult(sql_f)
            dc_data = sql_obj.data_collections_by_output_name(DC_OUTPUT)
            dc_power.extend(dc_data)

    else:  # we are on Mac; sqlite3 module doesn't work in Mac IronPython
        # Execute the honybee CLI to obtain the results via CPython
        result_dict = get_results_mac(_sql)
        cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'result',
                'generation-data']
        cmds.extend(_sql)
        process = subprocess.Popen(cmds, stdout=subprocess.PIPE, env=custom_env)
        stdout = process.communicate()
        data_dicts = json.loads(stdout[0])
        production, consumption = serialize_data(data_dicts)

        for sql_f in _sql:
            cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'result',
                    'data-by-outputs', sql_f, DC_OUTPUT]
            process = subprocess.Popen(cmds, stdout=subprocess.PIPE, env=custom_env)
            stdout = process.communicate()
            data_dicts = json.loads(stdout[0])
            dc_data = serialize_data(data_dicts[0])
            dc_power.extend(dc_data)

    # output the separate summary results
    site_totals = (
        result_dict['total_production'],
        result_dict['total_consumption']
    )
    utility_totals = (
        result_dict['production_used_on_site'],
        result_dict['production_surplus_sold'],
        result_dict['consumption_purchased']
    )

    # group the generator results by identifier
    if len(dc_power) != 0 and not isinstance(dc_power[0], (float, int)):
        dc_dict = OrderedDict()
        for g_data in dc_power:
            gen_id = g_data.header.metadata['System'].split('..')[0]
            g_data.header.metadata['System'] = gen_id
            try:
                dc_dict[gen_id] += g_data
            except KeyError:
                dc_dict[gen_id] = g_data
        dc_power = [dcp for dcp in dc_dict.values()]
