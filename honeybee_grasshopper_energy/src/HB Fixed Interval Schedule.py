# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Create a schedule defined by a list of values at a fixed interval or timestep
running over the entirety of the simulation period.
-

    Args:
        _values: A list of timeseries values occuring at a fixed timestep over
            the entire simulation. Typically, this should be a list of 8760
            values for each hour of the year but it can be a shorter list if
            you don't plan on using the schedule in an annual simulation. In
            this case, the analysis_period_ should probably be different than
            the default. This list can also have a length much greater than
            8760 if a timestep greater than 1 is used.
        _timestep_: An integer for the number of steps per hour that the input
            values correspond to.  For example, if each value represents 30
            minutes, the timestep is 2. For 15 minutes, it is 4. Default is 1,
            meaning each value represents a single hour. Must be one of the
            following: (1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60).
        analysis_period_: A ladybug AnalysisPeriod object to note when the input
            values take effect. Default is for the whole year. Note that this
            default usually should not be changed unless you plan to run a
            simulation that is much shorter than a year.
        _name: Text to set the name for the Schedule and to be incorporated
            into a unique Schedule identifier.
        _type_limit_: A text string from the name of the ScheduleTypeLimit to
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
    
    Returns:
        report: Reports, errors, warnings, etc.
        schedule: A ScheduleRuleset object that can be assigned to a Room, a Load
            object, or a ProgramType object.
"""

ghenv.Component.Name = "HB Fixed Interval Schedule"
ghenv.Component.NickName = 'FixedIntervalSchedule'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '2 :: Schedules'
ghenv.Component.AdditionalHelpFromDocStrings = "4"

try:  # import the ladybug dependencies
    from ladybug.dt import Date
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.schedule.fixedinterval import ScheduleFixedInterval
    from honeybee_energy.lib.scheduletypelimits import schedule_type_limit_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set the defaults
    _timestep_ = 1 if _timestep_ is None else _timestep_
    start_date = Date(1, 1) if analysis_period_ is None else \
        analysis_period_.st_time.date

    # get the ScheduleTypeLimit object
    if _type_limit_ is None:
        _type_limit_ = schedule_type_limit_by_identifier('Fractional')
    elif isinstance(_type_limit_, str):
        _type_limit_ = schedule_type_limit_by_identifier(_type_limit_)

    # create the schedule object
    schedule = ScheduleFixedInterval(
        clean_and_id_ep_string(_name), _values, _type_limit_, _timestep_, start_date,
        placeholder_value=0, interpolate=False)
    schedule.display_name = _name
