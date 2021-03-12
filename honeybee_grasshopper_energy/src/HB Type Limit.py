# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Create a custom ScheduleTypeLimit object that can be assigned to any schedule object.
_
Schedule types exist for the sole purpose of validating schedule values against
upper/lower limits and assigning a data type and units to the schedule values.
As such, they are not necessary to run energy simulations but their use is
generally considered good practice.
-

    Args:
        _name: Text to set the name for the ScheduleTypeLimit. This should be
            unique to avoif conflcit with other schedule types.
        low_limit_: An optional number for the lower limit for values in the
            schedule. If None, there will be no lower limit.
        up_limit_: An optional number for the upper limit for values in the
            schedule. If None, there will be no upper limit.
        discrete_: Boolean to not whether the values of the schedule are continuous
            or discrete. The latter means that only integers are accepted as
            schedule values. Default: False for 'Continuous'.
        _unit_type_: Text for an EnergyPlus unit type, which will be used to assign
            units to the values in the schedule.  Note that this field is not used
            in the actual calculations of EnergyPlus. Default: 'Dimensionless'.
            Choose from the following:
                * Dimensionless
                * Temperature
                * DeltaTemperature
                * PrecipitationRate
                * Angle
                * ConvectionCoefficient
                * ActivityLevel
                * Velocity
                * Capacity
                * Power
                * Availability
                * Percent
                * Control
                * Mode
    
    Returns:
        report: Reports, errors, warnings, etc.
        type_limit: A ScheduleTypeLimit object that can be assigned to any schedule object.
"""

ghenv.Component.Name = "HB Type Limit"
ghenv.Component.NickName = 'TypeLimit'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '2 :: Schedules'
ghenv.Component.AdditionalHelpFromDocStrings = "0"


try:  # import the honeybee-energy dependencies
    from honeybee_energy.schedule.typelimit import ScheduleTypeLimit
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set default values
    numeric_type = 'Discrete' if discrete_ else 'Continuous'
    _unit_type_ = 'Dimensionless' if _unit_type_ is None else _unit_type_

    # create the ScheduleTypeLimit
    type_limit =  ScheduleTypeLimit(
        _name, low_limit_, up_limit_, numeric_type, _unit_type_)
