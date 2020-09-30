# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Apply an All-Air template HVAC to a list of Honeybee Rooms.
_
All-air systems provide both ventilation and satisfaction of heating + cooling
demand with the same stream of warm/cool air. As such, they often grant tight
control over zone humidity. However, because such systems often involve the
cooling of air only to reheat it again, they are often more energy intensive
than systems that separate ventilation from the meeting of thermal loads.
-

    Args:
        _rooms: Honeybee Rooms to which the input template HVAC will be assigned.
            This can also be a Honeybee Model for which all conditioned Rooms
            will be assigned the HVAC system.
        _system_type: Text for the specific type of all-air system and equipment.
            The "HB All-Air HVAC Templates" component has a full list of the
            supported all-air system templates.
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
        _economizer_: Text to indicate the type of air-side economizer used on the
            HVAC system. Economizers will mix in a greater amount of outdoor
            air to cool the zone (rather than running the cooling system) when
            the zone needs cooling and the outdoor air is cooler than the zone.
            Choose from the options below. If Inferred, the economizer will be set
            to whatever is recommended for the given vintage. Default: Inferred.
                * Inferred
                * NoEconomizer
                * DifferentialDryBulb
                * DifferentialEnthalpy
        sensible_hr_: A number between 0 and 1 for the effectiveness of sensible
            heat recovery within the system. Typical values range from 0.5 for
            simple glycol loops to 0.81 for enthalpy wheels (the latter tends to
            be fiarly expensive for air-based systems) Default: auto-calculated
            by vintage (usually 0 for no heat recovery).
        latent_hr_: A number between 0 and 1 for the effectiveness of latent heat
            recovery within the system. Typical values are 0 for all types of
            heat recovery except enthalpy wheels, which can have values as high
            as 0.76. Default: auto-calculated by vintage (usually 0 for no heat
            recovery).

    Returns:
        rooms: The input Rooms with an all-air HVAC system applied.
"""

ghenv.Component.Name = "HB All-Air HVAC"
ghenv.Component.NickName = 'AllAirHVAC'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '4 :: HVAC'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import uuid

try:  # import the honeybee extension
    from honeybee.altnumber import autosize
    from honeybee.typing import clean_and_id_ep_string
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.hvac.allair import EQUIPMENT_TYPES_DICT
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
    # set default values for economizer and heat recovery
    econ = _economizer_ if _economizer_ is not None else 'Inferred'
    sens = sensible_hr_ if sensible_hr_ is not None else autosize
    latent = latent_hr_ if latent_hr_ is not None else autosize
    # get an identifier for the HVAC system
    name = clean_and_id_ep_string(_name_) if _name_ is not None else str(uuid.uuid4())[:8]
    hvac = hvac_class(name, vintage, _system_type, econ, sens, latent)
    if _name_ is not None:
        hvac.display_name = _name_

    # apply the HVAC system to the rooms
    for room in rooms:
        if room.properties.energy.is_conditioned:
            room.properties.energy.hvac = hvac
