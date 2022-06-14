# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Create a schedule from a single constant value or a list of 24 hourly values
repeating continuously over every day of the year.
-

    Args:
        _values: A list of 24 values that represent the schedule values at each
            hour of the day. This can also be a single constant value for the
            whole day.
        _name_: Text to set the name for the Schedule and to be incorporated
            into a unique Schedule identifier.
        _type_limit_: A text string from the identifier of the ScheduleTypeLimit to
            be looked up in the schedule type limit library. This can also be a
            custom ScheduleTypeLimit object from the "HB Type Limit" component.
            The input here will be used to validate schedule values against
            upper/lower limits and assign units to the schedule values. Default:
            "Fractional" for values that range continuously between 0 and 1.
            Choose from the following built-in options:
                * Fractional
                * On-Off
                * Temperature
                * Activity Level
                * Power
                * Humidity
                * Angle
                * Delta Temperature
                * Control Level

    Returns:
        report: Reports, errors, warnings, etc.
        schedule: A ScheduleRuleset object that can be assigned to a Room, a Load
            object, or a ProgramType object.
        idf_text: Text strings for the EnergyPlus Schedule that will ultimately
            be written into the IDF for simulation. This can also be used to add
            the schedule to the schedule library that is loaded up upon the start
            of Honeybee by copying this text into the honeybee/library/schedules/
            user_library.idf file.
"""

ghenv.Component.Name = 'HB Constant Schedule'
ghenv.Component.NickName = 'ConstantSchedule'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '2 :: Schedules'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.schedule.ruleset import ScheduleRuleset
    from honeybee_energy.lib.scheduletypelimits import schedule_type_limit_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # get the ScheduleTypeLimit object
    if _type_limit_ is None:
        _type_limit_ = schedule_type_limit_by_identifier('Fractional')
    elif isinstance(_type_limit_, str):
        _type_limit_ = schedule_type_limit_by_identifier(_type_limit_)

    # create the schedule object
    name = clean_and_id_ep_string('ConstantSchedule') if _name_ is None else \
        clean_ep_string(_name_)
    if len(_values) == 1:
        schedule = ScheduleRuleset.from_constant_value(name, _values[0], _type_limit_)
        idf_text, constant_none = schedule.to_idf()
    else:
        schedule = ScheduleRuleset.from_daily_values(name, _values, timestep=1,
            schedule_type_limit=_type_limit_)
        idf_year, idf_week = schedule.to_idf()
        idf_days = [day_sch.to_idf(_type_limit_) for day_sch in schedule.day_schedules]
        idf_text = [idf_year] + idf_week + idf_days if idf_week is not None \
            else idf_year
    if _name_ is not None:
        schedule.display_name = _name_
