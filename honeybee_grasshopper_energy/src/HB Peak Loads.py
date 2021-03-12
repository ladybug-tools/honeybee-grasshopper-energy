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
room-level peak cooling and heating on summer and winter design days.
-

    Args:
        _rooms: A list of Honeybee Rooms for which peak loads will be computed.
        shades_: An optional list of Honeybee Shades that can block the sun to
            the input _rooms.
        _ddy_file: Path to a .ddy file on your system as a text string, which contains
            design day conditions for the peak load analysis. This can also
            be the path to an .epw file, in which case design days will be
            determined by statitically analysing the annual data to approximate
            0.4% and 99.6% design conditions. Note that .ddy files can also be
            created using the "DF Construct Design Day" and "DF Write DDY"
            components.
            _
            When constructing custom design days, it is recommended that the .ddy
            file contain only one summer and one winter design day. If mutliple
            summer or winter design days are found, they will be filtered according
            to their name in order to identify the 0.4% and 99.6% design conditions
            for the sensible (dry bulb temperature) design days.
        _timestep_: An integer for the number of timesteps per hour at which the energy
            simulation will be run and results reported. It is recommended that
            this be at least 6 but it can be increased to better capture
            the minute in which peak cooling occurs. (Default: 6).
            The following values are acceptable:
            (1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60)
        run_bal_: Set to True to have the load balance computed after the
            simulation is run. This ensures that data collections for various
            terms of the load balance are output from the "balance".
            This can help explain why the loads are what they are but can
            also increase the component run time. (Default: False).
        _run: Set to "True" to run the simulation to obtain annual loads. This can
            also be the integer 2 to run the simulation while being able to see
            the simulation process (with a batch window).

    Returns:
        report: A report of the energy simulation run.
        peak_cool: A list of numbers that align with the input _rooms and correspond
            to the peak cooling of each room on the summer design day in Watts.
            Note that, for multi-room simulations, the individual room peaks may
            not be coincident, meaning that summing these values together won't
            give a correct sense of the size of cetral cooling equipment serving
            multiple rooms. For such equipment, the max of the cooling data
            collection should be used.
        peak_heat: A list of numbers that align with the input _rooms and correspond
            to the peak heating of each room on the winter design day in Watts.
            Note that, for multi-room simulations, the individual room peaks may
            not be coincident, meaning that summing these values together won't
            give a correct sense of the size of cetral heating equipment serving
            multiple rooms. For such equipment, the max of the heating data
            collection should be used.
        cooling: A Data Collection indicating the combined cooling demand of the rooms
            at each simulation timestep of the summer design day. This can be
            plugged into the "LB Monthly Chart" component to visualize the demand
            or it can be deconstructed with the "LB Deconstruct Data" component
            for analysis.
        heating: A Data Collection indicating the combined heating demand of the rooms
            at each simulation timestepof the winter design day. This can be
            plugged into the "LB Monthly Chart" component to visualize the demand
            or it can be deconstructed with the "LB Deconstruct Data" component
            for analysis.
        cool_bal: A list of data collections for the various terms of the sensible load
            balance that contribute to peak cooling on the summer design day. These
            can be plugged into the "LB Monthly Chart" component (with stack_ set
            to True) to visualize the terms contributing to the peak. Will be
            None unless run_bal_ is set to True.
        heat_bal: A list of data collections for the various terms of the sensible load
            balance that contribute to peak heating on the summer design day. These
            can be plugged into the "LB Monthly Chart" component (with stack_ set
            to True) to visualize the terms contributing to the peak. Will be
            None unless run_bal_ is set to True.
