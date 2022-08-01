# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Parse all of the common Room-level energy-related results from an SQL result file
that has been generated from an energy simulation.

-
    Args:
        _sql: The file path of the SQL result file that has been generated from
            an energy simulation.

    Returns:
        cooling: DataCollections for the cooling energy in kWh. For Ideal Air
            loads, this output is the sum of sensible and latent heat that must
            be removed from each room.  For detailed HVAC systems, this output
            will be electric energy needed to power each chiller/cooling coil.
        heating: DataCollections for the heating energy needed in kWh. For Ideal
            Air loads, this is the heat that must be added to each room.  For
            detailed HVAC systems, this will be fuel energy or electric energy
            needed for each boiler/heating element.
        lighting: DataCollections for the electric lighting energy used for
            each room in kWh.
        electric_equip: DataCollections for the electric equipment energy used
            for each room in kWh.
        gas_equip: DataCollections for the gas equipment energy used for each
            room in kWh.
        process: DataCollections for the process load energy used for each
            room in kWh.
        hot_water: DataCollections for the service hote water energy used for each
            room in kWh.
        fan_electric: DataCollections for the fan electric energy in kWh for
            either a ventilation fan or a HVAC system fan.
        pump_electric: DataCollections for the water pump electric energy in kWh
            for a heating/cooling system.
        people_gain: DataCollections for the internal heat gains in each room
            resulting from people (kWh).
        solar_gain: DataCollections for the total solar gain in each room (kWh).
        infiltration_load: DataCollections for the heat loss (negative) or heat
            gain (positive) in each room resulting from infiltration (kWh).
        mech_vent_load: DataCollections for the heat loss (negative) or heat gain
            (positive) in each room resulting from the outdoor air coming through
            the HVAC System (kWh).
        nat_vent_load: DataCollections for the heat loss (negative) or heat gain
            (positive) in each room resulting from natural ventilation (kWh).
