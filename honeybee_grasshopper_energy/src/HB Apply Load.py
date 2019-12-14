# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Apply load objects to Rooms. (eg. People, Lighting, Equipment, Infiltration,
Ventilation, Setpoint).
-

    Args:
        _rooms: Honeybee Rooms to which the input load objects should be assigned.
        people_: A People object to describe the occupancy of the rooms. If None,
            the people of the input rooms will not be changed.
        lighting_: A Lighting object to describe the lighting usage of the rooms.
            If None, the lighting of the input rooms will not be changed.
        electric_equip_: An ElectricEquipment object to describe the usage
            of electric equipment within the rooms. If None, the electric equipment
            of the rooms will not be changed.
        gas_equip_: A GasEquipment object to describe the usage of gas equipment
            within the rooms. If None, the gas equipment of the rooms will not
            be changed.
        infiltration_: An Infiltration object to describe the outdoor air leakage of
            the rooms. If None, the infiltration of the rooms will not be changed.
        ventilation_: A Ventilation object to describe the minimum outdoor air
            requirement of the rooms. If None, the ventilation of the rooms will
            not be changed.
        setpoint_: A Setpoint object to describe the temperature and humidity
            setpoints of the rooms.  If None, the setpoint of the rooms will
            not be changed.
    
    Returns:
        report: Reports, errors, warnings, etc.
        rooms: The input Rooms with their loads edited.
"""

ghenv.Component.Name = "HB Apply Load"
ghenv.Component.NickName = 'ApplyLoad'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "Energy"
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    rooms = [obj.duplicate() for obj in _rooms]
    
    # assign the people objects to the Room
    if people_ is not None:
        for room in rooms:
            room.properties.energy.people = people_
    
    # assign the lighting objects to the Room
    if lighting_ is not None:
        for room in rooms:
            room.properties.energy.lighting = lighting_
    
    # assign the electric_equipment objects to the Room
    if electric_equip_ is not None:
        for room in rooms:
            room.properties.energy.electric_equipment = electric_equip_
    
    # assign the gas_equipment objects to the Room
    if gas_equip_ is not None:
        for room in rooms:
            room.properties.energy.gas_equipment = gas_equip_
    
    # assign the infiltration objects to the Room
    if infiltration_ is not None:
        for room in rooms:
            room.properties.energy.infiltration = infiltration_
    
    # assign the ventilation objects to the Room
    if ventilation_ is not None:
        for room in rooms:
            room.properties.energy.ventilation = ventilation_
    
    # assign the setpoint objects to the Room
    if setpoint_ is not None:
        for room in rooms:
            room.properties.energy.setpoint = setpoint_
