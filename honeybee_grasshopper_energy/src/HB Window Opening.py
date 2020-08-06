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
ghenv.Component.Message = '0.1.1'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:
    from honeybee_energy.ventcool.opening import VentilationOpening
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))


try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning, \
        longest_list
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # loop through the rooms and assign the objects
    op_count = 0
    rooms = []
    for i, room_init in enumerate(_rooms):
        room = room_init.duplicate()  # duplicate to avoid editing the input

        # assign the ventilation control for the windows
        room.properties.energy.window_vent_control = longest_list(_vent_cntrl, i)

        # create the base ventilation opening
        f_area = 0.5 if len(_fract_area_oper_) == 0 else longest_list(_fract_area_oper_, i)
        f_height = 1.0 if len(_fract_height_oper_) == 0 else longest_list(_fract_height_oper_, i)
        discharge = 0.17 if len(_discharge_coeff_) == 0 else longest_list(_discharge_coeff_, i)
        vent_open = VentilationOpening(f_area, f_height, discharge)

        # assign the cross ventilation
        cross_vent = longest_list(_wind_cross_vent_, i) if \
            len(_wind_cross_vent_) != 0 else None
        if cross_vent is None:
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
            vent_open.wind_cross_vent = cross_vent
        vent_aps = room.properties.energy.assign_ventilation_opening(vent_open)
        rooms.append(room)
        op_count += len(vent_aps)

    # give a warning if no operable windows were found among the connected rooms
    if op_count == 0:
        give_warning(
            ghenv.Component, 'No operable Apertures were found among the connected _rooms.\n'
            'Make sure that you have set the is_oeprable property of Apertures to True.')