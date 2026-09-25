# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Define exaust air for rooms or programs in terms of a flow rate per fixture and a
fixture count for each room. Note that this overwrites any exhaust air flow
that might have been defined in terms of a per-unit-area.
_
The term "fixture" is used broadly as a way to reference a wide variety of
contaminant sources such as toilets/urinals, shower heads, kitchen hoods,
fume hoods, etc. Accordingly, this component is the recommended way to set up
rooms for compliance with ventilation standards like ASHRAE 62.1, where exhaust
air is definied in terms of how many fixutres of a certain type exist in the space.
-

    Args:
        _room_or_program: Honeybee Rooms or ProgramType objects which will have exhaust air
            edited to be defined in terms of a flow rate per fixture and a
            fixture count. This can also be the identifier of a ProgramType
            to be looked up in the program type library. This can also be a
            Honeybee Model for which all Rooms will have their exaust air
            properties changed.
        _flow_per_fixture: A numerical value for the level of exhaust air ventilation
            in m3/s for each fixture in the room. The term "fixture" is used
            broadly as a way to reference a wide variety of contaminant sources
            such as toilets/urinals, shower heads, kitchen hoods, fume hoods,
            etc. Typical values for different types of fixtures in ASHRAE 62.1
            are as follows:
                * Private Toilet - 0.0236 m3/s
                * Public Toilet - 0.03304 m3/s
                * Locker Room Shower Head - 0.0236 m3/s
                * Residential Kitchen Hood - 0.04719 m3/s
                * Fume Hood - ~0.2832 m3/s (4' wide hood with 1.5' sash height)
        _fixture_count_: An integer for the number of fixtures in the room. This
            is multiplied by the _flow_per_fixture_, which is then added to the
            flow_per_area to yield the final exhaust air flow rate (Default: 1).
        schedule_: An optional fractional schedule for the exhaust air ventilation over
            the course of the year. The type of this schedule should be
            Fractional and the fractional values get multiplied by
            the total design flow rate to yield a complete exhaust air profile.
            Values of 0 in the schedule will shut the exhaust fan off completely.
            If None, the design level of exhaust air will be used throughout
            all timesteps of the simulation, meaning that this schedule is
            Always On. (Default: None).
        _pressure_rise_: A number for the the pressure rise across the fan in Pascals
            (N/m2). This is often a function of the fan speed and the conditions in
            which the fan is operating. It plays an important role in determining
            the amount of energy consumed by the fan. Typical kitchen and bathroom
            exhaust fans have pressure rises around 125 Pa but, in healthcare
            settings where filters create more resistance, higher pressures
            around 250 Pa are more common. (Default: 125).
        _efficiency_: A number between 0 and 1 for the overall efficiency of the fan.
            Specifically, this is the ratio of the power delivered to the fluid
            to the electrical input power. It is the product of the fan motor
            efficiency and the fan impeller efficiency.
            Fans that have a higher blade diameter, no obstructions or filters,
            and operate at lower speeds with smaller pressure rises for
            their size tend to have higher efficiencies. Because motor efficiencies
            are typically between 0.8 and 0.9, the best overall fan efficiencies
            tend to be around 0.7 with most typical fan efficiencies between 0.5 and
            0.7. When filters are added, which is common for most exhaust fans,
            the total efficiency typically ends up between 0.3 and 0.4. (Default: 0.35).

    Returns:
        report: Reports, errors, warnings, etc.
        mod_obj: The input Rooms or ProgramTypes with exhaust air defined in terms
            of a fixture count and flow per fixture.
"""

ghenv.Component.Name = 'HB Apply Exhaust by Fixture'
ghenv.Component.NickName = 'ExhaustFixture'
ghenv.Component.Message = '1.10.0'
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
    from honeybee_energy.load.exhaust import ExhaustAir
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

    # assign the exhaust criteria
    for i, obj in enumerate(edit_objs):
        vent = dup_load(obj, 'exhaust', ExhaustAir)
        vent.flow_per_area = 0
        vent.flow_per_fixture = longest_list(_flow_per_fixture, i)
        if len(_fixture_count_) != 0:
            vent.fixture_count = longest_list(_fixture_count_, i)
        if len(_pressure_rise_) != 0:
            vent.pressure_rise = longest_list(_pressure_rise_, i)
        if len(_efficiency_) != 0:
            vent.efficiency = longest_list(_efficiency_, i)
        if len(schedule_) != 0:
            sched = longest_list(schedule_, i)
            if isinstance(sched, str):
                sched = schedule_by_identifier(sched)
            vent.schedule = sched
        try:  # assume it's a Room
            obj.properties.energy.exhaust = vent
        except AttributeError:  # it's a ProgramType
            obj.exhaust = vent
