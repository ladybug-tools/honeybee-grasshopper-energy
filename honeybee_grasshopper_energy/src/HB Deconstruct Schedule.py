# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Deconstruct a ScheduleRuleset into an array of day-long ladybug DataCollections
representing each unique ScheduleDay that defines the ScheduleRuleset.
_
These DataCollections can be used to make visualizations of timeseries schedule
values over each unique day of the schedule using a component like the
"LB Line Chart".
-

    Args:
        _schedule: A ScheduleRuleSet to be deconstructed into DataCollections
            of timeseries schedule values for each unique day. This can also
            be the identifier of a Schedule to be looked up in the schedule library.
        _timestep_: An integer for the number of steps per hour at which to make
            the resulting daily DataCollections.
    
    Returns:
        day_names: A list of display names for each unique ScheduleDay that
            defines the input ScheduleRuleset.
        day_data: A list of day-long ladybug DataCollections representing each
            unique ScheduleDay that defines the ScheduleRuleset. These can be
            used to make visualizations of timeseries schedule values over each
            day of the schedule using a component like the "LB Line Chart".
        type_limit: The ScheduleTypeLimit object assigned to the ScheduleRuleset.
"""

ghenv.Component.Name = "HB Deconstruct Schedule"
ghenv.Component.NickName = 'DeconstrSch'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '2 :: Schedules'
ghenv.Component.AdditionalHelpFromDocStrings = "2"


try:  # import the honeybee-energy dependencies
    from honeybee_energy.schedule.ruleset import ScheduleRuleset
    from honeybee_energy.lib.schedules import schedule_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))
try:  # import the ladybug dependencies
    from ladybug.dt import Date
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
    
    # process the timestep
    _timestep_ = 1 if _timestep_ is None else _timestep_
    st_date = Date(1, 1)
    type_limit = _schedule.schedule_type_limit
    
    # process the default ScheduleDay
    default = _schedule.default_day_schedule.data_collection(
        st_date, type_limit, _timestep_)
    default.header.metadata['applied'] = 'default'
    
    # create the ScheduleDay DataCollections
    day_names = [_schedule.default_day_schedule.display_name]
    day_data = [default]
    for rule in _schedule.schedule_rules:
        data_col = rule.schedule_day.data_collection(
            st_date, type_limit, _timestep_)
        meta_str = ', '.join(rule.days_applied) + \
            ' | {} to {}'.format(rule.start_date, rule.end_date)
        data_col.header.metadata['applied'] = meta_str
        day_names.append(rule.schedule_day.display_name)
        day_data.append(data_col)
    
    # process the design day schedules
    if _schedule.summer_designday_schedule is not None:
        summer = _schedule.summer_designday_schedule.data_collection(
            st_date, type_limit, _timestep_)
        summer.header.metadata['applied'] = 'summer design'
        day_names.append(_schedule.summer_designday_schedule.display_name)
        day_data.append(summer)
    if _schedule.winter_designday_schedule is not None:
        winter = _schedule.winter_designday_schedule.data_collection(
            st_date, type_limit, _timestep_)
        winter.header.metadata['applied'] = 'winter design'
        day_names.append(_schedule.winter_designday_schedule.display_name)
        day_data.append(winter)
