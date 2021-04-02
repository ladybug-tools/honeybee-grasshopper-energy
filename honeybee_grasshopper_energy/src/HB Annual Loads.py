# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Run Honeybee Rooms through a quick energy simulation to obtain an estimate of
annual heating, cooling, lighting, equipment, and service hot water loads.
_
Note that the default settings used by this component are only suitable for evaluating
annual loads in the case where an error of up to 5% is acceptable. Also
note that annual loads are not the same as annual energy use or utility costs
and, while the "cop" inputs can be used to approximate some effects of real
heating + cooling systems, any evaulation of actual energy use, utility costs,
or GHG emissions should be done by modeling a detailed HVAC using the "HB
Model to OSM" component.
-

    Args:
        _rooms: A list of Honeybee Rooms for which annual loads will be computed.
        shades_: An optional list of Honeybee Shades that can block the sun to
            the input _rooms.
        _epw_file: Path to an .epw file on your system as a text string.
        _timestep_: An integer for the number of timesteps per hour at which the
            energy balance calculation will be run. This has a dramatic
            impact on the speed of the simulation and the accuracy of
            results. Higher timesteps lead to longer simulations and
            more accurate results. At the lowest aceptable timestep of 1,
            the results can have an error up to 5% but increasing the
            timestep to 4 should drop errors to below 1%. (Default: 1).
            The following values are acceptable:
            (1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60)
        _cool_cop_: An optional number which the cooling load will be divided by to
            account for the relative importance of cooling loads compared
            to heating loads (aka. the Coefficient of Performance or COP).
            For most cooling systems, this is value greater than 1, though
            how much greater varies widely between cooling systems and it is
            ultimately a function of how close the temperature of the cooling
            system's heat sink is to the room temperature setpoints. If set to 1,
            the output cooling will be the energy that must be removed from the
            _rooms to meet the setpoint (aka. the cooling demand). (Default: 1).
        _heat_cop_: An optional number which the heating load will be divided by to
            account for the relative importance of heating loads compared
            to cooling loads (aka. the Coefficient of Performance or COP).
            For fuel-based systems like gas boilers, this value tends to be
            less than 1 in order to represent the efficiency of the boiler
            and account for losses of heat, such as that through flue gases.
            For certain electric systems like heat pumps, this can be a value
            greater than 1 as such pumps may be able to pump more heat energy
            into a room per unit of electricity consumed. If set to 1, the
            output will be the energy that must be added to the _rooms to meet
            the setpoint (aka. the heating demand). (Default: 1).
        run_bal_: Set to True to have the full load balance computed after the
            simulation is run. This ensures that data collections for various
            terms of the load balance are output from the "balance".
            This can help explain why the loads are what they are but can
            also increase the component run time. (Default: False).
        _run: Set to "True" to run the simulation to obtain annual loads. This can
            also be the integer 2 to run the simulation while being able to see
            the simulation process (with a batch window).

    Returns:
        report: A report of the energy simulation run.
        total_load: A list of numbers for the 4-5 output load terms normalized by the floor
             area of the input _rooms. Units are kWh/m2. They are ordered
            as follows.
            _
            * cooling
            * heating
            * lighting
            * electric equipment
            * gas equipment (if the input rooms have it)
            * service hot water (if the input rooms have it)
        cooling: A monthly Data Collection for the cooling load intensity in kWh/m2.
        heating: A monthly Data Collection for the heating load intensity in kWh/m2.
        lighting: A monthly Data Collection for the lighting load intensity in kWh/m2.
        equip: A monthly Data Collection for the equipment load intensity in kWh/m2.
            Typically, this is only the load from electric equipment but, if
            the attached _rooms have gas equipment, this will be a list of two
            data collections for electric and gas equipment respectively.
        hot_water: A monthly Data Collection for the service hot water load intensity
            in kWh/m2.
        balance: A list of monthly data collections for the various terms of the
            floor-normalized load balance in kWh/m2. Will be None unless
            run_bal_ is set to True.
"""

ghenv.Component.Name = 'HB Annual Loads'
ghenv.Component.NickName = 'AnnualLoads'
ghenv.Component.Message = '1.2.1'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import os
import subprocess
import json

try:
    from ladybug.futil import write_to_file_by_name, nukedir
    from ladybug.epw import EPW
    from ladybug.sql import SQLiteResult
    from ladybug.datacollection import MonthlyCollection
    from ladybug.header import Header
    from ladybug.analysisperiod import AnalysisPeriod
    from ladybug.datatype.energyintensity import EnergyIntensity
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.config import folders
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.result.loadbalance import LoadBalance
    from honeybee_energy.simulation.parameter import SimulationParameter
    from honeybee_energy.run import run_idf
    from honeybee_energy.result.err import Err
    from honeybee_energy.writer import energyplus_idf_version
    from honeybee_energy.config import folders as energy_folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from lbt_recipes.version import check_energyplus_version
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import conversion_to_meters, tolerance, angle_tolerance
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def check_window_vent(rooms):
    """Check a rooms to make sure there's no opening of windows as coarse timestep."""
    for room in rooms:
        if room.properties.energy.window_vent_control is not None:
            msg = 'Window ventilation was detected but your timestep is too low ' \
                'to model window opening correctly.\nIt is recommended that you ' \
                'increase your timestep to at least 4 to get loads for this case.'
            print msg
            give_warning(ghenv.Component, msg)


