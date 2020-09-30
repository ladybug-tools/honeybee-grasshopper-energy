# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Construct a complete thermal load balance from energy simulation results and
honeybee Rooms or a Model.

-
    Args:
        _rooms_model: An array of honeybee Rooms or a honeybee Model for which
            the thermal load balance will be computed. In most cases, these
            should be the Rooms or Model that are fed directly into the
            simulation. But this can also be a subset of such Rooms and the
            balance will only be computed for those Rooms.
        cooling_: Array of data collections for 'Zone Ideal Loads Supply Air
            Cooling Energy'.
        heating_: Array of data collections for 'Zone Ideal Loads Supply Air
            Heating Energy'.
        lighting_: Array of data collections for 'Zone Lights Heating Energy'.
        electric_equip_: Array of data collections for 'Zone Electric Equipment
            Heating Energy'.
        gas_equip_: Array of data collections for 'Zone Gas Equipment Heating Energy'.
        people_gain_: Array of data collections for 'Zone People Heating Energy'.
        solar_gain_: Array of data collections for 'Zone Windows Transmitted
            Solar Radiation Energy'.
        infiltration_load_: An array of data collections for the infiltration heat
            loss (negative) or heat gain (positive).
        mech_vent_load_: An array of data collections for the ventilation heat loss
            (negative) or heat gain (positive) as a result of meeting minimum
            outdoor air requirements with the mechanical system.
        nat_vent_load_: An array of data collections for the natural ventilation
            heat loss (negative) or heat gain (positive).
        face_energy_flow_: An array of data collections for the surface heat loss
            (negative) or heat gain (positive).
    
    Returns:
        report: ...
        balance:  A list of data collections where each collection represents a
            load balance term. This can then be plugged into the "LB Hourly Plot"
            or "LB Monthly Chart" to give a visualization of the load balance
            over all connected Rooms.
        balance_storage:  The balance output plus an additional term to represent
            the remainder of the load balance. This term is labeled "Storage" since
            it typically represents the energy being stored in the building's mass. 
            If this term is particularly large, it can indicate that not all of
            the load balance terms have been plugged into this component.
        norm_bal: A list of data collections where each collection represents a
            load balance term that has bee normalized by the Room floor area.
            This can then be plugged into the "LB Hourly Plot" or "LB Monthly Chart"
            to give a visualization of the load balance over all connected Rooms.
        norm_bal_storage:  The norm_bal output plus an additional term to represent
            the remainder of the load balance. This term is labeled "Storage" since
            it typically represents the energy being stored in the building's mass. 
            If this term is particularly large, it can indicate that not all of
            the load balance terms have been plugged into this component.
"""

ghenv.Component.Name = 'HB Thermal Load Balance'
ghenv.Component.NickName = 'LoadBalance'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '6 :: Result'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.result.loadbalance import LoadBalance
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import units_system
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def check_input(input_list):
    """Check that an input isn't a zero-length list or None."""
    return None if len(input_list) == 0 or input_list[0] is None else input_list


if all_required_inputs(ghenv.Component):
    # extract any rooms from input Models
    rooms = []
    for hb_obj in _rooms_model:
        if isinstance(hb_obj, Model):
            rooms.extend(hb_obj.rooms)
        else:
            rooms.append(hb_obj)

    # process all of the inputs
    cooling_ = check_input(cooling_)
    heating_ = check_input(heating_)
    lighting_ = check_input(lighting_)
    electric_equip_ = check_input(electric_equip_)
    gas_equip_ = check_input(gas_equip_)
    people_gain_ = check_input(people_gain_)
    solar_gain_ = check_input(solar_gain_)
    infiltration_load_ = check_input(infiltration_load_)
    mech_vent_load_ = check_input(mech_vent_load_)
    nat_vent_load_ = check_input(nat_vent_load_)
    face_energy_flow_ = check_input(face_energy_flow_)

    # construct the load balance object and output the results
    load_bal_obj = LoadBalance(
        rooms, cooling_, heating_, lighting_, electric_equip_, gas_equip_,
        people_gain_, solar_gain_, infiltration_load_, mech_vent_load_,
        nat_vent_load_, face_energy_flow_, units_system())

    balance = load_bal_obj.load_balance_terms(False, False)
    if len(balance) != 0:
        balance_storage = balance + [load_bal_obj.storage]
        norm_bal = load_bal_obj.load_balance_terms(True, False)
        norm_bal_storage = load_bal_obj.load_balance_terms(True, True)
