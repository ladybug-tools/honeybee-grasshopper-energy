# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Apply a Dedicated Outdoor Air System (DOAS) template HVAC to Honeybee Rooms.
_
DOAS systems separate minimum ventilation supply from the satisfaction of heating
+ cooling demand. Ventilation air tends to be supplied at neutral temperatures
(close to room air temperature) and heating / cooling loads are met with additional
pieces of zone equipment (eg. Fan Coil Units (FCUs)).
_
Because DOAS systems only have to cool down and re-heat the minimum ventilation air,
they tend to use less energy than all-air systems. They also tend to use less energy
to distribute heating + cooling by puping around hot/cold water or refrigerant
instead of blowing hot/cold air. However, they do not provide as good of control
over humidity and so they may not be appropriate for rooms with high latent loads
like auditoriums, kitchens, laundromats, etc.
-

    Args:
        _rooms: Honeybee Rooms to which the input template HVAC will be assigned.
            This can also be a Honeybee Model for which all conditioned Rooms
            will be assigned the HVAC system.
        _system_type: Text for the specific type of DOAS system and equipment.
            The "HB DOAS HVAC Templates" component has a full list of the
            supported DOAS system templates.
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
        _name_: Text to set the name for the HVAC system and to be incorporated into
            unique HVAC identifier. If the name is not provided, a random name
            will be assigned.
        sensible_hr_: A number between 0 and 1 for the effectiveness of sensible
            heat recovery within the system. Typical values range from 0.5 for
            simple glycol loops to 0.81 for enthalpy wheels (the latter of
            which is a fairly common ECM for DOAS systems) Default: auto-calculated
            by vintage (usually 0 for no heat recovery).
        latent_hr_: A number between 0 and 1 for the effectiveness of latent heat
            recovery within the system. Typical values are 0 for all types of
            heat recovery except enthalpy wheels, which can have values as high
            as 0.76. Default: auto-calculated by vintage (usually 0 for no heat
            recovery).

    Returns:
        rooms: The input Rooms with a DOAS HVAC system applied.
"""

ghenv.Component.Name = "HB DOAS HVAC"
ghenv.Component.NickName = 'DOASHVAC'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '4 :: HVAC'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

import uuid

try:  # import the honeybee extension
    from honeybee.altnumber import autosize
    from honeybee.typing import clean_and_id_ep_string
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.hvac.doas import EQUIPMENT_TYPES_DICT
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
    # set default values for heat recovery
    sens = sensible_hr_ if sensible_hr_ is not None else autosize
    latent = latent_hr_ if latent_hr_ is not None else autosize
    # get an identifier for the HVAC system
    name = clean_and_id_ep_string(_name_) if _name_ is not None else str(uuid.uuid4())[:8]
    hvac = hvac_class(name, vintage, _system_type, sens, latent)
    if _name_ is not None:
        hvac.display_name = _name_

    # apply the HVAC system to the rooms
    for room in rooms:
        if room.properties.energy.is_conditioned:
            room.properties.energy.hvac = hvac
