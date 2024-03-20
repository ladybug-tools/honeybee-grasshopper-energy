# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a custom simulation output object by plugging in one or more names of
EnergyPlus simulation ouputs.
The resulting object can be used to request output variables from EnergyPlus.
-

    Args:
        base_sim_output_: An optional simulation output object to serve as the
            starting point for the sim_output object returned by this component.
            All of the output names will simply be appended to this initial
            starting object.
        output_names_: A list of EnergyPlus output names as strings (eg.
            'Surface Window System Solar Transmittance'. These outputs will be
            requested from the simulation.
        _report_frequency_: Text for the frequency at which the outputs
                are reported. Default: 'Hourly'.
                Choose from the following:
                    * Annual
                    * Monthly
                    * Daily
                    * Hourly
                    * Timestep
        summary_reports_: An optional list of EnergyPlus summary report names as strings.
            If None, only the 'AllSummary' report will be requested from the
            simulation and will appear in the HTML report output by EnergyPlus.
            See the Input Output Reference SummaryReports section for a full
            list of all reports that can be requested. https://bigladdersoftware.com/
            epx/docs/9-1/input-output-reference/output-table-summaryreports.html
        _unmet_setpt_tol_: A number in degrees Celsius for the difference that the zone
            conditions must be from the thermostat setpoint in order
            for the setpoint to be considered unmet. This will affect how unmet
            hours are reported in the output. ASHRAE 90.1 uses a tolerance of
            1.11C, which is equivalent to 1.8F. (Default: 1.11C).

    Returns:
        sim_output: A SimulationOutput object that can be connected to the
            "HB Simulation Parameter" component in order to specify which
            types of outputs should be written from EnergyPlus.
"""

ghenv.Component.Name = 'HB Custom Simulation Output'
ghenv.Component.NickName = 'CustomOutput'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from honeybee_energy.simulation.output import SimulationOutput
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import turn_off_old_tag
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
turn_off_old_tag(ghenv.Component)


# set the starting sim_output
sim_output = base_sim_output_.duplicate() if base_sim_output_ is not None \
    else SimulationOutput()

# set reporting frequency
if _report_frequency_ is not None:
    sim_output.reporting_frequency = _report_frequency_.title()

# add the _output names
for output_name in output_names_:
    sim_output.add_output(output_name)

# add the summary_reports_
for rep in summary_reports_:
    sim_output.add_summary_report(rep)

# add the unmet setpoint tolerance
if _unmet_setpt_tol_ is not None:
    sim_output.unmet_setpoint_tolerance = _unmet_setpt_tol_
