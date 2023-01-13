# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Compute spatially-resolved Universal Thermal Climate Index (UTCI) and heat/cold
stress conditions an EPW and Honeybee model.
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
longwave MRT at each sensor. For outdoor sensors, each sensor's sky view is multiplied
by the EPW sky temperature to account for longwave radiant exchange with the sky.
All outdoor context shades and the ground are assumed to be at the EPW air
temperature unless they have been modeled as Honeybee rooms.
_
A Radiance-based enhanced 2-phase method is used for all shortwave MRT calculations,
which precisely represents direct sun by tracing a ray from each sensor to the
solar position. To determine Thermal Comfort Percent (TCP), the occupancy schedules
of the energy model are used for indoor sensors if no schedule_ is input. Any
hour of the energy model occupancy schedule that is 0.1 or greater will be
considered occupied. If no schedule_ is input, all hours of the outdoors are
considered occupied.
-

    Args:
        _model: A Honeybee Model for which UTCI comfort will be mapped. Note that
            this model should have radiance grids assigned to it in order
            to produce meaningful results.
        _epw: Path to an EPW weather file to be used for the comfort map simulation.
        ddy_: Path to a DDY file with design days to be used for the initial sizing
            calculation of the energy simulation. Providing this input is important
            when there are conditioned Room geometries in the model, in which
            case the sizing of the building heating/cooling systems is important
            for modeling the heat exchange between indoors and outdoors.
            Otherwise, it can be ignored with little consequence for
            the simulation.
        north_: A number between -360 and 360 for the counterclockwise difference
            between the North and the positive Y-axis in degrees. This can
            also be Vector for the direction to North. (Default: 0).
        run_period_: An AnalysisPeriod to set the start and end dates of the simulation.
            If None, the simulation will be annual.
        _wind_speed_: A single number for meteorological wind speed in m/s or an hourly
            data collection of wind speeds that align with the input run_period_.
            This will be used for all outdoor comfort evaluation.
            _
            This can also be the path to a folder with csv files that align with
            the model sensor grids. Each csv file should have the same name as
            the sensor grid. Each csv file should contain a matrix of air speed
            values in m/s with one row per sensor and one column per timestep
            of the run period. Note that, when using this type of matrix input,
            these values are not meteorological and should be AT HUMAN SUBJECT LEVEL.
            _
            If unspecified, the EPW wind speed will be used for all outdoor sensors
            and all sensors on the indoors will use a wind speed of 0.5 m/s,
            which is the lowest acceptable value for the UTCI model.
        schedule_: A schedule to specify the relevant times during which comfort
            should be evaluated. This must either be a Ladybug Hourly Data
            Collection that aligns with the input run_period_ or the path to a
            CSV file with a number of rows equal to the length of the run_period_.
            If unspecified, it will be assumed that all times are relevant for
            outdoor sensors and the energy model occupancy schedules will be
            used for indoor sensors.
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
        env_conds: A folder containing CSV matrices with all of the environmental conditions
            that were input to the comfort model. These can be loaded into Grasshopper
            using the "HB Read Environment Matrix" component. This includes the following.
                * MRT
                * Air Temperature
                * Relative Humidity
                * Longwave MRT
                * Shortwave MRT Delta
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
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '7 :: Thermal Map'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import os

try:
    from lbt_recipes.recipe import Recipe
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import units_system
    from ladybug_rhino.grasshopper import all_required_inputs, recipe_result
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    # create the recipe and set the input arguments
    recipe = Recipe('utci_comfort_map')
    recipe.input_value_by_name('model', _model)
    recipe.input_value_by_name('epw', _epw)
    recipe.input_value_by_name('ddy', ddy_)
    recipe.input_value_by_name('north', north_)
    recipe.input_value_by_name('run-period', run_period_)
    if isinstance(_wind_speed_, str) and os.path.isdir(_wind_speed_):
        recipe.input_value_by_name('air-speed-matrices', _wind_speed_)
    else:
        recipe.input_value_by_name('wind-speed', _wind_speed_)
    recipe.input_value_by_name('schedule', schedule_)
    recipe.input_value_by_name('solarcal-parameters', solar_body_par_)
    recipe.input_value_by_name('radiance-parameters', radiance_par_)

    # perform an extra check for units because many people forget to check them
    if isinstance(_model, Model):
        check_model = _model
        if check_model.units != 'Meters':
            check_model = _model.duplicate()
            check_model.convert_to_units('Meters')
        # remove degenerate geometry within native E+ tolerance of 0.01 meters
        for room in check_model.rooms:
            try:
                room.remove_colinear_vertices_envelope(
                    tolerance=0.01, delete_degenerate=True)
            except AssertionError as e:  # room removed; likely wrong units
                error = 'Your Model units system is: {}. ' \
                    'Is this correct?\n{}'.format(_model.units, e)
                raise ValueError(error)

    # run the recipe
    silent = True if _run > 1 else False
    project_folder = recipe.run(
        run_settings_, radiance_check=True, openstudio_check=True, silent=silent)

    # load the results
    try:
        env_conds = recipe_result(recipe.output_value_by_name('environmental-conditions', project_folder))
        utci = recipe_result(recipe.output_value_by_name('utci', project_folder))
        condition = recipe_result(recipe.output_value_by_name('condition', project_folder))
        category = recipe_result(recipe.output_value_by_name('category', project_folder))
        TCP = recipe_result(recipe.output_value_by_name('tcp', project_folder))
        HSP = recipe_result(recipe.output_value_by_name('hsp', project_folder))
        CSP = recipe_result(recipe.output_value_by_name('csp', project_folder))
    except Exception:
        raise Exception(recipe.failure_message(project_folder))
