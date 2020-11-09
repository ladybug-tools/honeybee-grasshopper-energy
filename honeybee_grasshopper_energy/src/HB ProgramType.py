# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a ProgramType object possessing all schedules and loads defining a program.
ProgramTypes can be assigned to Honeybee Rooms to specify all default schedules
and loads on the Room.
-

    Args:
        _name: Text to set the name for the ProgramType and to be incorporated
            into a unique ProgramType identifier.
        base_program_: An optional ProgramType object that will be used as the
            starting point for the new ProgramType output from this component.
            This can also be text for the name of a ProgramType within the library
            such as that output from the "HB Search Program Types" component.
            If None, a Plenum program type will be used as the base with no loads,
            setpoints, or ventilation requirements assigned.
        _people_: A People object to describe the occupancy of the program. If None,
            no occupancy will be assumed for the program. Default: None.
        _lighting_: A Lighting object to describe the lighting usage of the program.
            If None, no lighting will be assumed for the program. Default: None.
        _electric_equip_: An ElectricEquipment object to describe the usage
            of electric equipment within the program. If None, no electric equipment
            will be assumed for the program. Default: None.
        _gas_equip_: A GasEquipment object to describe the usage of gas equipment
            within the program. If None, no gas equipment will be assumed for
            the program. Default: None.
        _infiltration_: An Infiltration object to describe the outdoor air leakage of
            the program. If None, no infiltration will be assumed for the program.
            Default: None.
        _ventilation_: A Ventilation object to describe the minimum outdoor air
            requirement of the program. If None, no ventilation requirement will
            be assumed for the program. Default: None
        _setpoint_: A Setpoint object to describe the temperature and humidity
            setpoints of the program.  If None, the ProgramType cannot be assigned
            to a Room that is conditioned. Default: None.
    
    Returns:
        program: A ProgramType object that can be assigned to Honeybee Rooms in
            order to specify all default schedules and loads on the Room.
"""

ghenv.Component.Name = "HB ProgramType"
ghenv.Component.NickName = 'ProgramType'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.programtype import ProgramType
    from honeybee_energy.lib.programtypes import program_type_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # get the base program type
    if base_program_ is None:
        program = ProgramType(clean_and_id_ep_string(_name))
        program.display_name = _name
    else:
        if isinstance(base_program_, str):
            base_program_ = program_type_by_identifier(base_program_)
        program = base_program_.duplicate()
        program.identifier = clean_and_id_ep_string(_name)
        program.display_name = _name
    
    # go through each input load and assign it to the set
    if _people_ is not None:
        program.people = _people_
    if _lighting_ is not None:
        program.lighting = _lighting_
    if _electric_equip_ is not None:
        program.electric_equipment = _electric_equip_
    if _gas_equip_ is not None:
        program.gas_equipment = _gas_equip_
    if _infiltration_ is not None:
        program.infiltration = _infiltration_
    if _ventilation_ is not None:
        program.ventilation = _ventilation_
    if _setpoint_ is not None:
        program.setpoint = _setpoint_