"""

ghenv.Component.Name = 'HB Read Room Energy Result'
ghenv.Component.NickName = 'RoomEnergyResult'
ghenv.Component.Message = '1.5.1'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '6 :: Result'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import os
import subprocess
import json

try:
    from ladybug.sql import SQLiteResult
    from ladybug.datacollection import HourlyContinuousCollection, \
        MonthlyCollection, DailyCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.result.loadbalance import LoadBalance
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def subtract_loss_from_gain(gain_load, loss_load):
    """Create a single DataCollection from gains and losses."""
    total_loads = []
    for gain, loss in zip(gain_load, loss_load):
        total_load = gain - loss
        total_load.header.metadata['type'] = \
            total_load.header.metadata['type'].replace('Gain ', '')
        total_loads.append(total_load)
    return total_loads


def serialize_data(data_dicts):
    """Reserialize a list of collection dictionaries."""
    if len(data_dicts) == 0:
        return []
    elif data_dicts[0]['type'] == 'HourlyContinuous':
        return [HourlyContinuousCollection.from_dict(data) for data in data_dicts]
    elif data_dicts[0]['type'] == 'Monthly':
        return [MonthlyCollection.from_dict(data) for data in data_dicts]
    elif data_dicts[0]['type'] == 'Daily':
        return [DailyCollection.from_dict(data) for data in data_dicts]


# List of all the output strings that will be requested
cooling_outputs = LoadBalance.COOLING + (
    'Cooling Coil Electricity Energy',
    'Chiller Electricity Energy',
    'Zone VRF Air Terminal Cooling Electricity Energy',
    'VRF Heat Pump Cooling Electricity Energy',
    'Chiller Heater System Cooling Electricity Energy',
    'District Cooling Chilled Water Energy',
    'Evaporative Cooler Electricity Energy')
heating_outputs = LoadBalance.HEATING + (
    'Boiler NaturalGas Energy',
    'Heating Coil Total Heating Energy',
    'Heating Coil NaturalGas Energy',
    'Heating Coil Electricity Energy',
    'Humidifier Electricity Energy',
    'Zone VRF Air Terminal Heating Electricity Energy',
    'VRF Heat Pump Heating Electricity Energy',
    'VRF Heat Pump Defrost Electricity Energy',
    'VRF Heat Pump Crankcase Heater Electricity Energy',
    'Chiller Heater System Heating Electricity Energy',
    'District Heating Hot Water Energy',
    'Baseboard Electricity Energy',
    'Hot_Water_Loop_Central_Air_Source_Heat_Pump Electricity Consumption',
    'Boiler Electricity Energy',
    'Water Heater NaturalGas Energy',
    'Water Heater Electricity Energy',
    'Cooling Coil Water Heating Electricity Energy')
lighting_outputs = LoadBalance.LIGHTING
electric_equip_outputs = LoadBalance.ELECTRIC_EQUIP
gas_equip_outputs = LoadBalance.GAS_EQUIP
process_outputs = LoadBalance.PROCESS
shw_outputs = ('Water Use Equipment Heating Energy',) + LoadBalance.HOT_WATER
fan_electric_outputs = (
    'Zone Ventilation Fan Electricity Energy',
    'Fan Electricity Energy',
    'Cooling Tower Fan Electricity Energy')
pump_electric_outputs = 'Pump Electricity Energy'
people_gain_outputs = LoadBalance.PEOPLE_GAIN
solar_gain_outputs = LoadBalance.SOLAR_GAIN
infil_gain_outputs = LoadBalance.INFIL_GAIN
infil_loss_outputs = LoadBalance.INFIL_LOSS
vent_loss_outputs = LoadBalance.VENT_LOSS
vent_gain_outputs = LoadBalance.VENT_GAIN
nat_vent_gain_outputs = LoadBalance.NAT_VENT_GAIN
nat_vent_loss_outputs = LoadBalance.NAT_VENT_LOSS
all_output = \
[cooling_outputs, heating_outputs, lighting_outputs, electric_equip_outputs, gas_equip_outputs,
 process_outputs, shw_outputs, fan_electric_outputs, pump_electric_outputs,
 people_gain_outputs, solar_gain_outputs, infil_gain_outputs, infil_loss_outputs,
 vent_loss_outputs, vent_gain_outputs, nat_vent_gain_outputs, nat_vent_loss_outputs]


if all_required_inputs(ghenv.Component):
    # check the size of the SQL file to see if we should use the CLI
    assert os.path.isfile(_sql), 'No sql file found at: {}.'.format(_sql)
    if os.name == 'nt' and os.path.getsize(_sql) < 1e8:
        # small file on windows; use IronPython like usual
        # create the SQL result parsing object
        sql_obj = SQLiteResult(_sql)

        # get all of the results relevant for energy use
        cooling = sql_obj.data_collections_by_output_name(cooling_outputs)
        heating = sql_obj.data_collections_by_output_name(heating_outputs)
        lighting = sql_obj.data_collections_by_output_name(lighting_outputs)
        electric_equip = sql_obj.data_collections_by_output_name(electric_equip_outputs)
        hot_water = sql_obj.data_collections_by_output_name(shw_outputs)
        gas_equip = sql_obj.data_collections_by_output_name(gas_equip_outputs)
        process = sql_obj.data_collections_by_output_name(process_outputs)
        fan_electric = sql_obj.data_collections_by_output_name(fan_electric_outputs)
        pump_electric = sql_obj.data_collections_by_output_name(pump_electric_outputs)

        # get all of the results relevant for gains and losses
        people_gain = sql_obj.data_collections_by_output_name(people_gain_outputs)
        solar_gain = sql_obj.data_collections_by_output_name(solar_gain_outputs)
        infil_gain = sql_obj.data_collections_by_output_name(infil_gain_outputs)
        infil_loss = sql_obj.data_collections_by_output_name(infil_loss_outputs)
        vent_loss = sql_obj.data_collections_by_output_name(vent_loss_outputs)
        vent_gain = sql_obj.data_collections_by_output_name(vent_gain_outputs)
        nat_vent_gain = sql_obj.data_collections_by_output_name(nat_vent_gain_outputs)
        nat_vent_loss = sql_obj.data_collections_by_output_name(nat_vent_loss_outputs)

    else:  # we are on Mac; sqlite3 module doesn't work in Mac IronPython
        # Execute the honybee CLI to obtain the results via CPython
        cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'result',
                'data-by-outputs', _sql]
        for outp in all_output:
            out_str = json.dumps(outp) if isinstance(outp, tuple) else '["{}"]'.format(outp)
            cmds.append(out_str)
        use_shell = True if os.name == 'nt' else False
        process = subprocess.Popen(cmds, stdout=subprocess.PIPE, shell=use_shell)
        stdout = process.communicate()
        data_coll_dicts = json.loads(stdout[0])

        # get all of the results relevant for energy use
        cooling = serialize_data(data_coll_dicts[0])
        heating = serialize_data(data_coll_dicts[1])
        lighting = serialize_data(data_coll_dicts[2])
        electric_equip = serialize_data(data_coll_dicts[3])
        gas_equip = serialize_data(data_coll_dicts[4])
        process = serialize_data(data_coll_dicts[5])
        hot_water = serialize_data(data_coll_dicts[6])
        fan_electric = serialize_data(data_coll_dicts[7])
        pump_electric = serialize_data(data_coll_dicts[8])

        # get all of the results relevant for gains and losses
        people_gain = serialize_data(data_coll_dicts[9])
        solar_gain = serialize_data(data_coll_dicts[10])
        infil_gain = serialize_data(data_coll_dicts[11])
        infil_loss = serialize_data(data_coll_dicts[12])
        vent_loss = serialize_data(data_coll_dicts[13])
        vent_gain = serialize_data(data_coll_dicts[14])
        nat_vent_gain = serialize_data(data_coll_dicts[15])
        nat_vent_loss = serialize_data(data_coll_dicts[16])

    # do arithmetic with any of the gain/loss data collections
    if len(infil_gain) == len(infil_loss):
        infiltration_load = subtract_loss_from_gain(infil_gain, infil_loss)
    if len(vent_gain) == len(vent_loss) == len(cooling) == len(heating):
        mech_vent_loss = subtract_loss_from_gain(heating, vent_loss)
        mech_vent_gain = subtract_loss_from_gain(cooling, vent_gain)
        mech_vent_load = [data.duplicate() for data in
                          subtract_loss_from_gain(mech_vent_gain, mech_vent_loss)]
        for load in mech_vent_load:
            load.header.metadata['type'] = \
                'Zone Ideal Loads Ventilation Heat Energy'
    if len(nat_vent_gain) == len(nat_vent_loss):
        nat_vent_load = subtract_loss_from_gain(nat_vent_gain, nat_vent_loss)

    # remove the district hot water system used for service hot water from space heating
    shw_equip, distr_i = [], None
    for i, heat in enumerate(heating):
        if not isinstance(heat, float):
            try:
                heat_equip = heat.header.metadata['System']
                if heat_equip.startswith('SHW'):
                    shw_equip.append(i)
                elif heat_equip == 'SERVICE HOT WATER DISTRICT HEAT':
                    distr_i = i
            except KeyError:
                pass
    if len(shw_equip) != 0 and distr_i is None:
        hot_water = [heating.pop(i) for i in reversed(shw_equip)]
    elif distr_i is not None:
        for i in reversed(shw_equip + [distr_i]):
            heating.pop(i)
