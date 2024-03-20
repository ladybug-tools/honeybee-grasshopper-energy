# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Run Honeybee objects capable of generating electricity (such as Shades with PV
properties) through a quick energy simulation to obtain an estimate of
electricity production.
_
Note that this component only evaluates electricity production and not energy
consumption. Any number of Honeybee Rooms or other objects can be connected
but they will only be simulated as context shade that casts shadows on the
generator objects.
-

    Args:
        _hb_objs: An array of honeybee Rooms, Faces, Apertures, Doors or Shades to be
            included in the simulation of electricity production. This can also
            be an entire Model to be simulated. Any number of Honeybee Rooms or
            non-generating objects can be connected but they will only be
            simulated as context shade that casts shadows on the
            generator objects.
        _epw_file: Path to an .epw file on your system as a text string.
        _north_: A number between -360 and 360 for the counterclockwise difference
            between the North and the positive Y-axis in degrees.
            90 is West and 270 is East. (Default: 0).
        _inverter_eff_: A number between 0 and 1 for the load centers's inverter nominal
            rated DC-to-AC conversion efficiency. An inverter converts DC power,
            such as that output by photovoltaic panels, to AC power, such as
            that distributed by the electrical grid and is available from
            standard electrical outlets. Inverter efficiency is defined as the
            inverter's rated AC power output divided by its rated DC power
            output. (Default: 0.96).
        _dc_to_ac_size_: A positive number (typically greater than 1) for the ratio of the
            inverter's DC rated size to its AC rated size. Typically, inverters
            are not sized to convert the full DC output under standard test
            conditions (STC) as such conditions rarely occur in reality and
            therefore unnecessarily add to the size/cost of the inverter. For a
            system with a high DC to AC size ratio, during times when the 
            DC power output exceeds the inverter's rated DC input size, the inverter
            limits the array's power output by increasing the DC operating voltage,
            which moves the arrays operating point down its current-voltage (I-V)
            curve. The default value of 1.1 is reasonable for most systems. A
            typical range is 1.1 to 1.25, although some large-scale systems have
            ratios of as high as 1.5. The optimal value depends on the system's
            location, array orientation, and module cost. (Default: 1.1).
        _run: Set to "True" to run the simulation to obtain annual loads. This can
            also be the integer 2 to run the simulation while being able to see
            the simulation process (with a batch window).

    Returns:
        report: A report of the energy simulation run.
        total_ac: A number for the total on-site produced alternating current (AC)
            electricity in kWh.
        ac_power: A data collection of all on-site produced electricity (kWh). This
            represents the alternating current (AC) electricity coming out of
            the inverter that processes all on-site power production.
        generators: A list of names for each of the electricity generation objects that
            were found among the connected _hb_objs. These names align with the
            tota_dc output below as well as the dc_power data collections.
        total_dc: A list of numbers for the direct current (DC) electricity produced
            by each generator object in kWh.
        dc_power: A list of data collections for the direct current (DC) electricity
            produced by each on-site electricity generator (kWh). Each
            photovoltaic object will have a separate data collection.
