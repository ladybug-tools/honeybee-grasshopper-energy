# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Get information about end use intensity from an EnergyPlus SQL file.
-

    Args:
        _sql: The file path of the SQL result file that has been generated from
            an energy simulation. This can also be a list of EnergyPlus files
            in which case, EUI will be computed across all files.
        ip_: Boolean to note whether the EUI should be in SI (kWh/m2) or IP
            (kBtu/ft2) units. (Default: False).

    Returns:
        eui: The total end use intensity result from the simulation. Specifically,
            this is the sum of all electricity, fuel, district heating/cooling,
            etc. divided by the gross floor area (including both conditioned
            and unconditioned spaces). The value will be in kWh/m2 if ip_
            is False or None and kBtu/ft2 if True.
        eui_end_use: The end use intensity result from the simulation, broken down by each
            end use. These values coorespond to the end_uses output below. Values
            will be in kWh/m2 if ip_ is False or None and kBtu/ft2 if True.
        end_uses: A list of text for each of the end uses in the simulation (Heating,
            Cooling, etc.). Thes outputs coorespond to the eui_end_use
            output above.
        gross_floor: The total gross floor area of the energy model. This can be used
            to compute the total energy use from the intensity values above or
            it can be used to help with other result post-processing. The value
            will be in m2 if ip_ is False or None and ft2 if True.
"""

ghenv.Component.Name = 'HB End Use Intensity'
ghenv.Component.NickName = 'EUI'
ghenv.Component.Message = '1.6.1'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '6 :: Result'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import os
import subprocess
import json

try:
    from ladybug.datatype.area import Area
    from ladybug.datatype.energyintensity import EnergyIntensity
    from ladybug.datatype.energy import Energy
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.result.eui import eui_from_sql
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


# Use the SQLiteResult class to parse the result files directly on Windows.
def get_results_windows(sql_files):
    results = eui_from_sql(sql_files)
    return results['eui'], results['total_floor_area'], results['end_uses']


# The SQLite3 module doesn't work in IronPython on Mac, so we must make a call
# to the Honeybee CLI (which runs on CPython) to get the results.
def get_results_mac(sql_files):
    from collections import OrderedDict
    cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'result',
            'energy-use-intensity']
    cmds.extend(sql_files)
    process = subprocess.Popen(cmds, stdout=subprocess.PIPE)
    stdout = process.communicate()
    results = json.loads(stdout[0], object_pairs_hook=OrderedDict)
    return results['eui'], results['total_floor_area'], results['end_uses']


if all_required_inputs(ghenv.Component):
    # ensure that _sql is a list rather than a single string
    if isinstance(_sql, basestring):
        _sql = [_sql]

    # get the results
    get_results = get_results_windows if os.name == 'nt' else get_results_mac
    eui, gross_floor, end_use_pairs = get_results(_sql)

    # create separate lists for end use values and labels
    eui_end_use = end_use_pairs.values()
    end_uses = [use.replace('_', ' ').title() for use in end_use_pairs.keys()]

    # convert data to IP if requested
    if ip_:
        eui_typ, a_typ, e_typ = EnergyIntensity(), Area(), Energy()
        eui = round(eui_typ.to_ip([eui], 'kWh/m2')[0][0], 3)
        gross_floor = round(a_typ.to_ip([gross_floor], 'm2')[0][0], 3)
        eui_end_use = [round(eui_typ.to_ip([val], 'kWh/m2')[0][0], 3)
                       for val in eui_end_use]
