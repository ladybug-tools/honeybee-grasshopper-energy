# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Compute spatially-resolved Universal Thermal Climate Index (UTCI) and heat/cold
stress conditions an EPW and Honeybee model.
_
This recipe uses EnergyPlus to obtain longwave radiant temperatures and indoor air
temperatures. The outdoor air temperature and air speed are taken directly from
the EPW. A Radiance-based, enhanced 2-phase method is used for shortwave MRT
calculations, which uses an accurate direct sun calculation with precise solar
positions.
_
The energy properties of the model geometry are what determine the outcome of the
simulation, though the model's Radiance sensor grids are what determine where
the comfort mapping occurs.
-

    Args:
        _model: A Honeybee Model for which UTCI comfort will be mapped. Note that
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
        sensor_count_: Integer for the maximum number of sensor grid points per
            parallel execution. (Default: 200).
        _wind_speed_: A single number for meteorological wind speed in m/s or an hourly
            data collection of wind speeds that align with the input run_period_.
            This will be used for all indoor comfort evaluation. Note that the
            EPW wind speed will be used for any outdoor sensors. (Default: 0.5).
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
        _run: Set to True to run the recipe and get results.

    Returns:
        report: Reports, errors, warnings, etc.
        utci: A folder containing CSV maps of Universal Thermal Climate Index (UTCI)
            temperatures for each sensor grid at each time step of the analysis.
            This can be connected to the "HB Read Thermal Matrix" component to
            parse detailed results into Grasshopper. Values are in Celsius.
        condition: A folder containing CSV maps of comfort conditions for each sensor
            grid at each time step of the analysis. This can be connected to the
            "HB Read Thermal Matrix" component to parse detailed results into
            Grasshopper. Values are as follows.
                * -1 = unacceptably cold conditions
                *  0 = neutral (comfortable) conditions
                * +1 = unacceptably hot conditions
        category: A folder containing CSV maps of the heat/cold stress categories for
            each sensor grid at each time step of the analysis. This can be connected
            to the "HB Read Thermal Matrix" component to parse detailed results
            into Grasshopper. This can be used to understand not just whether
            conditions are acceptable but how uncomfortably hot or cold they
            are. Values indicate the following.
                * -5 = extreme cold stress
                * -4 = very strong cold stress
                * -3 = strong cold stress
                * -2 = moderate cold stress
                * -1 = slight cold stress
                *  0 = no thermal stress
                * +1 = slight heat stress
                * +2 = moderate heat stress
                * +3 = strong heat stress
                * +4 = very strong heat stress
                * +5 = extreme heat stress
        TCP: Lists of values between 0 and 100 for the Thermal Comfort Percent (TCP).
            These can be plugged into the "LB Spatial Heatmap" component along
            with meshes of the sensor grids to visualize spatial thermal comfort.
            TCP is the percentage of occupied time where thermal conditions are
            acceptable/comfortable. Occupied hours are determined from the
            occuppancy schedules of each room (any time where the occupancy
            schedule is >= 0.1 will be considered occupied). Outdoor sensors
            are considered occupied at all times. More custom TCP studies can
            be done by post-processing the condition results.
        HSP: Lists of values between 0 and 100 for the Heat Sensation Percent (HSP).
            These can be plugged into the "LB Spatial Heatmap" component along with
            meshes of the sensor grids to visualize uncomfortably hot locations.
            HSP is the percentage of occupied time where thermal conditions are
            hotter than what is considered acceptable/comfortable. Occupied hours
            are determined from the occuppancy schedules of each room (any time
            where the occupancy schedule is >= 0.1 will be considered occupied).
            Outdoor sensors are considered occupied at all times. More custom HSP
            studies can be done by post-processing the condition results.
        CSP: Lists of values between 0 and 100 for the Cold Sensation Percent (CSP).
            These can be plugged into the "LB Spatial Heatmap" component along with
            meshes of the sensor grids to visualize uncomfortably cold locations.
            CSP is the percentage of occupied time where thermal conditions are
            colder than what is considered acceptable/comfortable. Occupied hours
            are determined from the occuppancy schedules of each room (any time
            where the occupancy schedule is >= 0.1 will be considered occupied).
            Outdoor sensors are considered occupied at all times. More custom CSP
            studies can be done by post-processing the condition results.
"""

ghenv.Component.Name = 'HB UTCI Comfort Map'
ghenv.Component.NickName = 'UTCIMap'
ghenv.Component.Message = '1.2.2'
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
    recipe = Recipe('utci_comfort_map')
    recipe.input_value_by_name('model', _model)
    recipe.input_value_by_name('epw', _epw)
    recipe.input_value_by_name('ddy', _ddy)
    recipe.input_value_by_name('north', north_)
    recipe.input_value_by_name('run-period', run_period_)
    recipe.input_value_by_name('sensor-count', sensor_count_)
    recipe.input_value_by_name('wind-speed', _wind_speed_)
    recipe.input_value_by_name('solarcal-parameters', solar_body_par_)
    recipe.input_value_by_name('radiance-parameters', radiance_par_)

    # run the recipe
    project_folder = recipe.run(
        run_settings_, radiance_check=True, openstudio_check=True)

    # load the results
    utci = recipe_result(recipe.output_value_by_name('utci', project_folder))
    condition = recipe_result(recipe.output_value_by_name('condition', project_folder))
    category = recipe_result(recipe.output_value_by_name('category', project_folder))
    TCP = recipe_result(recipe.output_value_by_name('tcp', project_folder))
    HSP = recipe_result(recipe.output_value_by_name('hsp', project_folder))
    CSP = recipe_result(recipe.output_value_by_name('csp', project_folder))
