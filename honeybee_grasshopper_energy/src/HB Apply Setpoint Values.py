# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Apply values for setpoints to a Room or ProgramType.
-

    Args:
        _room_or_program: Honeybee Rooms or ProgramType objects to which the input
            setpoints should be assigned. This can also be the name of a
            ProgramType to be looked up in the program type library.
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
        mod_obj: The input Rooms or ProgramTypes with their setpoint values edited.
"""

ghenv.Component.Name = "HB Apply Setpoint Values"
ghenv.Component.NickName = 'ApplySetpointVals'
ghenv.Component.Message = '0.2.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    from honeybee.room import Room
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.load.setpoint import Setpoint
    from honeybee_energy.schedule.ruleset import ScheduleRuleset
    import honeybee_energy.lib.scheduletypelimits as _type_lib
    from honeybee_energy.lib.programtypes import program_type_by_name
    from honeybee_energy.programtype import ProgramType
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))
try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def dup_setpoint(hb_obj):
    """Duplicate a setpoint object assigned to a Room or ProgramType."""
    # try to get the setpoint object assgined to the Room or ProgramType
    try:  # assume it's a Room
        setpt_obj = hb_obj.properties.energy.setpoint
    except AttributeError:  # it's a ProgramType
        setpt_obj = hb_obj.setpoint
    
    try:  # duplicate the setpoint object
        return setpt_obj.duplicate()
    except AttributeError:  # create a new object if it does not exist
        heat_sch = ScheduleRuleset.from_constant_value(
            '{}_HtgSetp'.format(hb_obj.name), -50, _type_lib.temperature)
        cool_sch = ScheduleRuleset.from_constant_value(
            '{}_ClgSetp'.format(hb_obj.name), 50, _type_lib.temperature)
        return Setpoint('{}_Setpoint'.format(hb_obj.name), heat_sch, cool_sch)


def assign_setpoint(hb_obj, setpt_obj):
    """Assign a setpoint object to a Room or a ProgramType."""
    try:  # assume it's a Room
        hb_obj.properties.energy.setpoint = setpt_obj
    except AttributeError:  # it's a ProgramType
        hb_obj.setpoint = setpt_obj


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    mod_obj = []
    for obj in _room_or_program:
        if isinstance(obj, (Room, ProgramType)):
            mod_obj.append(obj.duplicate())
        elif isinstance(obj, str):
            program = program_type_by_name(obj)
            mod_obj.append(program.duplicate())
        else:
            raise TypeError('Expected Honeybee Room or ProgramType. '
                            'Got {}.'.format(type(obj)))
    
    # assign the cooling_setpt_
    if cooling_setpt_ is not None:
        for obj in mod_obj:
            setpoint = dup_setpoint(obj)
            setpoint.cooling_setpoint = cooling_setpt_
            assign_setpoint(obj, setpoint)
    
    # assign the heating_setpt_
    if heating_setpt_ is not None:
        for obj in mod_obj:
            setpoint = dup_setpoint(obj)
            setpoint.heating_setpoint = heating_setpt_
            assign_setpoint(obj, setpoint)
    
    # assign the humid_setpt_
    if humid_setpt_ is not None:
        for obj in mod_obj:
            setpoint = dup_setpoint(obj)
            setpoint.humidifying_setpoint = humid_setpt_
            assign_setpoint(obj, setpoint)
    
    # assign the dehumid_setpt_
    if dehumid_setpt_ is not None:
        for obj in mod_obj:
            setpoint = dup_setpoint(obj)
            setpoint.dehumidifying_setpoint = dehumid_setpt_
            assign_setpoint(obj, setpoint)
