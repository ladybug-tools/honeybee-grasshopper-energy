# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
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
            HVAC vintages. (Default: 90.1-2013). Choose from the following.
                * DOE Ref Pre-1980
                * DOE Ref 1980-2004
                * 90.1-2004
                * 90.1-2007
                * 90.1-2010
                * 90.1-2013
        _name_: Text to set the name for the heating/cooling system and to be
            incorporated into unique system identifier. If the name is not
            provided, a random name will be assigned.

    Returns:
        rooms: The input Rooms with a heating/cooling system applied.
"""

ghenv.Component.Name = "HB HeatCool HVAC"
ghenv.Component.NickName = 'HeatCoolHVAC'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '4 :: HVAC'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

import uuid

try:  # import the honeybee extension
    from honeybee.altnumber import autosize
    from honeybee.typing import clean_and_id_ep_string
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.hvac.heatcool import EQUIPMENT_TYPES_DICT
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

# dictionary to get correct vintages
vintages = {
    'DOE Ref Pre-1980': 'DOE Ref Pre-1980',
    'DOE Ref 1980-2004': 'DOE Ref 1980-2004',
    '90.1-2004': '90.1-2004',
    '90.1-2007': '90.1-2007',
    '90.1-2010': '90.1-2010',
    '90.1-2013': '90.1-2013',
    'pre_1980': 'DOE Ref Pre-1980',
    '1980_2004': 'DOE Ref 1980-2004',
    '2004': '90.1-2004',
    '2007': '90.1-2007',
    '2010': '90.1-2010',
    '2013': '90.1-2013',
    None: '90.1-2013'
    }

if all_required_inputs(ghenv.Component):
    # extract any rooms from input Models and duplicate the rooms
    rooms = []
    for hb_obj in _rooms:
        if isinstance(hb_obj, Model):
            rooms.extend([room.duplicate() for room in hb_obj.rooms])
        else:
            rooms.append(hb_obj.duplicate())

    # create the instance of the HVAC system to be applied to the rooms
    try:  # get the class for the HVAC system
        hvac_class = EQUIPMENT_TYPES_DICT[_system_type]
    except KeyError:
        raise ValueError('System Type "{}" is not recognized as an all-air HVAC '
                         'system.'.format(_system_type))
    vintage = vintages[_vintage_]  # get the vintage of the HVAC
    # get an identifier for the HVAC system
    name = clean_and_id_ep_string(_name_) if _name_ is not None else str(uuid.uuid4())[:8]
    hvac = hvac_class(name, vintage, _system_type)
    if _name_ is not None:
        hvac.display_name = _name_

    # apply the HVAC system to the rooms
    for room in rooms:
        if room.properties.energy.is_conditioned:
            room.properties.energy.hvac = hvac
