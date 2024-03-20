# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Apply values for setpoints to a Room or ProgramType.
-

    Args:
        _room_or_program: Honeybee Rooms or ProgramType objects to which the input
            setpoints should be assigned. This can also be the identifier of a
            ProgramType to be looked up in the program type library. This can
            also be a Honeybee Model for which all Rooms will be assigned
            the setpoints.
        cooling_setpt_: A numerical value for a single constant temperature for
            the cooling setpoint [C].
        heating_setpt_: A numerical value for a single constant temperature for
            the heating setpoint [C].
        humid_setpt_: A numerical value for a single constant value for the
            humidifying setpoint [%].
        dehumid_setpt_: A numerical value for a single constant value for the
            dehumidifying setpoint [%].
        cutout_difference_: An optional positive number for the temperature difference between the
            cutout temperature and the setpoint temperature. Specifying a non-zero
            number here is useful for modeling the throttling range associated
            with a given setup of setpoint controls and HVAC equipment. Throttling
            ranges describe the range where a zone is slightly over-cooled or
            over-heated beyond the thermostat setpoint. They are used to avoid
            situations where HVAC systems turn on only to turn off a few minutes later,
            thereby wearing out the parts of mechanical systems faster. They can
            have a minor impact on energy consumption and can often have significant
            impacts on occupant thermal comfort, though using the default value
            of zero will often yield results that are close enough when trying
            to estimate the annual heating/cooling energy use. Specifying a value
            of zero effectively assumes that the system will turn on whenever
            conditions are outside the setpoint range and will cut out as soon
            as the setpoint is reached. (Default: 0).

    Returns:
        report: Reports, errors, warnings, etc.
        mod_obj: The input Rooms or ProgramTypes with their setpoint values edited.
"""

ghenv.Component.Name = "HB Apply Setpoint Values"
ghenv.Component.NickName = 'ApplySetpointVals'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

import uuid

try:
    from honeybee.model import Model
    from honeybee.room import Room
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.load.setpoint import Setpoint
    from honeybee_energy.schedule.ruleset import ScheduleRuleset
    import honeybee_energy.lib.scheduletypelimits as _type_lib
    from honeybee_energy.lib.programtypes import program_type_by_identifier, \
        building_program_type_by_identifier
    from honeybee_energy.programtype import ProgramType
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))
try:
    from ladybug_rhino.grasshopper import all_required_inputs, longest_list
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def dup_setpoint(hb_obj):
    """Duplicate a setpoint object assigned to a Room or ProgramType."""
    # try to get the setpoint object assgined to the Room or ProgramType
    try:  # assume it's a Room
        setpt_obj = hb_obj.properties.energy.setpoint
    except AttributeError:  # it's a ProgramType
        setpt_obj = hb_obj.setpoint

    load_id = '{}_Setpoint'.format(hb_obj.identifier)
    try:  # duplicate the setpoint object
        dup_load = setpt_obj.duplicate()
        dup_load.identifier = load_id
        return dup_load
    except AttributeError:  # create a new object if it does not exist
        heat_sch = ScheduleRuleset.from_constant_value(
            '{}_HtgSetp'.format(hb_obj.identifier), -50, _type_lib.temperature)
        cool_sch = ScheduleRuleset.from_constant_value(
            '{}_ClgSetp'.format(hb_obj.identifier), 50, _type_lib.temperature)
        return Setpoint(load_id, heat_sch, cool_sch)


def assign_setpoint(hb_obj, setpt_obj):
    """Assign a setpoint object to a Room or a ProgramType."""
    try:  # assume it's a Room
        hb_obj.properties.energy.setpoint = setpt_obj
    except AttributeError:  # it's a ProgramType
        hb_obj.setpoint = setpt_obj


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

    # assign the cooling_setpt_
    if len(cooling_setpt_) != 0:
        for i, obj in enumerate(edit_objs):
            setpoint = dup_setpoint(obj)
            setpoint.cooling_setpoint = longest_list(cooling_setpt_, i)
            assign_setpoint(obj, setpoint)

    # assign the heating_setpt_
    if len(heating_setpt_) != 0:
        for i, obj in enumerate(edit_objs):
            setpoint = dup_setpoint(obj)
            setpoint.heating_setpoint = longest_list(heating_setpt_, i)
            assign_setpoint(obj, setpoint)

    # assign the humid_setpt_
    if len(humid_setpt_) != 0:
        for i, obj in enumerate(edit_objs):
            setpoint = dup_setpoint(obj)
            setpoint.humidifying_setpoint = longest_list(humid_setpt_, i)
            assign_setpoint(obj, setpoint)

    # assign the dehumid_setpt_
    if len(dehumid_setpt_) != 0:
        for i, obj in enumerate(edit_objs):
            setpoint = dup_setpoint(obj)
            setpoint.dehumidifying_setpoint = longest_list(dehumid_setpt_, i)
            assign_setpoint(obj, setpoint)

    # assign the cutout_difference_
    if len(cutout_difference_) != 0:
        for i, obj in enumerate(edit_objs):
            setpoint = dup_setpoint(obj)
            setpoint.setpoint_cutout_difference = longest_list(cutout_difference_, i)
            assign_setpoint(obj, setpoint)