def data_to_load_intensity(data_colls, floor_area, data_type, cop=1):
    """Convert data collections output by EnergyPlus to a single load intensity collection.

    Args:
        data_colls: A list of monthly data collections for an energy term.
        floor_area: The total floor area of the rooms, used to compute EUI.
        data_type: Text for the data type of the collections (eg. "Cooling").
        cop: Optional number for the COP, which the results will be divided by.
    """
    if len(data_colls) != 0:
        total_vals = [sum(month_vals) / floor_area for month_vals in zip(*data_colls)]
        if cop != 1:
            total_vals = [val / cop for val in total_vals]
    else:  # just make a "filler" collection of 0 values
        total_vals = [0] * 12
    meta_dat = {'type': data_type}
    total_head = Header(EnergyIntensity(), 'kWh/m2', AnalysisPeriod(), meta_dat)
    return MonthlyCollection(total_head, total_vals, range(12))


def serialize_data(data_dicts):
    """Reserialize a list of MonthlyCollection dictionaries."""
    return [MonthlyCollection.from_dict(data) for data in data_dicts]


# List of all the output strings that will be requested
cool_out = 'Zone Ideal Loads Supply Air Total Cooling Energy'
heat_out = 'Zone Ideal Loads Supply Air Total Heating Energy'
light_out = 'Zone Lights Electricity Energy'
el_equip_out = 'Zone Electric Equipment Electricity Energy'
gas_equip_out = 'Zone Gas Equipment NaturalGas Energy'
shw_out = 'Water Use Equipment Heating Energy'
gl_el_equip_out = 'Zone Electric Equipment Total Heating Energy'
gl_gas_equip_out = 'Zone Gas Equipment Total Heating Energy'
gl1_shw_out = 'Water Use Equipment Zone Sensible Heat Gain Energy'
gl2_shw_out = 'Water Use Equipment Zone Latent Gain Energy'
energy_output = (cool_out, heat_out, light_out, el_equip_out, gas_equip_out, shw_out)


