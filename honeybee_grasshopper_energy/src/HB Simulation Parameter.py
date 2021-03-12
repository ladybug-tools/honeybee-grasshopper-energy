# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a simulation parameter object that carries a complete set of EnergyPlus
simulation settings and can be plugged into the "HB Model To OSM" component.
-

    Args:
        _north_: A number between -360 and 360 for the counterclockwise
            difference between the North and the positive Y-axis in degrees.
            90 is West and 270 is East. Note that this is different than the
            convention used in EnergyPlus, which uses clockwise difference
            instead of counterclockwise difference. This can also be Vector
            for the direction to North. (Default: 0)
        _output_: A SimulationOutput that lists the desired outputs from the
            simulation and the format in which to report them. This can be
            created using the "HB Simulation Output" component. Default is to
            request zone energy use at an hourly timestep.
        _run_period_: A ladybyg AnalysisPeriod object to describe the time period
            over which to run the simulation. the default is to run the simulation
            for the whole year.
        daylight_saving_: An optional ladybug AnalysisPeriod object to describe
            start and end of daylight savings time in the simulation. If None, no
            daylight savings time will be applied to the simulation.
        holidays_: A list of Ladybug Date objects for the holidays within the
            simulation. These should be in the format of 'DD Month' (eg. '1 Jan',
            '25 Dec'). If None, no holidays are applied. Default: None.
        _start_dow_: Text for the day of the week on which the simulation
            starts. Default: 'Sunday'. Choose from the following:
                * Sunday
                * Monday
                * Tuesday
                * Wednesday
                * Thursday
                * Friday
                * Saturday
        _timestep_: An integer for the number of timesteps per hour at which the
            calculation will be run. Default: 6. The following values are acceptable:
            (1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60)
        _terrain_: Text for the terrain type in which the model sits, used to determine
            the wind profile. Default: 'City'. Choose from: 
                * Ocean
                * Country
                * Suburbs
                * Urban
                * City
        _sim_control_: A SimulationControl object that describes which types
            of calculations to run. This can be generated from the "HB
            Simulation Control" component. Default: perform a sizing calculation
            but only run the simulation for the RunPeriod.
        _shadow_calc_: A ShadowCalculation object describing settings for the
            EnergyPlus Shadow Calculation. This can be generated from the "HB
            Shadow Calculation" component. Default: Average over 30 days with
            FullExteriorWithReflections.
        _sizing_: A SizingParameter object with criteria for sizing the heating
            and cooling system.  This can be generated from the "HB Sizing
            Parameter" component.

    Returns:
        sim_par: A SimulationParameter object that can be connected to the
            "HB Model To IDF" component in order to specify EnergyPlus
            simulation settings
"""

ghenv.Component.Name = 'HB Simulation Parameter'
ghenv.Component.NickName = 'SimPar'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from ladybug.dt import Date, DateTime
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee_energy.simulation.output import SimulationOutput
    from honeybee_energy.simulation.runperiod import RunPeriod
    from honeybee_energy.simulation.daylightsaving import DaylightSavingTime
    from honeybee_energy.simulation.parameter import SimulationParameter
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.togeometry import to_vector2d
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


# set default simulation outputs
if _output_ is None:
    _output_ = SimulationOutput()
    _output_.add_zone_energy_use()
    _output_.add_hvac_energy_use()

# set default simulation run period
_run_period_ = RunPeriod.from_analysis_period(_run_period_) \
    if _run_period_ is not None else RunPeriod()

# set the daylight savings if it is input
if daylight_saving_ is not None:
    daylight_saving = DaylightSavingTime.from_analysis_period(daylight_saving_)
    _run_period_.daylight_saving_time = daylight_saving

# set the holidays if requested.
if len(holidays_) != 0:
    try:
        dates = tuple(Date.from_date_string(date) for date in holidays_)
    except ValueError:
        dates = tuple(DateTime.from_date_time_string(date).date for date in holidays_)
    _run_period_.holidays = dates

# set the start day of the week if it is input
if _start_dow_ is not None:
    _run_period_.start_day_of_week = _start_dow_.title()

# set the default timestep
_timestep_ = _timestep_ if _timestep_ is not None else 6

# set the default timestep
_terrain_ = _terrain_.title() if _terrain_ is not None else 'City'

# return final simulation parameters
sim_par = SimulationParameter(output=_output_,
                              run_period=_run_period_,
                              timestep=_timestep_,
                              simulation_control=_sim_control_,
                              shadow_calculation=_shadow_calc_,
                              sizing_parameter=_sizing_,
                              terrain_type=_terrain_)

# set the north if it is not defaulted
if _north_ is not None:
    try:
        sim_par.north_vector = to_vector2d(_north_)
    except AttributeError:  # north angle instead of vector
        sim_par.north_angle = float(_north_)
