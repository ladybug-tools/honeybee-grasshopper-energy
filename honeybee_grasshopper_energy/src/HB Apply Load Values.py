# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Apply values for specific load objects to Rooms.
_
This component will not edit any of the schedule objects associated with each load
value. If no schedule currently exists to describe how the load varies over the
simulation, the "Always On" schedule will be used as a default.
-

    Args:
        _rooms: Honeybee Rooms to which the input load objects should be assigned.
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
        rooms: The input Rooms with their load values edited.
"""

ghenv.Component.Name = "HB Apply Load Values"
ghenv.Component.NickName = 'ApplyLoadVals'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "Energy"
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    from honeybee_energy.load.people import People
    from honeybee_energy.load.lighting import Lighting
    from honeybee_energy.load.equipment import ElectricEquipment, GasEquipment
    from honeybee_energy.load.infiltration import Infiltration
    from honeybee_energy.load.ventilation import Ventilation
    from honeybee_energy.lib.schedules import schedule_by_name
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))
try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    rooms = [obj.duplicate() for obj in _rooms]
    
    # get the always on schedule
    always_on = schedule_by_name('Always On')
    
    # assign the people_per_floor_
    if people_per_floor_ is not None:
        for room in rooms:
            try:
                people = room.properties.energy.people.duplicate()
                people.people_per_area = people_per_floor_
            except AttributeError:
                people = People(
                    '{}_People'.format(room.name), people_per_floor_, always_on)
            room.properties.energy.people = people
    
    # assign the lighting_per_floor_
    if lighting_per_floor_ is not None:
        for room in rooms:
            try:
                lighting = room.properties.energy.lighting.duplicate()
                lighting.watts_per_area = lighting_per_floor_
            except AttributeError:
                lighting = Lighting(
                    '{}_Lighting'.format(room.name), lighting_per_floor_, always_on)
            room.properties.energy.lighting = lighting
    
    # assign the electric_per_floor_
    if electric_per_floor_ is not None:
        for room in rooms:
            try:
                equip = room.properties.energy.electric_equipment.duplicate()
                equip.watts_per_area = electric_per_floor_
            except AttributeError:
                equip = ElectricEquipment(
                    '{}_ElectricEquip'.format(room.name), electric_per_floor_, always_on)
            room.properties.energy.electric_equipment = equip
    
    # assign the gas_per_floor_
    if gas_per_floor_ is not None:
        for room in rooms:
            try:
                equip = room.properties.energy.gas_equipment.duplicate()
                equip.watts_per_area = gas_per_floor_
            except AttributeError:
                equip = GasEquipment(
                    '{}_GasEquip'.format(room.name), gas_per_floor_, always_on)
            room.properties.energy.gas_equipment = equip
    
    # assign the infilt_per_exterior_
    if infilt_per_exterior_ is not None:
        for room in rooms:
            try:
                infilt = room.properties.energy.infiltration.duplicate()
                infilt.flow_per_exterior_area = infilt_per_exterior_
            except AttributeError:
                infilt = Infiltration(
                    '{}_Infiltration'.format(room.name), infilt_per_exterior_, always_on)
            room.properties.energy.infiltration = infilt
    
    # assign the vent_per_floor_
    if vent_per_floor_ is not None:
        for room in rooms:
            try:
                vent = room.properties.energy.ventilation.duplicate()
            except AttributeError:
                vent = Ventilation('{}_Ventilation'.format(room.name))
            vent.flow_per_area = vent_per_floor_
            room.properties.energy.ventilation = vent
    
    # assign the vent_per_person_
    if vent_per_person_ is not None:
        for room in rooms:
            try:
                vent = room.properties.energy.ventilation.duplicate()
            except AttributeError:
                vent = Ventilation('{}_Ventilation'.format(room.name))
            vent.flow_per_person = vent_per_person_
            room.properties.energy.ventilation = vent