"""

ghenv.Component.Name = 'HB Peak Loads'
ghenv.Component.NickName = 'PeakLoads'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import os
import subprocess
import json

try:
    from ladybug.futil import write_to_file_by_name, nukedir
    from ladybug.ddy import DDY
    from ladybug.epw import EPW
    from ladybug.sql import SQLiteResult
    from ladybug.datacollection import HourlyContinuousCollection
    from ladybug.header import Header
    from ladybug.analysisperiod import AnalysisPeriod
    from ladybug.datatype.power import Power
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
    from honeybee_energy.result.zsz import ZSZ
    from honeybee_energy.writer import energyplus_idf_version
    from honeybee_energy.config import folders as energy_folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from lbt_recipes.version import check_energyplus_version
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import tolerance, angle_tolerance
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def check_for_filter_failure(des_days):
    """Raise a ValueError in the event that the design-dsy filtering process failed."""
    if len(des_days) == 0:
        raise ValueError(
            'Failed to filter the design days in the .ddy file to find the most '
            'appropriate one for sensible peak loads.\nTry connecting an .epw file '
            'instead.\n Or try creating your own .ddy file with a single summer '
            'and winter design day.'
        )


def check_and_filter_des_days(sim_par, des_days, day_type):
    """Filter design days to get the most appropriate one and assing it to sim_par."""
    if len(des_days) == 0:
        raise ValueError('No {}s were found in the connected .ddy file.'.format(day_type))
    elif len(des_days) == 1:  # just assign the one design day
        _sim_par_.sizing_parameter.add_design_day(des_days[0])
    else:  # find the most appropriate design day by percent
        key_wrd = '99.6%' if day_type == 'WinterDesignDay' else '.4%'
        des_days = [dday for dday in des_days if key_wrd in dday.name]
        check_for_filter_failure(des_days)
        if len(des_days) == 1:
            _sim_par_.sizing_parameter.add_design_day(des_days[0])
        else:  # find the most appropriate design day bu type
            key_wrd = ' DB' if day_type == 'WinterDesignDay' else ' DB=>MWB'
            des_days = [dday for dday in des_days if key_wrd in dday.name]
            check_for_filter_failure(des_days)
            if len(des_days) == 1:
                _sim_par_.sizing_parameter.add_design_day(des_days[0])
            else:
                check_for_filter_failure([])


def data_to_load(data_colls, data_type, analysis_period):
    """Convert data collections output by EnergyPlus to a single load collection.

    Args:
        data_colls: A list of monthly data collections for an energy term.
        data_type: Text for the data type of the collections (eg. "Cooling").
        analysis_period: AnalysisPeriod object describing the date and timestep
            of the design day.
    """
    if len(data_colls) != 0:
        total_vals = [sum(ts_vals) for ts_vals in zip(*data_colls)]
    else:  # just make a "filler" collection of 0 values
        total_vals = [0] * (24 * analysis_period.timestep)
    meta_dat = {'type': data_type}
    total_head = Header(Power(), 'W', analysis_period, meta_dat)
    return HourlyContinuousCollection(total_head, total_vals)


def serialize_data(data_dicts):
    """Reserialize a list of collection dictionaries."""
    return [HourlyContinuousCollection.from_dict(dat) for dat in data_dicts]


def filter_data_by_date(filt_date, data):
    """Filter a matrix of data collections by the date in their analysis period."""
    filtered_data = []
    for data_list in data:
        flit_list = []
        for d in data_list:
            a_per = d.header.analysis_period
            if a_per.st_month == filt_date.month and a_per.st_day == filt_date.day:
                flit_list.append(d.to_time_rate_of_change())
        filtered_data.append(flit_list)
    return filtered_data


def all_data_load_balance(rooms, data):
    """Get a LoadBalance object from a list of all relavant data collections."""
    return LoadBalance(
        rooms, lighting_data=data[0], electric_equip_data=data[1],
        gas_equip_data=c_data[2], service_hot_water_data=data[3],
        people_data=data[4], solar_data=data[5], infiltration_data=data[6],
        surface_flow_data=data[7], use_all_solar=True
    )


def reorder_balance(balance, order):
    """Reorder the terms of a load balance according to the desired names."""
    new_balance = []
    for term_name in order:
        for term in balance:
            if term.header.metadata['type'] == term_name:
                new_balance.append(term)
                break
    return new_balance


# List of the output strings that will be requested
opaque_energy_flow_output = 'Surface Average Face Conduction Heat Transfer Energy'
window_loss_output = 'Surface Window Heat Loss Energy'
window_gain_output = 'Surface Window Heat Gain Energy'
all_output = \
    [LoadBalance.LIGHTING, LoadBalance.ELECTRIC_EQUIP, LoadBalance.GAS_EQUIP,
     LoadBalance.HOT_WATER, LoadBalance.PEOPLE_GAIN, LoadBalance.SOLAR_GAIN,
     LoadBalance.INFIL_GAIN, LoadBalance.INFIL_LOSS, opaque_energy_flow_output,
     window_loss_output, window_gain_output]
term_order = \
    ['Solar', 'Window Conduction', 'Opaque Conduction', 'Infiltration', 'People',
     'Lighting', 'Electric Equipment', 'Gas Equipment', 'Service Hot Water']


if all_required_inputs(ghenv.Component) and _run:
    # check the presence of energyplus and check that the version is compatible
    check_energyplus_version()

    # create the Model from the _rooms and shades_
    _model = Model('Peak_Loads', _rooms, orphaned_shades=shades_,
                   tolerance=tolerance, angle_tolerance=angle_tolerance)

    # process the simulation folder name and the directory
    directory = os.path.join(folders.default_simulation_folder, _model.identifier)
    sch_directory = os.path.join(directory, 'schedules')
    nukedir(directory)  # delete any existing files in the directory

    # create simulation parameters for a design-day-optimized E+ sim
    _sim_par_ = SimulationParameter()
    _sim_par_.timestep = _timestep_ if _timestep_ is not None else 6
    _sim_par_.output.reporting_frequency = 'Timestep'
    _sim_par_.simulation_control.run_for_sizing_periods = True
    _sim_par_.simulation_control.run_for_run_periods = False
    if run_bal_:
        _sim_par_.output.add_zone_energy_use('Sensible')
        _sim_par_.output.add_gains_and_losses('Sensible')
        _sim_par_.output.add_surface_energy_flow()

    # load design days to the simulation parameters
    if _ddy_file.lower().endswith('.epw'):  # load design days from EPW
        epw_obj = EPW(_ddy_file)
        des_days = epw_obj.best_available_design_days()
        _sim_par_.sizing_parameter.design_days = des_days
        location = epw_obj.location
    else:  # load design days from DDY
        ddy_obj = DDY.from_ddy_file(_ddy_file)
        w_days = [day for day in ddy_obj.design_days if day.day_type == 'WinterDesignDay']
        s_days = [day for day in ddy_obj.design_days if day.day_type == 'SummerDesignDay']
        check_and_filter_des_days(_sim_par_, w_days, 'WinterDesignDay')
        check_and_filter_des_days(_sim_par_, s_days, 'SummerDesignDay')
        location = ddy_obj.location

    # get the dates of the heating and cooling design days
    h_dt = _sim_par_.sizing_parameter.design_days[0].sky_condition.date
    c_dt = _sim_par_.sizing_parameter.design_days[1].sky_condition.date
    tst = _sim_par_.timestep
    heat_ap = AnalysisPeriod(h_dt.month, h_dt.day, 0, h_dt.month, h_dt.day, 23, tst)
    cool_ap = AnalysisPeriod(c_dt.month, c_dt.day, 0, c_dt.month, c_dt.day, 23, tst)

    # create the strings for simulation paramters and model
    ver_str = energyplus_idf_version() if energy_folders.energyplus_version \
        is not None else energyplus_idf_version(compatibe_ep_version)
    model_str = _model.to.idf(_model, schedule_directory=sch_directory)
    idf_str = '\n\n'.join([ver_str, location.to_idf(), _sim_par_.to_idf(), model_str])

    # write the final string into an IDF
    idf = os.path.join(directory, 'in.idf')
    write_to_file_by_name(directory, 'in.idf', idf_str, True)

    # run the IDF through EnergyPlus
    silent = True if _run == 1 else False
    sql, zsz, rdd, html, err = run_idf(idf, silent=silent)
    if html is None and err is not None:  # something went wrong; parse the errors
        err_obj = Err(err)
        print(err_obj.file_contents)
        for error in err_obj.fatal_errors:
            raise Exception(error)

    # parse the result ZSZ and get the timestep data collections
    zsz_obj = ZSZ(zsz)
    cool_init = zsz_obj.cooling_load_data
    heat_init = zsz_obj.heating_load_data
    cooling = data_to_load(cool_init, 'Cooling', cool_ap)
    heating = data_to_load(heat_init, 'Heating', heat_ap)

    # parse the result sql and get the timestep data collections
    if os.name == 'nt':  # we are on windows; use IronPython like usual
        sql_obj = SQLiteResult(sql)
        peak_cool = [zs.calculated_design_load for zs in sql_obj.zone_cooling_sizes]
        peak_heat = [zs.calculated_design_load for zs in sql_obj.zone_heating_sizes]
    else:  # we are on Mac; sqlite3 module doesn't work in Mac IronPython
        # Execute the honybee CLI to obtain the results via CPython
        cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'result',
                'zone-sizes', sql]
        process = subprocess.Popen(cmds, stdout=subprocess.PIPE)
        stdout = process.communicate()
        peak_dicts = json.loads(stdout[0])
        peak_cool = [zs['calculated_design_load'] for zs in peak_dicts['cooling']]
        peak_heat = [zs['calculated_design_load'] for zs in peak_dicts['heating']]

    # construct the load balance if requested
    if run_bal_:
        if os.name == 'nt':  # we are on windows; use IronPython like usual
            light = sql_obj.data_collections_by_output_name(LoadBalance.LIGHTING)
            ele_equip = sql_obj.data_collections_by_output_name(LoadBalance.ELECTRIC_EQUIP)
            gas_equip = sql_obj.data_collections_by_output_name(LoadBalance.GAS_EQUIP)
            hot_water = sql_obj.data_collections_by_output_name(LoadBalance.HOT_WATER)
            people = sql_obj.data_collections_by_output_name(LoadBalance.PEOPLE_GAIN)
            solar = sql_obj.data_collections_by_output_name(LoadBalance.SOLAR_GAIN)
            infil_gain = sql_obj.data_collections_by_output_name(LoadBalance.INFIL_GAIN)
            infil_loss = sql_obj.data_collections_by_output_name(LoadBalance.INFIL_LOSS)
            opaque_flow = sql_obj.data_collections_by_output_name(opaque_energy_flow_output)
            window_loss = sql_obj.data_collections_by_output_name(window_loss_output)
            window_gain = sql_obj.data_collections_by_output_name(window_gain_output)
        else:  # we are on Mac; sqlite3 module doesn't work in Mac IronPython
            # Execute the honybee CLI to obtain the results via CPython
            cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'result',
                    'data-by-outputs', sql]
            for outp in all_output:
                out_str = json.dumps(outp) if isinstance(outp, tuple) else '["{}"]'.format(outp)
                cmds.append(out_str)
            process = subprocess.Popen(cmds, stdout=subprocess.PIPE)
            stdout = process.communicate()
            data_coll_dicts = json.loads(stdout[0])
            light = serialize_data(data_coll_dicts[0])
            ele_equip = serialize_data(data_coll_dicts[1])
            gas_equip = serialize_data(data_coll_dicts[2])
            hot_water = serialize_data(data_coll_dicts[3])
            people = serialize_data(data_coll_dicts[4])
            solar = serialize_data(data_coll_dicts[5])
            infil_gain = serialize_data(data_coll_dicts[6])
            infil_loss = serialize_data(data_coll_dicts[7])
            opaque_flow = serialize_data(data_coll_dicts[8])
            window_loss = serialize_data(data_coll_dicts[9])
            window_gain = serialize_data(data_coll_dicts[10])
            for dat in opaque_flow + window_loss + window_gain:
                dat.header.metadata['Surface'] = dat.header.metadata['Zone']

        infil = LoadBalance.subtract_loss_from_gain(infil_gain, infil_loss)
        window_flow = []
        window_flow = LoadBalance.subtract_loss_from_gain(window_gain, window_loss)
        face_flow = opaque_flow + window_flow
        all_data = [light, ele_equip, gas_equip, hot_water, people, solar, infil, face_flow]

        # construct the cooling design day balance
        c_data = filter_data_by_date(c_dt, all_data)
        load_bal = all_data_load_balance(_rooms, c_data)
        cool_bal = reorder_balance(load_bal.load_balance_terms(), term_order)

        # construct the heating design day balance
        h_data = filter_data_by_date(h_dt, all_data)
        load_bal = all_data_load_balance(_rooms, h_data)
        heat_bal = reorder_balance(load_bal.load_balance_terms(), term_order)
