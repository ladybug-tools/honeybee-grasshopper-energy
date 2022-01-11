# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Compute spatially-resolved operative temperature and Adaptive thermal comfort from
a Honeybee model.
_
This recipe uses EnergyPlus to obtain surface temperatures and indoor air
temperatures + humidities. Outdoor air temperatures, relative humidities, and
air speeds are taken directly from the EPW. The energy properties of the model
geometry are what determine the outcome of the simulation, though the model's
Radiance sensor grids are what determine where the comfort mapping occurs.
_
Longwave radiant temperatures are obtained by computing spherical view factors
from each sensor to the Room surfaces of the model using Radiance. These view factors
are then multiplied by the surface temperatures output by EnergyPlus to yield
longwave MRT at each sensor. All indoor shades (eg. those representing furniture)
are assumed to be at the room-average MRT.
_
A Radiance-based enhanced 2-phase method is used for all shortwave MRT calculations,
which precisely represents direct sun by tracing a ray from each sensor to the
solar position. To determine Thermal Comfort Percent (TCP), the occupancy schedules
of the energy model are used. Any hour of the occupancy schedule that is 0.1 or
greater will be considered occupied. All hours of the outdoors are considered occupied.
-

    Args:
        _model: A Honeybee Model for which adaptive comfort will be mapped. Note that
            this model should have radiance grids assigned to it in order
            to produce meaningful results.
        _epw: Path to an EPW weather file to be used for the comfort map simulation.
        _ddy: Path to a DDY file with design days to be used for the initial sizing
            calculation of the energy simulation.
        north_: A number between -360 and 360 for the counterclockwise difference
            between the North and the positive Y-axis in degrees. This can
            also be Vector for the direction to North. (Default: 0).
        run_period_: An AnalysisPeriod to set the start and end dates of the simulation.
            If None, the simulation will be annual.
        _air_speed_: A single number for air speed in m/s or an hourly data collection
            of air speeds that align with the input run_period_. This will be
            used for all indoor comfort evaluation. Note that the EPW wind speed
            will be used for any outdoor sensors. (Default: 0.1).
        comfort_par_: Optional comfort parameters from the "LB Adaptive Comfort Parameters"
            component to specify the criteria under which conditions are
            considered acceptable/comfortable. The default will use ASHRAE-55
            adaptive comfort criteria.
        solar_body_par_: Optional solar body parameters from the "LB Solar Body Parameters"
            object to specify the properties of the human geometry assumed in the
            shortwave MRT calculation. The default assumes average skin/clothing
            absorptivity and a human subject always has their back to the sun
            at a 45-degree angle (SHARP = 135).
        radiance_par_: Text for the radiance parameters to be used for ray
            tracing. (Default: -ab 2 -ad 5000 -lw 2e-05).
        run_settings_: Settings from the "HB Recipe Settings" component that specify
            how the recipe should be run. This can also be a text string of
            recipe settings.
        _run: Set to True to run the recipe and get results. This input can also be
            the integer "2" to run the recipe silently.

    Returns:
        report: Reports, errors, warnings, etc.
        op_temp: A folder containing CSV maps of Operative Temperature for each sensor
            grid at each time step of the analysis. This can be connected to the
            "HB Read Thermal Matrix" component to parse detailed results into
            Grasshopper. Values are in Celsius.
        condition: A folder containing CSV maps of comfort conditions for each sensor
            grid at each time step of the analysis. This can be connected to the
            "HB Read Thermal Matrix" component to parse detailed results into
            Grasshopper. Values are as follows.
                * -1 = unacceptably cold conditions
                *  0 = neutral (comfortable) conditions
                * +1 = unacceptably hot conditions
        deg_neut: A folder containing CSV maps of the degrees Celsius from the adaptive
            comfort neutral temperature for each sensor grid at each time step of
            the analysis. This can be connected to the "HB Read Thermal Matrix"
            component to parse detailed results into Grasshopper. This can be
            used to understand not just whether conditions are acceptable but
            how uncomfortably hot or cold they are.
        TCP: Lists of values between 0 and 100 for the Thermal Comfort Percent (TCP).
            These can be plugged into the "LB Spatial Heatmap" component along
            with meshes of the sensor grids to visualize spatial thermal comfort.
            TCP is the percentage of occupied time where thermal conditions are
            acceptable/comfortable. Occupied hours are determined from the
            occupancy schedules of each room (any time where the occupancy
            schedule is >= 0.1 will be considered occupied). Outdoor sensors
            are considered occupied at all times. More custom TCP studies can
            be done by post-processing the condition results.
        HSP: Lists of values between 0 and 100 for the Heat Sensation Percent (HSP).
            These can be plugged into the "LB Spatial Heatmap" component along with
            meshes of the sensor grids to visualize uncomfortably hot locations.
            HSP is the percentage of occupied time where thermal conditions are
            hotter than what is considered acceptable/comfortable. Occupied hours
            are determined from the occupancy schedules of each room (any time
            where the occupancy schedule is >= 0.1 will be considered occupied).
            Outdoor sensors are considered occupied at all times. More custom HSP
            studies can be done by post-processing the condition results.
        CSP: Lists of values between 0 and 100 for the Cold Sensation Percent (CSP).
            These can be plugged into the "LB Spatial Heatmap" component along with
            meshes of the sensor grids to visualize uncomfortably cold locations.
            CSP is the percentage of occupied time where thermal conditions are
            colder than what is considered acceptable/comfortable. Occupied hours
            are determined from the occupancy schedules of each room (any time
            where the occupancy schedule is >= 0.1 will be considered occupied).
            Outdoor sensors are considered occupied at all times. More custom CSP
            studies can be done by post-processing the condition results.
"""

ghenv.Component.Name = 'HB Adaptive Comfort Map'
ghenv.Component.NickName = 'AdaptiveMap'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '7 :: Thermal Map'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:
    from lbt_recipes.recipe import Recipe
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, recipe_result
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    # create the recipe and set the input arguments
    recipe = Recipe('adaptive_comfort_map')
    recipe.input_value_by_name('model', _model)
    recipe.input_value_by_name('epw', _epw)
    recipe.input_value_by_name('ddy', _ddy)
    recipe.input_value_by_name('north', north_)
    recipe.input_value_by_name('run-period', run_period_)
    recipe.input_value_by_name('air-speed', _air_speed_)
    recipe.input_value_by_name('comfort-parameters', comfort_par_)
    recipe.input_value_by_name('solarcal-parameters', solar_body_par_)
    recipe.input_value_by_name('radiance-parameters', radiance_par_)

    # run the recipe
    silent = True if _run > 1 else False
    project_folder = recipe.run(
        run_settings_, radiance_check=True, openstudio_check=True, silent=silent)

    # load the results
    try:
        op_temp = recipe_result(recipe.output_value_by_name('temperature', project_folder))
        condition = recipe_result(recipe.output_value_by_name('condition', project_folder))
        deg_neut = recipe_result(recipe.output_value_by_name('degrees-from-neutral', project_folder))
        TCP = recipe_result(recipe.output_value_by_name('tcp', project_folder))
        HSP = recipe_result(recipe.output_value_by_name('hsp', project_folder))
        CSP = recipe_result(recipe.output_value_by_name('csp', project_folder))
    except Exception:
        raise Exception(recipe.failure_message(project_folder))
