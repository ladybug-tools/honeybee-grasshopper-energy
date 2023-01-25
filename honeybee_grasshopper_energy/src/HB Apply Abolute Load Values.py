# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Apply absolute load values to Rooms.
_
Note that, while the assigned load values are absolute, this component will convert
them to the "normalized" value for each room (eg. lighting per floor area) in
order to apply them to the rooms. So any existing specification of load intensity
is overwritten with the absolute load here.
_
This also means that, if a room has no floors (or exterior walls for infiltration),
the resulting load values will be equal to 0 regardless of the input here. The
only exception is the vent_flow_, which will be applied regardless of the room
properties.
_
This component will not edit any of the schedules or other properties associated
with each load value. If no schedule currently exists to describe how the load
varies over the simulation, the "Always On" schedule will be used as a default.
-

    Args:
        _rooms: Honeybee Rooms to which the input load values should be assigned.
        person_count_: A number for the quantity of people in the room.
        lighting_watts_: A number for the installed wattage of lighting in the room (W).
        electric_watts_: A number for the installed wattage of electric equipment
            in the room (W).
        gas_watts_: A number for the installed wattage of gas equipment in the room (W).
        hot_wtr_flow_: Number for the peak flow rate of service hot water in the
            room in liters per hour (L/h).
        infiltration_ach_: A number for the infiltration flow rate in air changes
            per hour (ACH).
        vent_flow_: A numerical value for the absolute of flow of outdoor air ventilation
            for the room in cubic meters per second (m3/s). Note that inputting
            a value here will overwrite all specification of outdoor air ventilation
            currently on the room (per_floor, per_person, ach).

    Returns:
        report: Reports, errors, warnings, etc.
        rooms: The input Rooms with their load values modified.
"""

ghenv.Component.Name = 'HB Apply Abolute Load Values'
ghenv.Component.NickName = 'AbsoluteLoadVals'
ghenv.Component.Message = '1.6.1'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:
    from ladybug_rhino.grasshopper import all_required_inputs, longest_list
    from ladybug_rhino.config import conversion_to_meters
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    conversion = conversion_to_meters()
    rooms = [room.duplicate() for room in _rooms]  # duplicate the initial objects

    # assign the person_count_
    if len(person_count_) != 0:
        for i, room in enumerate(rooms):
            room.properties.energy.absolute_people(
                longest_list(person_count_, i), conversion)

    # assign the lighting_watts_
    if len(lighting_watts_) != 0:
        for i, room in enumerate(rooms):
            room.properties.energy.absolute_lighting(
                longest_list(lighting_watts_, i), conversion)

    # assign the electric_watts_
    if len(electric_watts_) != 0:
        for i, room in enumerate(rooms):
            room.properties.energy.absolute_electric_equipment(
                longest_list(electric_watts_, i), conversion)

    # assign the gas_watts_
    if len(gas_watts_) != 0:
        for i, room in enumerate(rooms):
            room.properties.energy.absolute_gas_equipment(
                longest_list(gas_watts_, i), conversion)

    # assign the hot_wtr_flow_
    if len(hot_wtr_flow_) != 0:
        for i, room in enumerate(rooms):
            room.properties.energy.absolute_service_hot_water(
                longest_list(hot_wtr_flow_, i), conversion)

    # assign the infiltration_ach_
    if len(infiltration_ach_) != 0:
        for i, room in enumerate(rooms):
            room.properties.energy.absolute_infiltration_ach(
                longest_list(infiltration_ach_, i), conversion)

    # assign the vent_flow_
    if len(vent_flow_) != 0:
        for i, room in enumerate(rooms):
            room.properties.energy.absolute_ventilation(longest_list(vent_flow_, i))
