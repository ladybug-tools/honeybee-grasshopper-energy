# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

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
ghenv.Component.Message = '1.2.1'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '6 :: Result'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import os
import subprocess
import json

from collections import OrderedDict

try:
    from ladybug.sql import SQLiteResult
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
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


# Use the SQLiteResult class to parse the result files directly on Windows.
def get_results_windows(sql_files):
    # set initial values that will be computed based on results
    total_floor_area, total_energy = 0, 0
    all_uses = \
        ('heating', 'cooling', 'interior_lighting', 'exterior_lighting',
         'interior_equipment', 'exterior_equipment', 'fans', 'pumps',
         'heat_rejection', 'humidification', 'heat_recovery', 'water_systems',
          'refrigeration', 'generators')
    end_uses = OrderedDict()
    for use in all_uses:
        end_uses[use] = 0

    # loop through the sql files in the directory and add the energy use
    for result_file in sql_files:
        # parse the SQL file
        sql_obj = SQLiteResult(result_file)
        # get the total floor area of the model
        area_dict = sql_obj.tabular_data_by_name('Building Area')
        areas = tuple(area_dict.values())
        total_floor_area += areas[0][0]
        # get the energy use
        eui_dict = sql_obj.tabular_data_by_name('End Uses')
        euis = tuple(eui_dict.values())
        total_energy += sum([val for val in euis[-2][:12]])
        end_uses['heating'] += sum([val for val in euis[0][:12]])
        end_uses['cooling'] += sum([val for val in euis[1][:12]])
        end_uses['interior_lighting'] += sum([val for val in euis[2][:12]])
        end_uses['exterior_lighting'] += sum([val for val in euis[3][:12]])
        end_uses['interior_equipment'] += sum([val for val in euis[4][:12]])
        end_uses['exterior_equipment'] += sum([val for val in euis[5][:12]])
        end_uses['fans'] += sum([val for val in euis[6][:12]])
        end_uses['pumps'] += sum([val for val in euis[7][:12]])
        end_uses['heat_rejection'] += sum([val for val in euis[8][:12]])
        end_uses['humidification'] += sum([val for val in euis[9][:12]])
        end_uses['heat_recovery'] += sum([val for val in euis[10][:12]])
        end_uses['water_systems'] += sum([val for val in euis[11][:12]])
        end_uses['refrigeration'] += sum([val for val in euis[12][:12]])
        end_uses['generators'] += sum([val for val in euis[13][:12]])
    
    # assemble all of the results into a final dictionary
    eui = round(total_energy / total_floor_area, 3)
    gross_floor = round(total_floor_area, 3)
    end_use_pairs = OrderedDict([(key, round(val / total_floor_area, 3))
                     for key, val in end_uses.items() if val != 0])
    return eui, gross_floor, end_use_pairs
    

# The SQLite3 module doesn't work in IronPython on Mac, so we must make a call
# to the Honeybee CLI (which runs on CPython) to get the results.
def get_results_mac(sql_files):
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
