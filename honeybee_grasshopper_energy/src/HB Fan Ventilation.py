# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Add ventilation fans to Rooms.
_
This fan is not connected to any heating or cooling system and is meant to
represent the intentional circulation of unconditioned outdoor air for the
purposes of keeping a space cooler, drier or free of indoor pollutants (as in
the case of kitchen or bathroom exhaust fans).
-

    Args:
        _rooms: Honeybee Rooms to which ventilation fans should be assigned.
        _name_: Text to set the name for the ventilation fan and to be incorporated into a
            unique ventilation fan identifier. If None, a unique name will be
            generated.
        _flow_rate: A positive number for the flow rate of the fan in m3/s.
        _vent_type_: Text to indicate the type of type of ventilation. Choose from the
            options below. For either Exhaust or Intake, values for fan pressure
            and efficiency define the fan electric consumption. For Exhaust
            ventilation, the conditions of the air entering the space are assumed
            to be equivalent to outside air conditions. For Intake and Balanced
            ventilation, an appropriate amount of fan heat is added to the
            entering air stream. For Balanced ventilation, both an intake fan
            and an exhaust fan are assumed to co-exist, both having the same
            flow rate and power consumption (using the entered values for fan
            pressure rise and fan total efficiency). Thus, the fan electric
            consumption for Balanced ventilation is twice that for the Exhaust or 
            Intake ventilation types which employ only a single fan. (Default: Balanced).
                * Exhaust
                * Intake
                * Balanced
        _pressure_rise_: A number for the the pressure rise across the fan in Pascals (N/m2).
            This is often a function of the fan speed and the conditions in
            which the fan is operating since having the fan blow air through filters
            or narrow ducts will increase the pressure rise that is needed to
            deliver the input flow rate. The pressure rise plays an important role in
            determining the amount of energy consumed by the fan. Smaller fans like
            a 0.05 m3/s desk fan tend to have lower pressure rises around 60 Pa.
            Larger fans, such as a 6 m3/s fan used for ventilating a large room tend
            to have higher pressure rises around 400 Pa. The highest pressure rises
            are typically for large fans blowing air through ducts and filters, which
            can have pressure rises as high as 1000 Pa. If this input is None,
            the pressure rise will be estimated from the flow_rate, with higher
            flow rates corresponding to larger pressure rises (up to 400 Pa). These
            estimated pressure rises are generally assumed to have minimal obstructions
            between the fan and the room and they should be increased if the fan is
            blowing air through ducts or filters.
        _efficiency_: A number between 0 and 1 for the overall efficiency of the fan.
            Specifically, this is the ratio of the power delivered to the fluid
            to the electrical input power. It is the product of the fan motor
            efficiency and the fan impeller efficiency. Fans that have a higher blade
            diameter and operate at lower speeds with smaller pressure rises for
            their size tend to have higher efficiencies. Because motor efficiencies
            are typically between 0.8 and 0.9, the best overall fan efficiencies
            tend to be around 0.7 with most typical fan efficiencies between 0.5 and
            0.7. The lowest efficiencies often happen for small fans in situations
            with high pressure rises for their size, which can result in efficiencies
            as low as 0.15. If None, this input will be estimated from the fan
            flow rate and pressure rise with large fans operating at low pressure
            rises for their size having up to 0.7 efficiency and small fans
            operating at high pressure rises for their size having as low as
            0.15 efficiency.
        vent_cntrl_: A Ventilation Control object from the "HB Ventilation Control"
            component that dictates the conditions under which the
            fan is turned on. If None, the fan on all of the time.

    Returns:
        report: Reports, errors, warnings, etc.
        rooms: The input Rooms with ventilation fans assigned to them.
"""

ghenv.Component.Name = 'HB Fan Ventilation'
ghenv.Component.NickName = 'FanVent'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:  # import the honeybee extension
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.ventcool.fan import VentilationFan
    from honeybee_energy.lib.schedules import schedule_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, longest_list
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    rooms = [room.duplicate() for room in _rooms]

    # set default values and check the inputs
    _vent_type_ = ['Balanced'] if len(_vent_type_) == 0 else _vent_type_
    _pressure_rise_ = [None] if len(_pressure_rise_) == 0 else _pressure_rise_
    _efficiency_ = [None] if len(_efficiency_) == 0 else _efficiency_
    vent_cntrl_ = [None] if len(vent_cntrl_) == 0 else vent_cntrl_

    # loop through the rooms and assign ventilation fans
    for i, room in enumerate(rooms):
        flow_rate = longest_list(_flow_rate, i)
        if flow_rate != 0:
            name = clean_and_id_ep_string('VentilationFan') if len(_name_) == 0 else \
                clean_ep_string(longest_list(_name_, i))
            fan = VentilationFan(
                name, flow_rate,  longest_list(_vent_type_, i),
                longest_list(_pressure_rise_, i),
                longest_list(_efficiency_, i), longest_list(vent_cntrl_, i)
            )
            room.properties.energy.add_fan(fan)
