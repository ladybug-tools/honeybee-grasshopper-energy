# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a simulation output object by selecting sets of commonly-requested output variables.
The resulting object can be used to request output variables from EnergyPlus.
-

    Args:
        zone_energy_use_: Set to True to add outputs for zone energy use when ideal
            air systems are assigned. This includes, ideal air heating + cooling,
            lighting, electric + gas equipment, and fan electric energy.
        hvac_energy_use_: Set to True to add outputs for HVAC energy use from detailed
            systems. This includes outputs for different pieces of equipment,
            which together catch all energy-consuming parts of a system.
            (eg. chillers, boilers, coils, humidifiers, fans, pumps).
        gains_and_losses_: Set to True to Add outputs for zone gains and losses.
            This includes such as people gains, solar gains, infiltration losses/gains,
            and ventilation losses/gains.
        comfort_metrics_: Set to True to add outputs for zone thermal comfort analysis.
            This includes air temperature, mean radiant temperature, relative
            humidity.
        surface_temperature_: Set to True to add outputs for indoor and outdoor
            surface temperature.
        surface_energy_flow_: Set to True to add outputs for energy flow across
            all surfaces.
        load_type_: An optional text value to set the type of load outputs requested.
            Default - 'All'. Choose from the following:
                * All - all energy use including heat lost from the zone
                * Total - the total load added to the zone (both sensible and latent)
                * Sensible - the sensible load added to the zone
                * Latent - the latent load added to the zone
        _report_frequency_: Text for the frequency at which the outputs
                are reported. Default: 'Hourly'.
                Choose from the following:
                    * Annual
                    * Monthly
                    * Daily
                    * Hourly
                    * Timestep
    
    Returns:
        sim_output: A SimulationOutput object that can be connected to the
            "HB Simulation Parameter" component in order to specify which
            types of outputs should be written from EnergyPlus.
"""

ghenv.Component.Name = 'HB Simulation Output'
ghenv.Component.NickName = 'SimOutput'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from honeybee_energy.simulation.output import SimulationOutput
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))


# set default reporting frequency.
_report_frequency_ = _report_frequency_.title() \
    if _report_frequency_ is not None else 'Hourly'

# set the default load_type
load_type_ = load_type_.title() if load_type_ is not None else 'All'

# create the starting simulation output object.
sim_output = SimulationOutput(reporting_frequency=_report_frequency_)

# set each of the requested outputs
if zone_energy_use_:
    sim_output.add_zone_energy_use(load_type_)
if hvac_energy_use_:
    sim_output.add_hvac_energy_use()
if gains_and_losses_:
    load_type = load_type_ if load_type_ != 'All' else 'Total'
    sim_output.add_gains_and_losses(load_type)
if comfort_metrics_:
    sim_output.add_comfort_metrics()
if surface_temperature_:
    sim_output.add_surface_temperature()
if surface_energy_flow_:
    sim_output.add_surface_energy_flow()
