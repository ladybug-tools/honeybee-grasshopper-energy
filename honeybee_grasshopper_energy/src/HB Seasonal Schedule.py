# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Create a schedule using from other ScheduleRulesets and AnalysisPeriods over which
each schedule should be applied.
-

    Args:
        _base_schedule: A ScheduleRuleset that represents the base schedule on
            top of which the other _season_scheds will be applied. This can also
            be text to look up a ScheduleRuleset in the schedule library. Any time
            period that is not covered by the input _analysis_periods will default
            to this schedule. Furthermore, the summer and winter design day schedules
            will be taken from this schedule as well as the ScheduleTypeLimits.
        _season_scheds: A list of ScheduleRulesets that align with the _analysis_periods
            below and represent the schedules that will be applied over the
            _base_schedule for the duration of the respective AnalysisPeriod.
            This can also be text to look up ScheduleRulesets in the schedule
            library.
        _analysis_periods: A list of AnalysusPeriod objects that align with the
            _season_scheds and represent the time periods over which each season
            schedule should be applied. Note that, if these AnalysisPeriods
            overlap with one another, then the schedules that come later in
            this list will overwrite those that come earlier in the list for
            the duration of the overlapping time period.
        _name_: Text to set the name for the Schedule and to be incorporated
            into a unique Schedule identifier.

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

ghenv.Component.Name = "HB Seasonal Schedule"
ghenv.Component.NickName = 'SeasonalSchedule'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '2 :: Schedules'
ghenv.Component.AdditionalHelpFromDocStrings = "4"

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.schedule.ruleset import ScheduleRuleset
    from honeybee_energy.lib.schedules import schedule_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # check that the input _season_scheds align with the _analysis_periods
    assert len(_season_scheds) == len(_analysis_periods), \
        'Length of the _season_scheds list must match that of the _analysis_periods.' \
        '\n{} does not equal {}'.format(len(_season_scheds), len(_analysis_periods))

    # start by duplicating the base schedule
    name = clean_and_id_ep_string('SeasonalSchedule') if _name_ is None else \
        clean_ep_string(_name_)
    if isinstance(_base_schedule, str):
        _base_schedule = schedule_by_identifier(_base_schedule)
    schedule = _base_schedule.duplicate()
    schedule.identifier = name
    if _name_ is not None:
        schedule.display_name = _name_

    # translate the _season_scheds to individual Rules and apply them to the base
    for season_sch, a_period in zip(_season_scheds, _analysis_periods):
        if isinstance(season_sch, str):
            season_sch = schedule_by_identifier(season_sch)
        season_rules = season_sch.to_rules(
            a_period.st_time.date, a_period.end_time.date)
        for rule in reversed(season_rules):  # preserve priority order of rules
            schedule.add_rule(rule)

    # get the idf strings of the schedule
    idf_year, idf_week = schedule.to_idf()
    idf_days = [day_sch.to_idf(schedule.schedule_type_limit)
                for day_sch in schedule.day_schedules]
