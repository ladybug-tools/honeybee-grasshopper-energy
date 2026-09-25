# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create an ExhaustAir object that can be used to create a ProgramType or be
assigned directly to a Room.
_
Note the the 2 ventilation types (flow_per_area and flow_per_fixture) are
ultimately added together to yield the final exhaust air flow rate used
in the simulation.
-

    Args:
        _name_: Text to set the name for the Ventilation and to be incorporated
            into a unique Ventilation identifier. If None, a unique name will
            be generated.
        _flow_per_area_: A numerical value for the intensity of exhaust air ventilation
            in m3/s per square meter of floor area. (Default: 0).
        _flow_per_fixture: A numerical value for the level of exhaust air ventilation
            in m3/s for each fixture in the room. The term "fixture" is used
            broadly as a way to reference a wide variety of contaminant sources
            such as toilets/urinals, shower heads, kitchen hoods, fume hoods,
            etc. (Default: 0). Typical values for different types of fixtures in
            ASHRAE 62.1 are as follows:
                * Private Toilet - 0.0236 m3/s
                * Public Toilet - 0.03304 m3/s
                * Locker Room Shower Head - 0.0236 m3/s
                * Residential Kitchen Hood - 0.04719 m3/s
                * Fume Hood - ~0.2832 m3/s (4' wide hood with 1.5' sash height)
        _fixture_count_: An integer for the number of fixtures in the room. This
            is multiplied by the _flow_per_fixture_, which is then added to the
            flow_per_area to yield the final exhaust air flow rate (Default: 1).
        _schedule_: An optional fractional schedule for the exhaust air ventilation over
            the course of the year. The type of this schedule should be
            Fractional and the fractional values get multiplied by
            the total design flow rate to yield a complete exhaust air profile.
            Values of 0 in the schedule will shut the exhaust fan off completely.
            If None, the design level of exhaust air will be used throughout
            all timesteps of the simulation, meaning that this schedule is
            Always On. (Default: None).
        _pressure_rise_: A number for the the pressure rise across the fan in Pascals
            (N/m2). This is often a function of the fan speed and the conditions in
            which the fan is operating. It plays an important role in determining
            the amount of energy consumed by the fan. Typical kitchen and bathroom
            exhaust fans have pressure rises around 125 Pa but, in healthcare
            settings where filters create more resistance, higher pressures
            around 250 Pa are more common. (Default: 125).
        _efficiency_: A number between 0 and 1 for the overall efficiency of the fan.
            Specifically, this is the ratio of the power delivered to the fluid
            to the electrical input power. It is the product of the fan motor
            efficiency and the fan impeller efficiency.
            Fans that have a higher blade diameter, no obstructions or filters,
            and operate at lower speeds with smaller pressure rises for
            their size tend to have higher efficiencies. Because motor efficiencies
            are typically between 0.8 and 0.9, the best overall fan efficiencies
            tend to be around 0.7 with most typical fan efficiencies between 0.5 and
            0.7. When filters are added, which is common for most exhaust fans,
            the total efficiency typically ends up between 0.3 and 0.4. (Default: 0.35).
        balance_sched_: An optional ScheduleRuleset or ScheduleFixedInterval
            for the fraction of exhaust air that is unbalanced by simple airflows,
            such as infiltration, natural ventilation, or zone mixing. Unbalanced
            exhaust is modeled as being provided by the outdoor air system in the
            central air system such that values of 1 in this schedule indicate
            all exhaust air balancing done by the mechanical system and values of 0
            indicate all air balanced by simple air flows. If None, then
            all the exhaust air flow is assumed to be unbalanced by simple
            airflows. The the flow rates at the zone return air node are reduced
            by the flow rate that is being exhausted and the zone outdoor air
            controller will ensure that the outdoor air flow rate is sufficient
            to serve the exhaust.

    Returns:
        exhaust: An Exhaust Air object that can be used to create a ProgramType or
            be assigned directly to a Room.
"""

ghenv.Component.Name = 'HB Exhaust Air'
ghenv.Component.NickName = 'Exhaust'
ghenv.Component.Message = '1.10.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.load.exhaust import ExhaustAir
    from honeybee_energy.lib.schedules import schedule_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import turn_off_old_tag
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
turn_off_old_tag(ghenv.Component)


# make a default Ventilation name if none is provided
name = clean_and_id_ep_string('ExhaustAir') if _name_ is None else \
    clean_ep_string(_name_)

# get the schedule
if isinstance(_schedule_, str):
    _schedule_ = schedule_by_identifier(_schedule_)
if isinstance(balance_sched_, str):
    balance_sched_ = schedule_by_identifier(balance_sched_)

# get default _flow_per_person_, _flow_per_area_, and _ach_
_flow_per_area_ = _flow_per_area_ if _flow_per_area_ is not None else 0.0
_flow_per_fixture_ = _flow_per_fixture_ if _flow_per_fixture_ is not None else 0.0
_fixture_count_ = _fixture_count_ if _fixture_count_ is not None else 1
_pressure_rise_ = 125 if _pressure_rise_ is None else _pressure_rise_
_efficiency_ = 0.35 if _efficiency_ is None else _efficiency_

# create the Ventilation object
exhaust = ExhaustAir(
    name, _flow_per_area_, _flow_per_fixture_, _fixture_count_,
    _schedule_, _pressure_rise_, _efficiency_, balance_sched_
)
if _name_ is not None:
    exhaust.display_name = _name_
