# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Adjust ventilation properties that impact how minimum outdoor air requirements
are computed for rooms.
_
This includes whether or not the different types of outdoor air flow rates
are summed together (the default) or the maximum is taken across the flow rates.
_
It also includes terms for the ventilation distribution effectivness, which
can raise the outdoor air requirements if a given system configuration does not
evenly distribute air througout the room. It can also lower the outdoor air
requirement if a system configuration is particularly good at delivering
air to the breathing zone of the room.
-

    Args:
        _room_or_program: Honeybee Rooms or ProgramType objects which will have ventilation
            properties changed. This can also be the identifier of a ProgramType
            to be looked up in the program type library. This can also be a
            Honeybee Model for which all Rooms will have their ventilation
            properties changed.
        use_max_flow_: Set to "True" to use the maximum flow rate across the the different
            types of outdoor air criteria instead of summing them together (the default).
            Summing together ventilation per-person and per-floor-area is how
            standards like ASHRAE 62.1 are written but other standards may
            use the maximum across specified criteria.
        effectiveness_cool_: A positive number to note the air distribution effectiveness
            of the ventilation system when it operates in cooling mode
            (or how well the system is able to mix the air when cooling).
            A value of 1 means that air is well mixed and specified air flows are not
            adjusted in the course of simulation. Values less than 1 indicate systems
            that do not mix the air as well and so the specified airflows are increased.
            Values greater than 1 indicate systems that are particularly good at
            delivering outdoor air to the breathing zone of a room and so the
            specified airflows can be reduced. (Default: 1).
        effectiveness_heat_: A positive number to note the air distribution effectiveness
            of the ventilation system when it operates in heating mode
            (or how well the system is able to mix the air when heating).
            A value of 1 means that air is well mixed and specified air flows are not
            adjusted in the course of simulation. Values less than 1 indicate systems
            that do not mix the air as well and so the specified airflows are increased.
            Values greater than 1 indicate systems that are particularly good at
            delivering outdoor air to the breathing zone of a room and so the
            specified airflows can be reduced. (Default: 1).
        secondary_recirc_: A number that is greater than or equal to zero, which notes
            the fraction of a zone's recirculation air that does not directly
            mix with the outdoor air. Used in cases where a central ventilation
            system supplies several zones and the return air is not collected
            through ducts back to the central air handler (eg. a plenum return
            system is used). This means unused outdoor ventilation air from other
            zones in the central system can be credited to the room. (Default: 0).

    Returns:
        report: Reports, errors, warnings, etc.
        mod_obj: The input Rooms or ProgramTypes with ventilation properties adjusted.
"""

ghenv.Component.Name = 'HB Ventilation Distribution'
ghenv.Component.NickName = 'VentDistrib'
ghenv.Component.Message = '1.10.1'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import uuid

try:
    from honeybee.model import Model
    from honeybee.room import Room
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.load.ventilation import Ventilation
    from honeybee_energy.lib.programtypes import program_type_by_identifier, \
        building_program_type_by_identifier
    from honeybee_energy.programtype import ProgramType
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, longest_list
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def dup_load(hb_obj, object_name, object_class):
    """Duplicate a load object assigned to a Room or ProgramType."""
    # try to get the load object assgined to the Room or ProgramType
    try:  # assume it's a Room
        load_obj = hb_obj.properties
        for attribute in ('energy', object_name):
            load_obj = getattr(load_obj, attribute)
    except AttributeError:  # it's a ProgramType
        load_obj = getattr(hb_obj, object_name)

    load_id = '{}_{}'.format(hb_obj.identifier, object_name)
    try:  # duplicate the load object
        dup_load = load_obj.duplicate()
        dup_load.identifier = load_id
        return dup_load
    except AttributeError:  # create a new object
        return object_class(load_id)


def duplicate_and_id_program(program):
    """Duplicate a program and give it a new unique ID."""
    new_prog = program.duplicate()
    new_prog.identifier = '{}_{}'.format(program.identifier, str(uuid.uuid4())[:8])
    return new_prog


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    mod_obj, edit_objs = [], []
    for obj in _room_or_program:
        if isinstance(obj, Room):
            new_obj = obj.duplicate()
            mod_obj.append(new_obj)
            edit_objs.append(new_obj)
        elif isinstance(obj, Model):
            new_obj = obj.duplicate()
            mod_obj.append(new_obj)
            edit_objs.extend(new_obj.rooms)
        elif isinstance(obj, ProgramType):
            new_obj = duplicate_and_id_program(obj)
            mod_obj.append(new_obj)
            edit_objs.append(new_obj)
        elif isinstance(obj, str):
            try:
                program = building_program_type_by_identifier(obj)
            except ValueError:
                program = program_type_by_identifier(obj)
            new_obj = duplicate_and_id_program(program)
            mod_obj.append(new_obj)
            edit_objs.append(new_obj)
        else:
            raise TypeError('Expected Honeybee Room, Model or ProgramType. '
                            'Got {}.'.format(type(obj)))

    # set default values and check the inputs
    use_max_flow_ = [False] if len(use_max_flow_) == 0 else use_max_flow_
    effectiveness_cool_ = [1] if len(effectiveness_cool_) == 0 else effectiveness_cool_
    effectiveness_heat_ = [1] if len(effectiveness_heat_) == 0 else effectiveness_heat_
    secondary_recirc_ = [0] if len(secondary_recirc_) == 0 else secondary_recirc_

    # assign the ventilation criteria
    for i, obj in enumerate(edit_objs):
        vent = dup_load(obj, 'ventilation', Ventilation)
        if longest_list(use_max_flow_, i):
            vent.method = 'Max'
        else:
            vent.method = 'Sum'
        vent.effectiveness_cooling = longest_list(effectiveness_cool_, i)
        vent.effectiveness_heating = longest_list(effectiveness_heat_, i)
        vent.secondary_recirculation = longest_list(secondary_recirc_, i)
        try:  # assume it's a Room
            obj.properties.energy.ventilation = vent
        except AttributeError:  # it's a ProgramType
            obj.ventilation = vent
