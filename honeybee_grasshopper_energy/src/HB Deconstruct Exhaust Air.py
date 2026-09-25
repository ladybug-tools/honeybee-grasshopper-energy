# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Deconstruct a ExhaustAir object into its constituient properties.
_
Note the the 2 exhaust air  types (flow_per_area and flow_per_fixture) are
ultimately added together to yield the final exhaust air flow rate used
in the simulation.
-

    Args:
        _exhaust: An ExhaustAir object to be deconstructed.
    
    Returns:
        name: Text string for the exhaust air display name.
        flow_per_area: A numerical value for the intensity of exhaust air ventilation
            in m3/s per square meter of floor area.
        flow_per_fixture: A numerical value for the level of exhaust air ventilation
            in m3/s for each fixture in the room. The term "fixture" is used
            broadly as a way to reference a wide variety of contaminant sources
            such as toilets/urinals, shower heads, kitchen hoods, fume hoods, etc.
        fixture_count: An integer for the number of fixtures in the room. This
            is multiplied by the _flow_per_fixture_, which is then added to the
            flow_per_area to yield the final exhaust air flow rate (Default: 1).
        schedule: A fractional schedule for the exhaust air ventilation over
            the course of the year. The schedule values get multiplied by
            the total design flow rate to yield a complete exhaust air profile.
            Values of 0 in the schedule shut the exhaust fan off completely.
        pressure_rise: A number for the the pressure rise across the fan in Pascals
            (N/m2). This is often a function of the fan speed and the conditions in
            which the fan is operating. It plays an important role in determining
            the amount of energy consumed by the fan. Typical kitchen and bathroom
            exhaust fans have pressure rises around 125 Pa but, in healthcare
            settings where filters create more resistance, higher pressures
            around 250 Pa are more common.
        efficiency: A number between 0 and 1 for the overall efficiency of the fan.
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
        balance_sched: A schedule for the fraction of exhaust air that is unbalanced by simple airflows,
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
"""

ghenv.Component.Name = 'HB Deconstruct Exhaust Air'
ghenv.Component.NickName = 'DecnstrExhaustAir'
ghenv.Component.Message = '1.10.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from honeybee_energy.load.exhaust import ExhaustAir
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # check the input
    assert isinstance(_exhaust, ExhaustAir), \
        'Expected ExhaustAir object. Got {}.'.format(type(_exhaust))

    # get the properties of the object
    name = _exhaust.display_name
    flow_per_area = _exhaust.flow_per_area
    flow_per_fixture = _exhaust.flow_per_fixture
    fixture_count = _exhaust.fixture_count
    schedule = _exhaust.schedule
    pressure_rise = _exhaust.pressure_rise
    efficiency = _exhaust.efficiency
    balance_sched = _exhaust.balancing_schedule
