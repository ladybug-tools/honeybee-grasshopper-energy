# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Deconstruct a ProgramType object into its component load objects.
-

    Args:
        _program: A ProgramType object or text for the identifier of a ProgramType
            to be looked up in the program type library.
    
    Returns:
        people: A People object that describes the occupancy of the program. If None,
            no people are assumed to occupy the program.
        lighting: A Lighting object that describes the lighting usage of the program.
            If None, no lights are assumed to be installed.
        electric_equip: An ElectricEquipment object to describe the usage
            of electric equipment within the program. If None, no electric equipment
            is assumed to be installed.
        gas_equip: A GasEquipment object to describe the usage of gas equipment
            within the program. If None, no gas equipment is assumed to be installed.
        hot_water: A ServiceHotWater object to describe the usage of hot water within
            the program. If None, no hot water is be assumed for the program.
        infiltration: An Infiltration object to describe the outdoor air leakage of
            the program. If None, no infiltration is be assumed for the program.
        ventilation: A Ventilation object to describe the minimum outdoor air
            requirement of the program. If None, no ventilation requirement is
            be assumed for the program.
        setpoint: A Setpoint object to describe the temperature and humidity
            setpoints of the program.  If None, the ProgramType cannot be assigned
            to a Room that is conditioned.
"""

ghenv.Component.Name = "HB Deconstruct ProgramType"
ghenv.Component.NickName = 'DeconstrProgram'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:
    from honeybee_energy.lib.programtypes import program_type_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # get the program from the library if it is a identifier
    if isinstance(_program, str):
        _program = program_type_by_identifier(_program)

    # get the components of the program
    people = _program.people
    lighting = _program.lighting
    electric_equip = _program.electric_equipment
    gas_equip = _program.gas_equipment
    hot_water = _program.service_hot_water
    infiltration = _program.infiltration
    ventilation = _program.ventilation
    setpoint = _program.setpoint
