# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Apply schedules to a Room, Model or ProgramType.
_
Note that, if a schedule is assigned to a Room or ProgramType that posseses
no value for a given load, an error will be raised. For example, assigning a
gas_equip_sch_ to a Room that has no GasEquipment object associated with it.
This situation can be avoided by first passing the Rooms or ProgramTypes
through the "HB Apply Load Values" component to eastablish a value for a
given load.
-

    Args:
        _room_or_program: Honeybee Rooms or Honeybee ProgramType objects for which
            schedules should be changed. This can also be the identifier of a
            ProgramType to be looked up in the program type library. This can
            also be a Honeybee Model for which all Rooms will be assigned
            the schedules.
        occupancy_sch_: A fractional schedule for the occupancy over the course
            of the year. This can also be the identifier of a schedule to be looked
            up in the schedule library.
        activity_sch_: A schedule for the activity of the occupants over the course of the
            year. The type limt of this schedule should be "ActivityLevel"
            and the values of the schedule equal to the number of Watts given off
            by an individual person in the room. If None, it will a default constant
            schedule with 120 Watts per person will be used, which is typical of
            awake, adult humans who are seated.
        lighting_sch_: A fractional schedule for the use of lights over the course of
            the year. This can also be the identifier of a schedule to be looked
            up in the schedule library.
        electric_equip_sch_: A fractional schedule for the use of electric equipment over
            the course of the year. This can also be the identifier of a schedule to
            be looked up in the schedule library.
        gas_equip_sch_: A fractional schedule for the use of gas equipment over the course of
            the year. This can also be the identifier of a schedule to
            be looked up in the schedule library.
        hot_water_sch_: A fractional schedule for the use of service hot water over
            the course of the year. This can also be the identifier of a
            schedule to be looked up in the schedule library.
        infiltration_sch_: A fractional schedule for the infiltration over the
            course of the year. This can also be the identifier of a schedule to
            be looked up in the schedule library.
        ventilation_sch_: A fractional schedule for the ventilation over the course of
            the year. This can also be the identifier of a schedule to be
            looked up in the schedule library. The fractional values will get
            multiplied by the total design flow rate to yield a complete ventilation
            profile. Setting this schedule to be the occupancy schedule of the
            zone will mimic demand controlled ventilation.
        heating_setpt_sch_: A temperature schedule for the heating setpoint.
            This can also be a identifier of a schedule to be looked up in the
            schedule library. The type limit of this schedule should be
            temperature and the values should be the temperature setpoint in
            degrees Celcius.
        cooling_setpt_sch_: A temperature schedule for the cooling setpoint.
            This can also be a identifier of a schedule to be looked up in the
            schedule library. The type limit of this schedule should be
            temperature and the values should be the temperature setpoint in
            degrees Celcius.

    Returns:
        report: Reports, errors, warnings, etc.
        mod_obj: The input Rooms or ProgramTypes with their schedules modified.
"""

ghenv.Component.Name = "HB Apply Room Schedules"
ghenv.Component.NickName = 'ApplyRoomSch'
ghenv.Component.Message = '1.7.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '2 :: Schedules'
ghenv.Component.AdditionalHelpFromDocStrings = "3"

import uuid

try:
    from honeybee.model import Model
    from honeybee.room import Room
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.lib.schedules import schedule_by_identifier
    from honeybee_energy.lib.programtypes import program_type_by_identifier, \
        building_program_type_by_identifier
    from honeybee_energy.programtype import ProgramType
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, longest_list
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def schedule_object(schedule):
    """Get a schedule object by its identifier or return it it it's already a schedule."""
    if isinstance(schedule, str):
        return schedule_by_identifier(schedule)
    return schedule


def dup_load(hb_obj, object_name, input_name):
    """Duplicate a load object assigned to a Room or ProgramType."""
    # try to get the load object assgined to the Room or ProgramType
    try:  # assume it's a Room
        load_obj = hb_obj.properties
        for attribute in ('energy', object_name):
            load_obj = getattr(load_obj, attribute)
    except AttributeError:  # it's a ProgramType
        load_obj = getattr(hb_obj, object_name)

    try:  # duplicate the load object
        dup_load = load_obj.duplicate()
        dup_load.identifier = '{}_{}'.format(hb_obj.identifier, object_name)
        return dup_load
    except AttributeError:
        raise ValueError(
            '{0} has been input but the Room or ProgramType posseses no {1} object.'
            '\nUse the "HB Apply Load Values" component to define a {1} '
            'object.'.format(input_name, object_name))


