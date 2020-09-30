# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Apply load values to a Room or ProgramType.
_
This component will not edit any of the schedule objects associated with each load
value. If no schedule currently exists to describe how the load varies over the
simulation, the "Always On" schedule will be used as a default.
-

    Args:
        _room_or_program: Honeybee Rooms or ProgramType objects to which the input
            load objects should be assigned. This can also be the identifier of a
            ProgramType to be looked up in the program type library.
        people_per_floor_: A numerical value for the number of people per square
            meter of floor area.
        lighting_per_floor_: A numerical value for the lighting power density in
            Watts per square meter of floor area.
        electric_per_floor_: A numerical value for the electric equipment power density
            in Watts per square meter of floor area.
        gas_per_floor_: A numerical value for the gas equipment power density in
            Watts per square meter of floor area.
        infilt_per_exterior_: A numerical value for the intensity of infiltration
            in m3/s per square meter of exterior surface area. Typical values for
            this property are as follows (note all values are at typical building
            pressures of ~4 Pa):
                * 0.0001 (m3/s per m2 facade) - Tight building
                * 0.0003 (m3/s per m2 facade) - Average building
                * 0.0006 (m3/s per m2 facade) - Leaky building
        vent_per_floor_: A numerical value for the intensity of ventilation in m3/s
            per square meter of floor area.
        vent_per_person_: A numerical value for the intensity of ventilation
            in m3/s per person. Note that setting this value here does not mean
            that ventilation is varied based on real-time occupancy but rather
            that the design level of ventilation is determined using this value
            and the People object of the zone. To vary ventilation in real time,
            the ventilation schedule should be used. Most ventilation standards
            support that a value of 0.01 m3/s (10 L/s or ~20 cfm) per person is
            sufficient to remove odors. Accordingly, setting this value to 0.01
            and using 0 for the following ventilation terms will often be suitable
            for many applications.
    
    Returns:
        report: Reports, errors, warnings, etc.
        mod_obj: The input Rooms or ProgramTypes with their load values modified.
"""

ghenv.Component.Name = "HB Apply Load Values"
ghenv.Component.NickName = 'ApplyLoadVals'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    from honeybee.room import Room
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.load.people import People
    from honeybee_energy.load.lighting import Lighting
    from honeybee_energy.load.equipment import ElectricEquipment, GasEquipment
    from honeybee_energy.load.infiltration import Infiltration
    from honeybee_energy.load.ventilation import Ventilation
    from honeybee_energy.lib.schedules import schedule_by_identifier
    from honeybee_energy.lib.programtypes import program_type_by_identifier
    from honeybee_energy.programtype import ProgramType
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))
try:
    from ladybug_rhino.grasshopper import all_required_inputs, longest_list
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


# get the always on schedule
always_on = schedule_by_identifier('Always On')


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
        try:  # assume it's People, Lighting, Equipment or Infiltration
            return object_class(load_id, 0, always_on)
        except:  # it's a Ventilation object
            return object_class(load_id)


def assign_load(hb_obj, load_obj, object_name):
    """Assign a load object to a Room or a ProgramType."""
    try:  # assume it's a Room
        setattr(hb_obj.properties.energy, object_name, load_obj)
    except AttributeError:  # it's a ProgramType
        setattr(hb_obj, object_name, load_obj)


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    mod_obj = []
    for obj in _room_or_program:
        if isinstance(obj, (Room, ProgramType)):
            mod_obj.append(obj.duplicate())
        elif isinstance(obj, str):
            program = program_type_by_identifier(obj)
            mod_obj.append(program.duplicate())
        else:
            raise TypeError('Expected Honeybee Room or ProgramType. '
                            'Got {}.'.format(type(obj)))

    # assign the people_per_floor_
    if len(people_per_floor_) != 0:
        for i, obj in enumerate(mod_obj):
            people = dup_load(obj, 'people', People)
            people.people_per_area = longest_list(people_per_floor_, i)
            assign_load(obj, people, 'people')

    # assign the lighting_per_floor_
    if len(lighting_per_floor_) != 0:
        for i, obj in enumerate(mod_obj):
            lighting = dup_load(obj, 'lighting', Lighting)
            lighting.watts_per_area = longest_list(lighting_per_floor_, i)
            assign_load(obj, lighting, 'lighting')

    # assign the electric_per_floor_
    if len(electric_per_floor_) != 0:
        for i, obj in enumerate(mod_obj):
            equip = dup_load(obj, 'electric_equipment', ElectricEquipment)
            equip.watts_per_area = longest_list(electric_per_floor_, i)
            assign_load(obj, equip, 'electric_equipment')

    # assign the gas_per_floor_
    if len(gas_per_floor_) != 0:
        for i, obj in enumerate(mod_obj):
            equip = dup_load(obj, 'gas_equipment', GasEquipment)
            equip.watts_per_area = longest_list(gas_per_floor_, i)
            assign_load(obj, equip, 'gas_equipment')
    
    # assign the infilt_per_exterior_
    if len(infilt_per_exterior_) != 0:
        for i, obj in enumerate(mod_obj):
            infilt = dup_load(obj, 'infiltration', Infiltration)
            infilt.flow_per_exterior_area = longest_list(infilt_per_exterior_, i)
            assign_load(obj, infilt, 'infiltration')

    # assign the vent_per_floor_
    if len(vent_per_floor_) != 0:
        for i, obj in enumerate(mod_obj):
            vent = dup_load(obj, 'ventilation', Ventilation)
            vent.flow_per_area = longest_list(vent_per_floor_, i)
            assign_load(obj, vent, 'ventilation')

    # assign the vent_per_person_
    if len(vent_per_person_) != 0:
        for i, obj in enumerate(mod_obj):
            vent = dup_load(obj, 'ventilation', Ventilation)
            vent.flow_per_person = longest_list(vent_per_person_, i)
            assign_load(obj, vent, 'ventilation')