if all_required_inputs(ghenv.Component) and _run:
    # check the presence of energyplus and check that the version is compatible
    check_energyplus_version()

    # set defaults for COP
    _heat_cop_ = 1 if _heat_cop_ is None else _heat_cop_
    _cool_cop_ = 1 if _cool_cop_ is None else _cool_cop_

    # create the Model from the _rooms and shades_
    _model = Model('Annual_Loads', _rooms, orphaned_shades=shades_,
                   tolerance=tolerance, angle_tolerance=angle_tolerance)
    floor_area = _model.floor_area
    assert floor_area != 0, 'Connected _rooms have no floors with which to compute EUI.'
    floor_area = floor_area * conversion_to_meters() ** 2

    # process the simulation folder name and the directory
    directory = os.path.join(folders.default_simulation_folder, _model.identifier)
    sch_directory = os.path.join(directory, 'schedules')
    nukedir(directory)  # delete any existing files in the directory

    # create simulation parameters for the coarsest/fastest E+ sim possible
    _sim_par_ = SimulationParameter()
    _sim_par_.timestep = _timestep_ if _timestep_ is not None else 1
    _sim_par_.shadow_calculation.solar_distribution = 'FullExterior'
    _sim_par_.output.add_zone_energy_use()
    _sim_par_.output.reporting_frequency = 'Monthly'
    if run_bal_:
        _sim_par_.output.add_output(gl_el_equip_out)
        _sim_par_.output.add_output(gl_gas_equip_out)
        _sim_par_.output.add_output(gl1_shw_out)
        _sim_par_.output.add_output(gl2_shw_out)
        _sim_par_.output.add_gains_and_losses('Total')
        _sim_par_.output.add_surface_energy_flow()

    # check the rooms for inaccurate cases
    if _sim_par_.timestep < 4:
        check_window_vent(_rooms)

    # assign design days from the EPW
    msg = None
    folder, epw_file_name = os.path.split(_epw_file)
    ddy_file = os.path.join(folder, epw_file_name.replace('.epw', '.ddy'))
    if os.path.isfile(ddy_file):
        try:
            _sim_par_.sizing_parameter.add_from_ddy_996_004(ddy_file)
        except AssertionError:
            msg = 'No design days were found in the .ddy file next to the _epw_file.'
    else:
         msg = 'No .ddy file was found next to the _epw_file.'
    if msg is not None:
        epw_obj = EPW(_epw_file)
        des_days = [epw_obj.approximate_design_day('WinterDesignDay'),
                    epw_obj.approximate_design_day('SummerDesignDay')]
        _sim_par_.sizing_parameter.design_days = des_days
        msg = msg + '\nDesign days were generated from the input _epw_file but this ' \
            '\nis not as accurate as design days from DDYs distributed with the EPW.'
        give_warning(ghenv.Component, msg)
        print msg

    # create the strings for simulation paramters and model
    ver_str = energyplus_idf_version() if energy_folders.energyplus_version \
        is not None else energyplus_idf_version(compatibe_ep_version)
    sim_par_str = _sim_par_.to_idf()
    model_str = _model.to.idf(_model, schedule_directory=sch_directory)
    idf_str = '\n\n'.join([ver_str, sim_par_str, model_str])

    # write the final string into an IDF
    idf = os.path.join(directory, 'in.idf')
    write_to_file_by_name(directory, 'in.idf', idf_str, True)

    # run the IDF through EnergyPlus
    silent = True if _run == 1 else False
    sql, zsz, rdd, html, err = run_idf(idf, _epw_file, silent=silent)
    if html is None and err is not None:  # something went wrong; parse the errors
        err_obj = Err(err)
        print(err_obj.file_contents)
        for error in err_obj.fatal_errors:
            raise Exception(error)

    # parse the result sql and get the monthly data collections
    if os.name == 'nt':  # we are on windows; use IronPython like usual
        sql_obj = SQLiteResult(sql)
        cool_init = sql_obj.data_collections_by_output_name(cool_out)
        heat_init = sql_obj.data_collections_by_output_name(heat_out)
        light_init = sql_obj.data_collections_by_output_name(light_out)
        elec_equip_init = sql_obj.data_collections_by_output_name(el_equip_out)
        gas_equip_init = sql_obj.data_collections_by_output_name(gas_equip_out)
        shw_init = sql_obj.data_collections_by_output_name(shw_out)
    else:  # we are on Mac; sqlite3 module doesn't work in Mac IronPython
        # Execute the honybee CLI to obtain the results via CPython
        cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'result',
                'data-by-outputs', sql]
        for outp in energy_output:
            cmds.append('["{}"]'.format(outp))
        process = subprocess.Popen(cmds, stdout=subprocess.PIPE)
        stdout = process.communicate()
        data_coll_dicts = json.loads(stdout[0])
        cool_init = serialize_data(data_coll_dicts[0])
        heat_init = serialize_data(data_coll_dicts[1])
        light_init = serialize_data(data_coll_dicts[2])
        elec_equip_init = serialize_data(data_coll_dicts[3])
        gas_equip_init = serialize_data(data_coll_dicts[4])
        shw_init = serialize_data(data_coll_dicts[5])

    # convert the results to EUI and ouput them
    cooling = data_to_load_intensity(cool_init, floor_area, 'Cooling', _cool_cop_)
    heating = data_to_load_intensity(heat_init, floor_area, 'Heating', _heat_cop_)
    lighting = data_to_load_intensity(light_init, floor_area, 'Lighting')
    equip = data_to_load_intensity(elec_equip_init, floor_area, 'Electric Equipment')
    total_load = [cooling.total, heating.total, lighting.total, equip.total]

    # add gas equipment if it is there
    if len(gas_equip_init) != 0:
        gas_equip = data_to_load_intensity(gas_equip_init, floor_area, 'Gas Equipment')
        equip = [equip, gas_equip]
        total_load.append(gas_equip.total)
    hot_water = []
    if len(shw_init) != 0:
        hot_water = data_to_load_intensity(shw_init, floor_area, 'Service Hot Water')
        total_load.append(hot_water.total)

    # construct the load balance if requested
    if run_bal_:
        if os.name == 'nt':  # we are on windows; use IronPython like usual
            bal_obj = LoadBalance.from_sql_file(_model, sql)
            balance = bal_obj.load_balance_terms(True, True)
        else:  # we are on Mac; sqlite3 module doesn't work in Mac IronPython
            # Execute the honybee CLI to obtain the results via CPython
            model_json = os.path.join(directory, 'in.hbjson')
            with open(model_json, 'w') as fp:
                json.dump(_model.to_dict(), fp)
            cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'result',
                    'load-balance', model_json, sql]
            process = subprocess.Popen(cmds, stdout=subprocess.PIPE)
            stdout = process.communicate()
            balance = serialize_data(json.loads(stdout[0]))
