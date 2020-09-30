# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Parse the peak load and HVAC component sizes from an SQL result file that has
been generated from an energy simulation.
-

    Args:
        _sql: The file path of the SQL result file that has been generated from
            an energy simulation.
        comp_type_: An optional name of a HVAC component type, which will filter
            the HVAC components that appear in the output comp_props and
            comp_values. Connecting nothing here will mean that all HVAC
            component sizes are imported and a full list of possible components
            will appear in the comp_types output.
        
    
    Returns:
        zone_names: A list of zone names (honeybee Room identifiers) that correspond
            to the zone_peak_load and zone_peak_heat below.
        zone_peak_cool: A list of numbers for the peak cooling load of each zone
            on the summer design day. These correspond to the zone_names above.
        zone_peak_heat: A list of numbers for the peak heating load of each zone
            on the winter design day. These correspond to the zone_names above.
        comp_types: A list of HVAC component types that are available in the results.
            This will be equal to the input comp_type_ if a value is connected.
        comp_properties: A list of text descriptions for HVAC component properties.
            These correspond to the comp_values below.
        comp_values: Values denoting the size of various zone HVAC components 
            (eg. zone terminal sizes, boiler/chiller sizes, lengths of chilled
            beams, etc.). These correspond to the comp_properties above.
"""

ghenv.Component.Name = 'HB Read HVAC Sizing'
ghenv.Component.NickName = 'ReadHVAC'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '6 :: Result'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import os
import subprocess
import json

try:
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.result.sql import SQLiteResult, ZoneSize, ComponentSize
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # create the lists to be filled
    zone_names = []
    zone_peak_cool = []
    zone_peak_heat = []
    comp_properties_mtx = []
    comp_values_mtx = []

    if os.name == 'nt':  # we are on windows; use IronPython like usual
        sql_obj = SQLiteResult(_sql)  # create the SQL result parsing object
        zone_cooling_sizes = sql_obj.zone_cooling_sizes
        zone_heating_sizes = sql_obj.zone_heating_sizes
        if comp_type_ is None:
            comp_types = sql_obj.component_types
            component_sizes = sql_obj.component_sizes
        else:
            comp_types = comp_type_
            component_sizes = sql_obj.component_sizes_by_type(comp_type_)

    else:  # we are on Mac; sqlite3 module doesn't work in Mac IronPython
        # Execute the honybee CLI to obtain the zone sizes via CPython
        cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'result',
                'zone-sizes', _sql]
        process = subprocess.Popen(cmds, stdout=subprocess.PIPE)
        stdout = process.communicate()
        zone_size_dicts = json.loads(stdout[0])
        zone_cooling_sizes = [ZoneSize.from_dict(zs) for zs in zone_size_dicts['cooling']]
        zone_heating_sizes = [ZoneSize.from_dict(zs) for zs in zone_size_dicts['heating']]
        # Execute the honybee CLI to obtain the component sizes via CPython
        cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'result',
                'component-sizes', _sql]
        if comp_type_ is not None:
            comp_types = comp_type_
            cmds.extend(['--component-type', comp_type_])
        process = subprocess.Popen(cmds, stdout=subprocess.PIPE)
        stdout = process.communicate()
        comp_size_dicts = json.loads(stdout[0])
        component_sizes = [ComponentSize.from_dict(cs) for cs in comp_size_dicts]
        if comp_type_ is None:  # get a set of all unique component types
            _comp_types = set()
            for comp in component_sizes:
                _comp_types.add(comp.component_type)
            comp_types = list(_comp_types)

    # get the peak zone heating and cooling from the ZoneSize objects
    for zone_size in zone_cooling_sizes:
        zone_names.append(zone_size.zone_name)
        zone_peak_cool.append(zone_size.calculated_design_load)
    for zone_size in zone_heating_sizes:
        zone_peak_heat.append(zone_size.calculated_design_load)

    # get the HVAC component sizes from the ComponentSize objects
    for comp_size in component_sizes:
        comp_properties_mtx.append(comp_size.descriptions)
        comp_values_mtx.append(comp_size.values)
    # convert HVAC components to data trees
    comp_properties = list_to_data_tree(comp_properties_mtx)
    comp_values = list_to_data_tree(comp_values_mtx)