"""

ghenv.Component.Name = 'HB Generation Loads'
ghenv.Component.NickName = 'GenLoads'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import os
import subprocess
import json
from collections import OrderedDict

try:
    from ladybug.futil import write_to_file_by_name, nukedir
    from ladybug.sql import SQLiteResult
    from ladybug.datacollection import HourlyContinuousCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.config import folders
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.simulation.parameter import SimulationParameter
    from honeybee_energy.run import run_idf
    from honeybee_energy.result.err import Err
    from honeybee_energy.writer import energyplus_idf_version
    from honeybee_energy.config import folders as energy_folders
    from honeybee_energy.lib.constructions import opaque_construction_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from lbt_recipes.version import check_energyplus_version
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_vector2d
    from ladybug_rhino.config import units_system, tolerance, angle_tolerance
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def serialize_data(data_dicts):
    """Reserialize a list of HourlyContinuousCollection dictionaries."""
    return [HourlyContinuousCollection.from_dict(data) for data in data_dicts]


# List of all the output strings that will be requested
ac_out = 'Facility Total Produced Electricity Energy'
dc_out = 'Generator Produced DC Electricity Energy'
energy_output = (ac_out, dc_out)


if all_required_inputs(ghenv.Component) and _run:
    # check the presence of energyplus and check that the version is compatible
    check_energyplus_version()

    # create the Model from the _hb_objs
    models = [obj.duplicate() for obj in _hb_objs if isinstance(obj, Model)]
    other_objs = [obj.duplicate() for obj in _hb_objs if not isinstance(obj, Model)]
    model = Model.from_objects('Generation_Loads', other_objs, units_system(),
                               tolerance, angle_tolerance)
    for m in models:
        model.add_model(m)
    model.rooms_to_orphaned()
    soil_constr = opaque_construction_by_identifier('Mud')
    model.properties.energy.generate_ground_room(soil_constr)

    # set the inverter efficiency and size
    if _inverter_eff_ is not None:
        model.properties.energy.electric_load_center.inverter_efficiency = _inverter_eff_
    if _dc_to_ac_size_ is not None:
        model.properties.energy.electric_load_center.inverter_dc_to_ac_size_ratio = _dc_to_ac_size_

    # process the simulation folder name and the directory
    directory = os.path.join(folders.default_simulation_folder, model.identifier)
    sch_directory = os.path.join(directory, 'schedules')
    nukedir(directory)  # delete any existing files in the directory

    # create simulation parameters for the coarsest/fastest E+ sim possible
    _sim_par_ = SimulationParameter()
    _sim_par_.timestep = 6
    _sim_par_.shadow_calculation.solar_distribution = 'FullExteriorWithReflections'
    _sim_par_.output.reporting_frequency = 'Hourly'
    _sim_par_.output.add_electricity_generation()
    _sim_par_.output.include_html = False
    _sim_par_.simulation_control.do_zone_sizing = False
    _sim_par_.simulation_control.do_system_sizing = False
    _sim_par_.simulation_control.do_plant_sizing = False

    # set the north if it is not defaulted
    if _north_ is not None:
        try:
            _sim_par_.north_vector = to_vector2d(_north_)
        except AttributeError:  # north angle instead of vector
            _sim_par_.north_angle = float(_north_)

    # create the strings for simulation paramters and model
    ver_str = energyplus_idf_version() if energy_folders.energyplus_version \
        is not None else energyplus_idf_version(compatibe_ep_version)
    sim_par_str = _sim_par_.to_idf()
    model_str = model.to.idf(
        model, schedule_directory=sch_directory, patch_missing_adjacencies=True)
    idf_str = '\n\n'.join([ver_str, sim_par_str, model_str])

    # write the final string into an IDF
    idf = os.path.join(directory, 'in.idf')
    write_to_file_by_name(directory, 'in.idf', idf_str, True)

    # run the IDF through EnergyPlus
    silent = True if _run == 1 else False
    sql, zsz, rdd, html, err = run_idf(idf, _epw_file, silent=silent)
    if sql is None and err is not None:  # something went wrong; parse the errors
        err_obj = Err(err)
        print(err_obj.file_contents)
        for error in err_obj.fatal_errors:
            raise Exception(error)

    # parse the result sql and get the monthly data collections
    if os.name == 'nt':  # we are on windows; use IronPython like usual
        sql_obj = SQLiteResult(sql)
        ac_power = sql_obj.data_collections_by_output_name(ac_out)
        dc_power = sql_obj.data_collections_by_output_name(dc_out)
    else:  # we are on Mac; sqlite3 module doesn't work in Mac IronPython
        # Execute the honybee CLI to obtain the results via CPython
        cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'result',
                'data-by-outputs', sql]
        for outp in energy_output:
            cmds.append('["{}"]'.format(outp))
        custom_env = os.environ.copy()
        custom_env['PYTHONHOME'] = ''
        process = subprocess.Popen(cmds, stdout=subprocess.PIPE, env=custom_env)
        stdout = process.communicate()
        data_coll_dicts = json.loads(stdout[0])
        ac_power = serialize_data(data_coll_dicts[0])
        dc_power = serialize_data(data_coll_dicts[1])

    # give a warning if no generators were found in the results
    if len(ac_power) == 0:
        msg = 'No electricity generation objects were found in the connected _hb_objs.\n' \
            'Try applying PV properties to some of the connected Shade geometries.'
        print(msg)
        give_warning(ghenv.Component, msg)

    # group the generator results by identifier
    dc_dict = OrderedDict()
    for g_data in dc_power:
        gen_id = g_data.header.metadata['System'].split('..')[0]
        g_data.header.metadata['System'] = gen_id
        try:
            dc_dict[gen_id] += g_data
        except KeyError:
            dc_dict[gen_id] = g_data

    # sum the results and ouput them
    total_ac = [acp.total for acp in ac_power]
    generators = list(dc_dict.keys())
    total_dc = [dcp.total for dcp in dc_dict.values()]
    dc_power = [dcp for dcp in dc_dict.values()]
