# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Apply schedules to the various load objects of a Room.
_
Note that, if a schedule is assigned to a Room that posseses no value for a
given load, an error will be raised. For example, assigning a gas_equip_sch_
to a Room that has no GasEquipment object associated with it. This situation
can be avoided by first passing the Rooms through the "HB Apply Load Values"
component to eastablish a value for a given load.
-

    Args:
        _rooms: Honeybee Rooms for which schedules should be changed.
        occupancy_sch_: A fractional schedule for the occupancy over the course
            of the year. This can also be the name of a schedule to be looked
            up in the schedule library.
        activity_sch_: A schedule for the activity of the occupants over the
            course of the year. The type limt of this schedule should be "Power"
            and the values of the schedule equal to the number of Watts given off
            by an individual person in the room. If None, it will a default constant
            schedule with 120 Watts per person will be used, which is typical of
            awake, adult humans who are seated.
         heating_setpt_sch_: A temperature schedule for the heating setpoint.
            This can also be a name of a schedule to be looked up in the
            schedule library. The type limit of this schedule should be
            temperature and the values should be the temperature setpoint in
            degrees Celcius.
        cooling_setpt_sch_: A temperature schedule for the cooling setpoint.
            This can also be a name of a schedule to be looked up in the
            schedule library. The type limit of this schedule should be
            temperature and the values should be the temperature setpoint in
            degrees Celcius.
        lighting_sch_: A fractional for the use of lights over the course of the year.
            This can also be the name of a schedule to be looked up in the
            schedule library.
        electric_equip_sch_: A fractional for the use of electric equipment over
            the course of the year. This can also be the name of a schedule to
            be looked up in the schedule library.
        gas_equip_sch_: A fractional for the use of gas equipment over
            the course of the year. This can also be the name of a schedule to
            be looked up in the schedule library.
        infiltration_sch_: A fractional schedule for the infiltration over the
            course of the year. This can also be the name of a schedule to
            be looked up in the schedule library.
        ventilation_sch_: An optional fractional schedule for the ventilation over the
            course of the year. This can also be the name of a schedule to be
            looked up in the schedule library. The fractional values will get
            multiplied by the total design flow rate (determined from the fields
            above and the calculation_method) to yield a complete ventilation
            profile. Setting this schedule to be the occupancy schedule of the
            zone will mimic demand controlled ventilation.
    
    Returns:
        report: Reports, errors, warnings, etc.
        rooms: The input Rooms with their schedules edited.
"""

ghenv.Component.Name = "HB Apply Room Schedules"
ghenv.Component.NickName = 'ApplyRoomSch'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "Energy"
ghenv.Component.SubCategory = '2 :: Schedules'
ghenv.Component.AdditionalHelpFromDocStrings = "3"

try:
    from honeybee_energy.lib.schedules import schedule_by_name
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def dup_load(load_obj, input_name, object_name):
    """Duplicate a Room load object with a check to make sure the object exists."""
    try:
        return load_obj.duplicate()
    except AttributeError:
        raise ValueError(
            '{0} has been input but the Room posseses no {1} object.\nUse the '
            '"HB Apply Load Values" component to define a {1} '
            'object.'.format(input_name, object_name))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    rooms = [obj.duplicate() for obj in _rooms]
    
    # assign the occupancy schedule
    if occupancy_sch_ is not None:
        if isinstance(occupancy_sch_, str):
            occupancy_sch_ = schedule_by_name(occupancy_sch_)
        for room in rooms:
            people = dup_load(room.properties.energy.people,
                              'occupancy_sch_', 'people')
            people.occupancy_schedule = occupancy_sch_
            room.properties.energy.people = people
    
    # assign the activity schedule
    if activity_sch_ is not None:
        if isinstance(activity_sch_, str):
            activity_sch_ = schedule_by_name(activity_sch_)
        for room in rooms:
            people = dup_load(room.properties.energy.people,
                              'activity_sch_', 'people')
            people.activity_schedule = activity_sch_
            room.properties.energy.people = people
    
    # assign the heating setpoint schedule
    if heating_setpt_sch_ is not None:
        if isinstance(heating_setpt_sch_, str):
            heating_setpt_sch_ = schedule_by_name(heating_setpt_sch_)
        for room in rooms:
            setpoint = dup_load(room.properties.energy.setpoint,
                                'heating_setpt_sch_', 'setpoint')
            setpoint.heating_schedule = heating_setpt_sch_
            room.properties.energy.setpoint = setpoint
    
    # assign the cooling setpoint schedule
    if cooling_setpt_sch_ is not None:
        if isinstance(cooling_setpt_sch_, str):
            cooling_setpt_sch_ = schedule_by_name(cooling_setpt_sch_)
        for room in rooms:
            setpoint = dup_load(room.properties.energy.setpoint,
                                'cooling_setpt_sch_', 'setpoint')
            setpoint.cooling_schedule = cooling_setpt_sch_
            room.properties.energy.setpoint = setpoint
    
    # assign the lighting schedule
    if lighting_sch_ is not None:
        if isinstance(lighting_sch_, str):
            lighting_sch_ = schedule_by_name(lighting_sch_)
        for room in rooms:
            lighting = dup_load(room.properties.energy.lighting,
                                'lighting_sch_', 'lighting')
            lighting.schedule = lighting_sch_
            room.properties.energy.lighting = lighting
    
    # assign the electric equipment schedule
    if electric_equip_sch_ is not None:
        if isinstance(electric_equip_sch_, str):
            electric_equip_sch_ = schedule_by_name(electric_equip_sch_)
        for room in rooms:
            equip = dup_load(room.properties.energy.electric_equipment,
                             'electric_equip_sch_', 'electric equipment')
            equip.schedule = electric_equip_sch_
            room.properties.energy.electric_equipment = equip
    
    # assign the gas equipment schedule
    if gas_equip_sch_ is not None:
        if isinstance(gas_equip_sch_, str):
            gas_equip_sch_ = schedule_by_name(gas_equip_sch_)
        for room in rooms:
            equip = dup_load(room.properties.energy.gas_equipment,
                             'gas_equip_sch_', 'gas equipment')
            equip.schedule = gas_equip_sch_
            room.properties.energy.gas_equipment = equip
    
    # assign the infiltration schedule
    if infiltration_sch_ is not None:
        if isinstance(infiltration_sch_, str):
            infiltration_sch_ = schedule_by_name(infiltration_sch_)
        for room in rooms:
            infiltration = dup_load(room.properties.energy.infiltration,
                                    'infiltration_sch_', 'infiltration')
            infiltration.schedule = infiltration_sch_
            room.properties.energy.infiltration = infiltration
    
    # assign the infiltration schedule
    if ventilation_sch_ is not None:
        if isinstance(ventilation_sch_, str):
            ventilation_sch_ = schedule_by_name(ventilation_sch_)
        for room in rooms:
            ventilation = dup_load(room.properties.energy.ventilation,
                                    'ventilation_sch_', 'ventilation')
            ventilation.schedule = ventilation_sch_
            room.properties.energy.ventilation = ventilation
