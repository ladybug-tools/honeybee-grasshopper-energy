# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Create a schedule from lists of daily values for each day of the week.
-

    Args:
        _sun: A list of 24 values that represent the schedule values at each
            hour of Sunday. This can also be a single constant value for the
            whole day.
        _mon: A list of 24 values that represent the schedule values at each
            hour of Monday. This can also be a single constant value for the
            whole day.
        _tue: A list of 24 values that represent the schedule values at each
            hour of Tuesday. This can also be a single constant value for the
            whole day.
        _wed: A list of 24 values that represent the schedule values at each
            hour of Wednesday. This can also be a single constant value for the
            whole day.
        _thu: A list of 24 values that represent the schedule values at each
            hour of Thursday. This can also be a single constant value for the
            whole day.
        _fri: A list of 24 values that represent the schedule values at each
            hour of Friday. This can also be a single constant value for the
            whole day.
        _sat: A list of 24 values that represent the schedule values at each
            hour of Saturday. This can also be a single constant value for the
            whole day.
        _holiday_: An optional list of 24 values that represent the schedule
            values at each hour of holidays. This can also be a single constant
            value for the whole day. If no values are input here, the schedule
            for Sunday will be used for all holidays.
        _summer_des_: An optional list of 24 values that represent the schedule
            values at each hour of the summer design day. This can also be a
            single constant value for the whole day. If None, the daily
            schedule with the highest average value will be used unless
            the _type_limit_ is Temperature, in which case it will be
            the daily schedule with the lowest average value.
        _winter_des_: An optional list of 24 values that represent the schedule
            values at each hour of the summer design day. This can also be a
            single constant value for the whole day. If None, the daily
            schedule with the lowest average value will be used unless
            the _type_limit_ is Temperature, in which case it will be
            the daily schedule with the highest average value.
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
        idf_year: Text string for the EnergyPlus ScheduleYear that will ultimately
            be written into the IDF for simulation. This can also be used to add
            the schedule to the schedule library that is loaded up upon the start
            of Honeybee by copying this text into the honeybee/library/schedules/
            user_library.idf file along with the other idf text outputs.
        idf_week: Text string for the EnergyPlus ScheduleWeek that will ultimately
            be written into the IDF for simulation. This can also be used to add
            the schedule to the schedule library that is loaded up upon the start
            of Honeybee by copying this text into the honeybee/library/schedules/
            user_library.idf file along with the other idf text outputs.
        idf_days: Text strings for the EnergyPlus SchedulDays that will ultimately
            be written into the IDF for simulation. This can also be used to add
            the schedule to the schedule library that is loaded up upon the start
            of Honeybee by copying this text into the honeybee/library/schedules/
            user_library.idf file along with the other idf text outputs.
"""

ghenv.Component.Name = 'HB Weekly Schedule'
ghenv.Component.NickName = 'WeeklySchedule'
ghenv.Component.Message = '1.6.0'
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


def check_sched_values(values):
    """Check that input schedules are valid and format them to all be 24 values."""
    if len(values) == 24:
        return values
    elif len(values) == 1:
        return values * 24
    else:
        raise ValueError(
            'Schedule values must be either 24 or 1. Not {}.'.format(len(values)))


if all_required_inputs(ghenv.Component):
    # process any lists of single values such that they are all 24
    _sun = check_sched_values(_sun)
    _mon = check_sched_values(_mon)
    _tue = check_sched_values(_tue)
    _wed = check_sched_values(_wed)
    _thu = check_sched_values(_thu)
    _fri = check_sched_values(_fri)
    _sat = check_sched_values(_sat)
    _holiday_ = _sun if len(_holiday_) == 0 else check_sched_values(_holiday_)
    _summer_des_ = None if len(_summer_des_) == 0 else check_sched_values(_summer_des_)
    _winter_des_ = None if len(_winter_des_) == 0 else check_sched_values(_winter_des_)

    # get the ScheduleTypeLimit object
    if _type_limit_ is None:
        _type_limit_ = schedule_type_limit_by_identifier('Fractional')
    elif isinstance(_type_limit_, str):
        _type_limit_ = schedule_type_limit_by_identifier(_type_limit_)

    # create the schedule object
    name = clean_and_id_ep_string('WeeklySchedule') if _name_ is None else \
        clean_ep_string(_name_)
    schedule = ScheduleRuleset.from_week_daily_values(
        name, _sun, _mon, _tue, _wed, _thu, _fri, _sat, _holiday_,
        timestep=1, schedule_type_limit=_type_limit_,
        summer_designday_values=_summer_des_, winter_designday_values=_winter_des_)
    if _name_ is not None:
        schedule.display_name = _name_

    # get the idf strings of the schedule
    idf_year, idf_week = schedule.to_idf()
    idf_days = [day_sch.to_idf(_type_limit_) for day_sch in schedule.day_schedules]