def assign_load(hb_obj, load_obj, object_name):
    """Assign a load object to a Room or a ProgramType."""
    try:  # assume it's a Room
        setattr(hb_obj.properties.energy, object_name, load_obj)
    except AttributeError:  # it's a ProgramType
        setattr(hb_obj, object_name, load_obj)


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

    # assign the occupancy schedule
    if len(occupancy_sch_) != 0:
        for i, obj in enumerate(edit_objs):
            people = dup_load(obj, 'people', 'occupancy_sch_')
            people.occupancy_schedule = schedule_object(longest_list(occupancy_sch_, i))
            assign_load(obj, people, 'people')

    # assign the activity schedule
    if len(activity_sch_) != 0:
        for i, obj in enumerate(edit_objs):
            people = dup_load(obj, 'people', 'activity_sch_')
            people.activity_schedule = schedule_object(longest_list(activity_sch_, i))
            assign_load(obj, people, 'people')

    # assign the lighting schedule
    if len(lighting_sch_) != 0:
        for i, obj in enumerate(edit_objs):
            lighting = dup_load(obj, 'lighting', 'lighting_sch_')
            lighting.schedule = schedule_object(longest_list(lighting_sch_, i))
            assign_load(obj, lighting, 'lighting')

    # assign the electric equipment schedule
    if len(electric_equip_sch_) != 0:
        for i, obj in enumerate(edit_objs):
            equip = dup_load(obj, 'electric_equipment', 'electric_equip_sch_')
            equip.schedule = schedule_object(longest_list(electric_equip_sch_, i))
            assign_load(obj, equip, 'electric_equipment')

    # assign the gas equipment schedule
    if len(gas_equip_sch_) != 0:
        for i, obj in enumerate(edit_objs):
            equip = dup_load(obj, 'gas_equipment', 'gas_equip_sch_')
            equip.schedule = schedule_object(longest_list(gas_equip_sch_, i))
            assign_load(obj, equip, 'gas_equipment')

    # assign the hot water schedule
    if len(hot_water_sch_) != 0:
        for i, obj in enumerate(edit_objs):
            shw = dup_load(obj, 'service_hot_water', 'hot_water_sch_')
            shw.schedule = schedule_object(longest_list(hot_water_sch_, i))
            assign_load(obj, shw, 'service_hot_water')

    # assign the infiltration schedule
    if len(infiltration_sch_) != 0:
        for i, obj in enumerate(edit_objs):
            infiltration = dup_load(obj, 'infiltration', 'infiltration_sch_')
            infiltration.schedule = schedule_object(longest_list(infiltration_sch_, i))
            assign_load(obj, infiltration, 'infiltration')

    # assign the ventilation schedule
    if len(ventilation_sch_) != 0:
        for i, obj in enumerate(edit_objs):
            ventilation = dup_load(obj, 'ventilation', 'ventilation_sch_')
            ventilation.schedule = schedule_object(longest_list(ventilation_sch_, i))
            assign_load(obj, ventilation, 'ventilation')

    # assign the heating setpoint schedule
    if len(heating_setpt_sch_) != 0:
        for i, obj in enumerate(edit_objs):
            setpoint = dup_load(obj, 'setpoint', 'heating_setpt_sch_')
            setpoint.heating_schedule = schedule_object(longest_list(heating_setpt_sch_, i))
            assign_load(obj, setpoint, 'setpoint')

    # assign the cooling setpoint schedule
    if len(cooling_setpt_sch_) != 0:
        for i, obj in enumerate(edit_objs):
            setpoint = dup_load(obj, 'setpoint', 'cooling_setpt_sch_')
            setpoint.cooling_schedule = schedule_object(longest_list(cooling_setpt_sch_, i))
            assign_load(obj, setpoint, 'setpoint')
