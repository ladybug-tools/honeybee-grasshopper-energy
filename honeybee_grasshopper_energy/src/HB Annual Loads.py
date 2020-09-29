# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Run Honeybee Rooms through a quick energy simulation to obtain an estimate of
annual heating, cooling, lighting and equipment loads.
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
        _run: Set to "True" to run the simulation to obtain annual loads.

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
        cooling: A monthly Data Collection for the cooling load intensity in kWh/m2.
        heating: A monthly Data Collection for the heating load intensity in kWh/m2.
        lighting: A monthly Data Collection for the lighting load intensity in kWh/m2.
        equip: A monthly Data Collection for the equipment load intensity in kWh/m2.
            Typically, this is only the load from electric equipment but, if
            the attached _rooms have gas equipment, this will be a list of two
            data collections for electric and gas equipment respectively.
"""

ghenv.Component.Name = 'HB Annual Loads'
ghenv.Component.NickName = 'AnnualLoads'
ghenv.Component.Message = '0.2.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import os

try:
    from ladybug.futil import write_to_file_by_name, nukedir
    from ladybug.epw import EPW
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
    from honeybee_energy.simulation.parameter import SimulationParameter
    from honeybee_energy.run import run_idf
    from honeybee_energy.result.err import Err
    from honeybee_energy.result.sql import SQLiteResult
    from honeybee_energy.writer import energyplus_idf_version
    from honeybee_energy.config import folders as energy_folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import conversion_to_meters
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

# check the presence of openstudio and check that the version is compatible
compatibe_ep_version = (9, 3, 0)
hb_url = 'https://github.com/ladybug-tools/lbt-grasshopper/wiki/1.4-Compatibility-Matrix'
in_msg = 'Get a compatible version of EnergyPlus by downloading and installing\nthe ' \
    'version of OpenStudio listed in the Ladybug Tools compatibility matrix\n{}.'.format(hb_url)
assert energy_folders.energyplus_path is not None, \
    'No EnergyPlus installation was found on this machine.\n{}'.format(in_msg)
ep_version = energy_folders.energyplus_version
assert ep_version is not None and ep_version >= compatibe_ep_version, \
    'The installed EnergyPlus is not version {} or greater.' \
    '\n{}'.format('.'.join(str(v) for v in compatibe_ep_version), in_msg)


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


if all_required_inputs(ghenv.Component) and _run:
    # set defaults for COP
    _heat_cop_ = 1 if _heat_cop_ is None else _heat_cop_
    _cool_cop_ = 1 if _cool_cop_ is None else _cool_cop_

    # create the Model from the _rooms and shades_
    _model = Model('Quick_Annual_Energy', _rooms, orphaned_shades=shades_)
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
    sql, zsz, rdd, html, err = run_idf(idf, _epw_file, silent=True)
    if sql is None and err is not None:  # something went wrong; parse the errors
        err_obj = Err(err)
        print(err_obj.file_contents)
        for error in err_obj.fatal_errors:
            raise Exception(error)

    # parse the result sql and get the monthly data collections
    sql_obj = SQLiteResult(sql)
    cool_init = sql_obj.data_collections_by_output_name(
        'Zone Ideal Loads Supply Air Total Cooling Energy')
    heat_init = sql_obj.data_collections_by_output_name(
        'Zone Ideal Loads Supply Air Total Heating Energy')
    light_init = sql_obj.data_collections_by_output_name(
        'Zone Lights Electric Energy')
    elec_equip_init = sql_obj.data_collections_by_output_name(
        'Zone Electric Equipment Electric Energy')
    gas_equip_init = sql_obj.data_collections_by_output_name(
        'Zone Gas Equipment Gas Energy')

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
