# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Apply values for specific setpoints to Rooms.
-

    Args:
        _rooms: Honeybee Rooms to which the input load objects should be assigned.
        cooling_setpt_: A numerical value for a single constant temperature for
            the cooling setpoint [C].
        heating_setpt_: A numerical value for a single constant temperature for
            the heating setpoint [C].
        humid_setpt_: A numerical value for a single constant value for the
            humidifying setpoint [%].
        dehumid_setpt_: A numerical value for a single constant value for the
            dehumidifying setpoint [%].
    
    Returns:
        report: Reports, errors, warnings, etc.
        rooms: The input Rooms with their setpoint values edited.
"""

ghenv.Component.Name = "HB Apply Setpoint Values"
ghenv.Component.NickName = 'ApplySetpointVals'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "Energy"
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    from honeybee_energy.load.setpoint import Setpoint
    from honeybee_energy.schedule.ruleset import ScheduleRuleset
    import honeybee_energy.lib.scheduletypelimits as _type_lib
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))
try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    rooms = [obj.duplicate() for obj in _rooms]
    
    # assign the cooling_setpt_
    if cooling_setpt_ is not None:
        for room in rooms:
            try:
                setpoint = room.properties.energy.setpoint.duplicate()
                setpoint.cooling_setpoint = cooling_setpt_
            except AttributeError:
                heat_sch = ScheduleRuleset.from_constant_value(
                    '{}_HtgSetp'.format(self.name), -50, _type_lib.temperature)
                cool_sch = ScheduleRuleset.from_constant_value(
                    '{}_ClgSetp'.format(self.name), cooling_setpt_, _type_lib.temperature)
                setpoint = Setpoint('{}_Setpoint'.format(room.name), heat_sch, cool_sch)
            room.properties.energy.setpoint = setpoint
    
    # assign the heating_setpt_
    if heating_setpt_ is not None:
        for room in rooms:
            try:
                setpoint = room.properties.energy.setpoint.duplicate()
                setpoint.heating_setpoint = heating_setpt_
            except AttributeError:
                heat_sch = ScheduleRuleset.from_constant_value(
                    '{}_HtgSetp'.format(self.name), heating_setpt_, _type_lib.temperature)
                cool_sch = ScheduleRuleset.from_constant_value(
                    '{}_ClgSetp'.format(self.name), 50, _type_lib.temperature)
                setpoint = Setpoint('{}_Setpoint'.format(room.name), heat_sch, cool_sch)
            room.properties.energy.setpoint = setpoint
    
    # assign the humid_setpt_
    if humid_setpt_ is not None:
        for room in rooms:
            try:
                setpoint = room.properties.energy.setpoint.duplicate()
                setpoint.humidifying_setpoint = humid_setpt_
                room.properties.energy.setpoint = setpoint
            except AttributeError:
                raise ValueError('Humidifying setpoint cannot be assigned without'
                                 ' a cooling or heating setpoint.')
    
    # assign the dehumid_setpt_
    if dehumid_setpt_ is not None:
        for room in rooms:
            try:
                setpoint = room.properties.energy.setpoint.duplicate()
                setpoint.dehumidifying_setpoint = dehumid_setpt_
                room.properties.energy.setpoint = setpoint
            except AttributeError:
                raise ValueError('Dehumidifying setpoint cannot be assigned without'
                                 ' a cooling or heating setpoint.')
