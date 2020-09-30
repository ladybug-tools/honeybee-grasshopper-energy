# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

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
        lighting: DataCollections for the electric lighting energy needed for
            each room in kWh.
        electric_equip: DataCollections for the electric equipment energy needed
            for each room in kWh.
        gas_equip: DataCollections for the gas equipment energy needed for each
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
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '6 :: Result'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import os
import subprocess
import json

try:
    from ladybug.datacollection import HourlyContinuousCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.result.sql import SQLiteResult
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
    """Reserialize a list of HourlyContinuousCollection dictionaries."""
    return [HourlyContinuousCollection.from_dict(data) for data in data_dicts]


# List of all the output strings that will be requested
cooling_outputs = (
    'Zone Ideal Loads Supply Air Total Cooling Energy',
    'Zone Ideal Loads Zone Sensible Cooling Energy',
    'Zone Ideal Loads Zone Latent Cooling Energy',
    'Cooling Coil Electric Energy',
    'Chiller Electric Energy',
    'Zone VRF Air Terminal Cooling Electric Energy',
    'VRF Heat Pump Cooling Electric Energy',
    'Chiller Heater System Cooling Electric Energy',
    'District Cooling Chilled Water Energy',
    'Evaporative Cooler Electric Energy')
heating_outputs = (
    'Zone Ideal Loads Supply Air Total Heating Energy',
    'Zone Ideal Loads Zone Sensible Heating Energy',
    'Zone Ideal Loads Zone Latent Heating Energy',
    'Boiler Gas Energy',
    'Heating Coil Total Heating Energy',
    'Heating Coil Gas Energy',
    'Heating Coil Electric Energy',
    'Humidifier Electric Energy',
    'Zone VRF Air Terminal Heating Electric Energy',
    'VRF Heat Pump Heating Electric Energy',
    'VRF Heat Pump Defrost Electric Energy',
    'VRF Heat Pump Crankcase Heater Electric Energy',
    'Chiller Heater System Heating Electric Energy',
    'District Heating Hot Water Energy',
    'Baseboard Electric Energy',
    'Energy Management System Metered Output Variable 1')  # needed for ASHP electric
lighting_outputs = (
    'Zone Lights Electric Energy',
    'Zone Lights Total Heating Energy')
electric_equip_outputs =(
    'Zone Electric Equipment Electric Energy',
    'Zone Electric Equipment Total Heating Energy',
    'Zone Electric Equipment Radiant Heating Energy',
    'Zone Electric Equipment Convective Heating Energy',
    'Zone Electric Equipment Latent Gain Energy')
gas_equip_outputs = (
    'Zone Gas Equipment Gas Energy',
    'Zone Gas Equipment Total Heating Energy',
    'Zone Gas Equipment Radiant Heating Energy',
    'Zone Gas Equipment Convective Heating Energy',
    'Zone Gas Equipment Latent Gain Energy')
fan_electric_outputs = (
    'Zone Ventilation Fan Electric Energy',
    'Fan Electric Energy',
    'Cooling Tower Fan Electric Energy')
pump_electric_outputs = 'Pump Electric Energy'
people_gain_outputs = (
    'Zone People Total Heating Energy',
    'Zone People Sensible Heating Energy',
    'Zone People Sensible Latent Energy')
solar_gain_outputs = 'Zone Windows Total Transmitted Solar Radiation Energy'
infil_gain_outputs = (
    'Zone Infiltration Total Heat Gain Energy',
    'Zone Infiltration Sensible Heat Gain Energy',
    'Zone Infiltration Latent Heat Gain Energy')
infil_loss_outputs = (
    'Zone Infiltration Total Heat Loss Energy',
    'Zone Infiltration Sensible Heat Loss Energy',
    'Zone Infiltration Latent Heat Loss Energy')
vent_loss_outputs = (
    'Zone Ideal Loads Zone Total Heating Energy',
    'Zone Ideal Loads Zone Sensible Heating Energy',
    'Zone Ideal Loads Zone Latent Heating Energy')
vent_gain_outputs = (
    'Zone Ideal Loads Zone Total Cooling Energy',
    'Zone Ideal Loads Zone Sensible Cooling Energy',
    'Zone Ideal Loads Zone Latent Cooling Energy')
nat_vent_gain_outputs = (
    'Zone Ventilation Total Heat Gain Energy',
    'Zone Ventilation Sensible Heat Gain Energy',
    'Zone Ventilation Latent Heat Gain Energy')
nat_vent_loss_outputs = (
    'Zone Ventilation Total Heat Loss Energy',
    'Zone Ventilation Sensible Heat Loss Energy',
    'Zone Ventilation Latent Heat Loss Energy')
all_output = \
[cooling_outputs, heating_outputs, lighting_outputs, electric_equip_outputs,
 gas_equip_outputs, fan_electric_outputs, pump_electric_outputs, people_gain_outputs,
 solar_gain_outputs, infil_gain_outputs, infil_loss_outputs, vent_loss_outputs,
 vent_gain_outputs, nat_vent_gain_outputs, nat_vent_loss_outputs]


if all_required_inputs(ghenv.Component):
    if os.name == 'nt':  # we are on windows; use IronPython like usual
        # create the SQL result parsing object
        sql_obj = SQLiteResult(_sql)

        # get all of the results relevant for energy use
        cooling = sql_obj.data_collections_by_output_name(cooling_outputs)
        heating = sql_obj.data_collections_by_output_name(heating_outputs)
        lighting = sql_obj.data_collections_by_output_name(lighting_outputs)
        electric_equip = sql_obj.data_collections_by_output_name(electric_equip_outputs)
        gas_equip = sql_obj.data_collections_by_output_name(gas_equip_outputs)
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
        process = subprocess.Popen(cmds, stdout=subprocess.PIPE)
        stdout = process.communicate()
        data_coll_dicts = json.loads(stdout[0])

        # get all of the results relevant for energy use
        cooling = serialize_data(data_coll_dicts[0])
        heating = serialize_data(data_coll_dicts[1])
        lighting = serialize_data(data_coll_dicts[2])
        electric_equip = serialize_data(data_coll_dicts[3])
        gas_equip = serialize_data(data_coll_dicts[4])
        fan_electric = serialize_data(data_coll_dicts[5])
        pump_electric = serialize_data(data_coll_dicts[6])

        # get all of the results relevant for gains and losses
        people_gain = serialize_data(data_coll_dicts[7])
        solar_gain = serialize_data(data_coll_dicts[8])
        infil_gain = serialize_data(data_coll_dicts[9])
        infil_loss = serialize_data(data_coll_dicts[10])
        vent_loss = serialize_data(data_coll_dicts[11])
        vent_gain = serialize_data(data_coll_dicts[12])
        nat_vent_gain = serialize_data(data_coll_dicts[13])
        nat_vent_loss = serialize_data(data_coll_dicts[14])

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
