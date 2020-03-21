# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
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
            Default - 'Total'. Choose from the following:
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
        summary_reports_: An optional list of EnergyPlus summary report names as strings.
            If None, only the 'AllSummary' report will be requested from the simulation
            and no HTML report will be generated. If any value is input here, an HTML
            report will be requested and the summary report written into it.
            See the Input Output Reference SummaryReports section for a full
            list of all reports that can be requested. https://bigladdersoftware.com/
            epx/docs/9-1/input-output-reference/output-table-summaryreports.html
    
    Returns:
        sim_output: A SimulationOutput object that can be connected to the
            "HB Simulation Parameter" component in order to specify which
            types of outputs should be written from EnergyPlus.
"""

ghenv.Component.Name = "HB Simulation Output"
ghenv.Component.NickName = 'SimOutput'
ghenv.Component.Message = '0.1.2'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    from honeybee_energy.simulation.output import SimulationOutput
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))


# set default reporting frequency.
_report_frequency_ = _report_frequency_.title() \
    if _report_frequency_ is not None else 'Hourly'

# set the inclusion of HTML based on whether summary reports are requested.
_html = False if len(summary_reports_) == 0 else True

# set the default load_type
load_type_ = load_type_.title() if load_type_ is not None else 'All'

# create the starting simulation output object.
sim_output = SimulationOutput(outputs=None,
                              reporting_frequency=_report_frequency_,
                              include_sqlite=True,
                              include_html=_html,
                              summary_reports=summary_reports_)

# ensure that we always include AllSummary in the reports; it's used in result parsing
sim_output.add_summary_report('AllSummary')

# set each of the requested outputs
if zone_energy_use_:
    sim_output.add_zone_energy_use(load_type_)
if gains_and_losses_:
    load_type = load_type_ if load_type_ != 'All' else 'Total'
    sim_output.add_gains_and_losses(load_type)
if comfort_metrics_:
    sim_output.add_comfort_metrics()
if surface_temperature_:
    sim_output.add_surface_temperature()
if surface_energy_flow_:
    sim_output.add_surface_energy_flow()
