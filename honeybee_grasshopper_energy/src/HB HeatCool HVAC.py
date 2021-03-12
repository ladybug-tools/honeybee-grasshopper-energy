# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Apply a template system that only supplies heating and/or cooling (no ventilation)
to Honeybee Rooms.
_
These systems are only designed to satisfy heating + cooling demand and they
cannot meet any minimum ventilation requirements.
_
As such, these systems tend to be used in residential or storage settings where
meeting minimum ventilation requirements may not be required or the density
of occupancy is so low that infiltration is enough to meet fresh air demand.
-

    Args:
        _rooms: Honeybee Rooms to which the input template system will be assigned.
            This can also be a Honeybee Model for which all conditioned Rooms
            will be assigned the HVAC system.
        _system_type: Text for the specific type of heating/cooling system and equipment.
            The "HB HeatCool HVAC Templates" component has a full list of the
            supported Heating/Cooling system templates.
        _vintage_: Text for the vintage of the template system. This will be used
            to set efficiencies for various pieces of equipment within the system.
            The "HB Building Vintages" component has a full list of supported
            HVAC vintages. (Default: ASHRAE_2013).
        _name_: Text to set the name for the heating/cooling system and to be
            incorporated into unique system identifier. If the name is not
            provided, a random name will be assigned.

    Returns:
        rooms: The input Rooms with a heating/cooling system applied.
"""

ghenv.Component.Name = "HB HeatCool HVAC"
ghenv.Component.NickName = 'HeatCoolHVAC'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '4 :: HVAC'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

import os
import json
import uuid

try:  # import the honeybee extension
    from honeybee.altnumber import autosize
    from honeybee.typing import clean_and_id_ep_string
    from honeybee.model import Model
    from honeybee.room import Room
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.config import folders
    from honeybee_energy.hvac.heatcool import EQUIPMENT_TYPES_DICT
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

# dictionary to get correct vintages
vintages = {
    'DOE_Ref_Pre_1980': 'DOE_Ref_Pre_1980',
    'DOE_Ref_1980_2004': 'DOE_Ref_1980_2004',
    'ASHRAE_2004': 'ASHRAE_2004',
    'ASHRAE_2007': 'ASHRAE_2007',
    'ASHRAE_2010': 'ASHRAE_2010',
    'ASHRAE_2013': 'ASHRAE_2013',
    'DOE Ref Pre-1980': 'DOE_Ref_Pre_1980',
    'DOE Ref 1980-2004': 'DOE_Ref_1980_2004',
    '90.1-2004': 'ASHRAE_2004',
    '90.1-2007': 'ASHRAE_2007',
    '90.1-2010': 'ASHRAE_2010',
    '90.1-2013': 'ASHRAE_2013',
    'pre_1980': 'DOE_Ref_Pre_1980',
    '1980_2004': 'DOE_Ref_1980_2004',
    '2004': 'ASHRAE_2004',
    '2007': 'ASHRAE_2007',
    '2010': 'ASHRAE_2010',
    '2013': 'ASHRAE_2013',
    None: 'ASHRAE_2013'
    }

# dictionary of HVAC template names
ext_folder = folders.standards_extension_folders[0]
hvac_reg = os.path.join(ext_folder, 'hvac_registry.json')
with open(hvac_reg, 'r') as f:
    hvac_dict = json.load(f)


if all_required_inputs(ghenv.Component):
    # extract any rooms from input Models and duplicate the rooms
    rooms = []
    for hb_obj in _rooms:
        if isinstance(hb_obj, Model):
            rooms.extend([room.duplicate() for room in hb_obj.rooms])
        elif isinstance(hb_obj, Room):
            rooms.append(hb_obj.duplicate())
        else:
            raise ValueError(
                'Expected Honeybee Room or Model. Got {}.'.format(type(hb_obj)))

    # create the instance of the HVAC system to be applied to the rooms
    try:  # get the class for the HVAC system
        try:
            _sys_name = hvac_dict[_system_type]
        except KeyError:
            _sys_name = _system_type
        hvac_class = EQUIPMENT_TYPES_DICT[_sys_name]
    except KeyError:
        raise ValueError('System Type "{}" is not recognized as a HeatCool HVAC '
                         'system.'.format(_system_type))
    vintage = vintages[_vintage_]  # get the vintage of the HVAC
    # get an identifier for the HVAC system
    name = clean_and_id_ep_string(_name_) if _name_ is not None else str(uuid.uuid4())[:8]
    hvac = hvac_class(name, vintage, _sys_name)
    if _name_ is not None:
        hvac.display_name = _name_

    # apply the HVAC system to the rooms
    for room in rooms:
        if room.properties.energy.is_conditioned:
            room.properties.energy.hvac = hvac
