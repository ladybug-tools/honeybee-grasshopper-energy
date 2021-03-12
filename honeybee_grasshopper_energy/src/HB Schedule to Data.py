# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Get a ladybug DataCollection representing this schedule at a given timestep.
_
This DataCollection can be used to visualize timeseries schedule values over
the entire period of a simulation using a component like the "LB Hourly Plot".
_
This DataCollection can also be used in the crafting of conditional statements
with the ladybug components. For example, making a psychrometric chart of zone
temperature/humidity for only the hours that the occupancy schedule is above a
certain threshold.
-

    Args:
        _schedule: A ScheduleRuleSet or SchedileFixedInterval for which a DataCollection
            of timeseries schedule values will be produced. This can also be the
            identifier of a Schedule to be looked up in the schedule library.
        analysis_period_: An optional AnalysisPeriod to set the start and end datetimes
            of the resulting DataCollection. The timestep of this AnalysisPeriod
            will also be used to determine the timestep of the resulting DataCollection.
        _week_start_day_: An optional text string to set the start day of the week
            of the schedule timeseries data. Default: Sunday. Choose from the following:
                * Sunday
                * Monday
                * Tuesday
                * Wednesday
                * Thursday
                * Friday
                * Saturday
        holidays_: An optional list of strings (eq: 25 Dec) to represent the holidays
            in the resulting timeseries. Holiday schedules will be used for these
            dates in the resulting timeseries.
    
    Returns:
        data: A ladybug DataCollection representing the timeseries values of the schedule.
            This can be used to visualize timeseries schedule values over the entire
            period of a simulation using a component like the "LB Hourly Plot".
"""

ghenv.Component.Name = "HB Schedule to Data"
ghenv.Component.NickName = 'SchToData'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '2 :: Schedules'
ghenv.Component.AdditionalHelpFromDocStrings = "2"


try:  # import the honeybee-energy dependencies
    from honeybee_energy.schedule.ruleset import ScheduleRuleset
    from honeybee_energy.lib.schedules import schedule_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import the ladybug dependencies
    from ladybug.dt import Date, DateTime
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # get the schedue from the library if it's a string
    if isinstance(_schedule, str):
        _schedule = schedule_by_identifier(_schedule)

    # process the _week_start_day_
    week_start_day = 'Sunday' if _week_start_day_ is None else _week_start_day_.title()

    # process the analysis period if it is input
    if analysis_period_ is not None:
        start_date = analysis_period_.st_time.date
        end_date = analysis_period_.end_time.date
        timestep = analysis_period_.timestep
    else:
        start_date, end_date, timestep = Date(1, 1), Date(12, 31), 1

    # process the holidays_ if they are input
    holidays = None
    if len(holidays_) != 0 and holidays_[0] is not None:
        try:
            holidays = tuple(Date.from_date_string(hol) for hol in holidays_)
        except ValueError:
            holidays = tuple(DateTime.from_date_time_string(hol).date for hol in holidays_)

    # create the DataCollection
    if isinstance(_schedule, ScheduleRuleset):
        data = _schedule.data_collection(
            timestep, start_date, end_date, week_start_day, holidays, leap_year=False)
    else:  # assume that it is a ScheduleFixedInterval
        data = _schedule.data_collection_at_timestep(timestep, start_date, end_date)

    # if there are hour inputs on the analysis_period_, apply it to the data
    if analysis_period_ is not None and \
            (analysis_period_.st_hour != 0 or analysis_period_.end_hour != 23):
        data = data.filter_by_analysis_period(analysis_period_)
