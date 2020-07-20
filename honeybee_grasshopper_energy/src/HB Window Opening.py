# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Define the window opening properties for all operable apertures of a Room.
_
The default, simple ZoneVentilation can approximate airflow from both single-sided
bouyancy-driven ventilation as well as wind-driven cross ventilation, which results
from pressure differences across windows on two opposite sides of a Room.
_
Simple ZoneVentilation is computed using the following formulas:
Ventilation Wind = Wind Coefficient * Opening Area * Schedule * WindSpd 
Ventilation Stack = Stack Discharge Coefficient * Opening Area * Schedule * 
    SQRT(2 * Gravity * Operable Height * (|(Temp Zone - Temp Outdoors)| / Temp Zone)) 
Total Ventilation = SQRT((Ventilation Wind)^2 + (Ventilation Stack)^2)
_
More complex airflow phenomena can be modeled with the Airflow Network (AFN) and
the properties assigned by this component are still relevant for such simulations.
-

    Args:
        _rooms: Honeybee Room objects to which window ventilation opening properties
            will be assigned. Note that this component only assigns such properties
            to operable Apertures on the rooms. If the is_operable property
            of any of a room's apertures is not True, no opening properties
            will be assigned.
        _vent_cntrl: A Ventilation Control object from the "HB Ventilation Control"
            component, which dictates the opening behaviour of the Room's apertures.
        _fract_area_oper_: A number between 0.0 and 1.0 for the fraction of the
            window area that is operable. (Default: 0.5, typical of sliding windows).
        _fract_height_oper_: A number between 0.0 and 1.0 for the fraction
            of the distance from the bottom of the window to the top that is
            operable. (Default: 1.0, typical of windows that slide horizontally).
        _discharge_coeff_: A number between 0.0 and 1.0 that will be multipled
            by the area of the window in the stack (buoyancy-driven) part of the
            equation to account for additional friction from window geometry,
            insect screens, etc. (Default: 0.17, for unobstructed windows with
            insect screens). This value should be lowered if windows are of an
            awning or casement type and not allowed to fully open. Some common
            values for this coefficient include the following.
            -
                * 0.0 - Completely discount stack ventilation from the calculation.
                * 0.17 - For unobstructed windows with an insect screen.
                * 0.25 - For unobstructed windows with NO insect screen.
        _wind_cross_vent_: Boolean to indicate if there is an opening of roughly
            equal area on the opposite side of the Room such that wind-driven
            cross ventilation will be induced. If False, the assumption is that
            the operable area is primarily on one side of the Room and there is
            no wind-driven ventilation. If None, the normal vectors of the
            operable aperturs of the input _rooms will be analyzed. If window
            normals of a given room are found to have an angle difference greater
            than 90 degrees, cross ventilation will be set to True. Otherwise,
            it will be False.

    Returns:
        rooms: The input Honeybee Rooms with their window-opening properties edited.
"""

ghenv.Component.Name = 'HB Window Opening'
ghenv.Component.NickName = 'WindowOpen'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:
    from honeybee_energy.ventcool.opening import VentilationOpening
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))


try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set default properties for any missing inputs
    _fract_area_oper_ = 0.5 if _fract_area_oper_ is None else _fract_area_oper_
    _fract_height_oper_ = 1.0 if _fract_height_oper_ is None else _fract_height_oper_
    _discharge_coeff_ = 0.17 if _discharge_coeff_ is None else _discharge_coeff_
    vent_open = VentilationOpening(
        _fract_area_oper_, _fract_height_oper_, _discharge_coeff_)

    # loop through the rooms and assign the objects
    op_count = 0
    rooms = []
    for room_init in _rooms:
        room = room_init.duplicate()
        room.properties.energy.window_vent_control = _vent_cntrl
        if _wind_cross_vent_ is None:
            # analyze  normals of room's apertures to test if cross vent is possible
            orient_angles = []
            for face in room.faces:
                for ap in face.apertures:
                    if ap.is_operable:
                        orient_angles.append(ap.horizontal_orientation())
            if len(orient_angles) != 0:
                orient_angles.sort()
                vent_open.wind_cross_vent = \
                    True if orient_angles[-1] - orient_angles[0] >= 90 else False
            else:
                vent_open.wind_cross_vent = False
        else:
            vent_open.wind_cross_vent = _wind_cross_vent_
        vent_aps = room.properties.energy.assign_ventilation_opening(vent_open)
        rooms.append(room)
        op_count += len(vent_aps)

    # give a warning if no operable windows were found among the connected rooms
    if op_count == 0:
        give_warning(
            ghenv.Component, 'No operable Apertures were found among the connected _rooms.\n'
            'Make sure that you have set the is_oeprable property of Apertures to True.')