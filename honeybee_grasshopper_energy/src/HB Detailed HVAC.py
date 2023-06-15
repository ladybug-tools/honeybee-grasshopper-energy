# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Apply a detailed Ironbug HVAC to Honeybee Rooms or a Honeybee Model.
-

    Args:
        _hb_objs: Honeybee Rooms to which the input Ironbug HVAC will be assigned.
            This can also be a Honeybee Model for which the relevant Rooms
            referenced in the _hvac_system will be assigned the HVAC system.
        _hvac_system: A fully-detailed Irongbug HVAC system to be assigned to the
            input rooms (or model). 
        _name_: Text to set the name for the HVAC system and to be incorporated into
            unique HVAC identifier. If the name is not provided, a random name
            will be assigned.

    Returns:
        report: Reports, errors, warnings, etc.
        hb_objs: The input Rooms or Model with the detailed HVAC system applied.
"""

ghenv.Component.Name = "HB Detailed HVAC"
ghenv.Component.NickName = 'DetailedHVAC'
ghenv.Component.Message = '1.6.1'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '4 :: HVAC'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

import json

try:  # import the honeybee extension
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
    from honeybee.model import Model
    from honeybee.room import Room
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.config import folders
    from honeybee_energy.hvac.detailed import DetailedHVAC
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

if folders.ironbug_exe is None:
    msg = 'An installation of Ironbug that is compatible with this component\n' \
        'was not found on this machine. This component will not be usable.'
    print(msg)
    give_warning(ghenv.Component, msg)
elif folders.ironbug_version is not None:
    if folders.ironbug_version < (1, 9, 1):
        msg = 'Ironbug version "{}" is not compatible with this component.\n' \
            'This component will not be usable.'.format(
                '.'.join([str(i) for i in folders.ironbug_version]))
        print(msg)
        give_warning(ghenv.Component, msg)
else:
    msg = 'An installation of Ironbug was found at: {}\nbut it is not ' \
        'accessible. Contact your adminstrator.'.format(folders.ironbug_exe)
    print(msg)
    give_warning(ghenv.Component, msg)


if all_required_inputs(ghenv.Component):
    # extract any rooms from input Models and duplicate the rooms
    rooms, hb_objs = [], []
    for hb_obj in _hb_objs:
        if isinstance(hb_obj, Model):
            new_obj = hb_obj.duplicate()
            hb_objs.append(new_obj)
            rooms.extend(new_obj.rooms)
        elif isinstance(hb_obj, Room):
            new_obj = hb_obj.duplicate()
            hb_objs.append(new_obj)
            rooms.append(new_obj)
        else:
            raise ValueError(
                'Expected Honeybee Room or Model. Got {}.'.format(type(hb_obj)))

    # create the HVAC
    name = clean_and_id_ep_string('Detailed HVAC') if _name_ is None else \
        clean_ep_string(_name_)
    specification = json.loads(_hvac_system.ToJson())
    hvac = DetailedHVAC(name, specification)
    if _name_ is not None:
        hvac.display_name = _name_

    # apply the HVAC system to the rooms
    hvac_rooms = set(hvac.thermal_zones)
    hvac_count, rel_rooms = 0, []
    for room in rooms:
        if room.identifier in hvac_rooms:
            room.properties.energy.hvac = hvac
            rel_rooms.append(room.identifier)
            hvac_count += 1

    # give a warning if no rooms were assigned the HVAC or if there are missing rooms
    if hvac_count == 0:
        msg = 'None of the connected Rooms are referenced under the Ironbug HVAC system.\n' \
            'Make sure that the system has been set up with the correct Rooms.'
        print(msg)
        give_warning(ghenv.Component, msg)
    if len(rel_rooms) != len(hvac_rooms):
        missing_rooms = []
        found_rooms = set(rel_rooms)
        for rm_id in hvac_rooms:
            if rm_id not in found_rooms:
                missing_rooms.append(rm_id)
        msg = 'The Ironbug HVAC system contains the following rooms that are not ' \
            'in the connected _hb_objs.\n{}'.format('\n'.join(missing_rooms))
        print(msg)
        give_warning(ghenv.Component, msg)
