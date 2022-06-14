# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Adjust the properties of a Radiant HVAC that has been assigned to Honeybee Rooms.
_
Because Radiant HVAC systems interact with the conditioned rooms through the
thermal mass of the constructions in which they are embedded, their design
often requires
-

    Args:
        _rooms: Honeybee Rooms that have a Radiant HVAC assigned to them, which are to
            have their radiant properties adjusted. This can also be a Honeybee
            Model for which all Rooms with a Radiant HVAC sill be adjusted.
        radiant_type_: Text to indicate which faces are thermally active by default.
            Note that systems are assumed to be embedded in concrete slabs
            with no insulation within the slab unless otherwise specified.
            Choose from the following. (Default: Floor).
                * Floor
                * Ceiling
                * FloorWithCarpet
                * CeilingMetalPanel
                * FloorWithHardwood
        min_op_time_: A number for the minimum number of hours of operation
            for the radiant system before it shuts off. (Default: 1).
        switch_time_: A number for the minimum number of hours for when the system
            can switch between heating and cooling. (Default: 24).

    Returns:
        rooms: The input Rooms with the radiant HVAC properties edited.
"""

ghenv.Component.Name = 'HB Radiant HVAC Properties'
ghenv.Component.NickName = 'RadiantHVAC'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '4 :: HVAC'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the honeybee extension
    from honeybee.model import Model
    from honeybee.room import Room
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.hvac.doas.radiant import RadiantwithDOAS
    from honeybee_energy.hvac.heatcool.radiant import Radiant
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


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

    # collect all of the rooms with radiant systems assigned to them
    rad_hvac_dict = {}
    for room in rooms:
        r_hvac = room.properties.energy.hvac
        if isinstance(r_hvac, (RadiantwithDOAS, Radiant)):
            try:
                rad_hvac_dict[r_hvac.identifier].append(room)
            except KeyError:
                rad_hvac_dict[r_hvac.identifier] = [room]

    # adjust the properties of each radiant HVAC that was found
    for r_hvac_rooms in rad_hvac_dict.values():
        new_r_hvac = r_hvac_rooms[0].properties.energy.hvac.duplicate()
        if min_op_time_:
            new_r_hvac.minimum_operation_time = min_op_time_
        if switch_time_:
            new_r_hvac.switch_over_time = switch_time_
        if radiant_type_:
            new_r_hvac.radiant_type = radiant_type_
        for new_r in r_hvac_rooms:
            new_r.properties.energy.hvac = new_r_hvac

    # raise a warning if no rooms with a radiant HVAC were found
    if len(rad_hvac_dict) == 0:
        msg = 'No Rooms with a Radiant HVAC were found among the connected _rooms.\n' \
            'Make sure that a Radiant HVAC has been assigned with either the\n' \
            '"HB DOAS HVAC" or "HB HeatCool HVAC" component.'
        print(msg)
        give_warning(ghenv.Component, msg)
