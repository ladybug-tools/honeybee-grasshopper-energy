# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Define the window opening properties for all operable apertures of a Room.
_
By default, the properties assigned by this component are translated into simple
ZoneVentilation objects in the resulting IIDF, which can approximate airflow
from both single-sided bouyancy-driven ventilation as well as wind-driven cross
ventilation. Bouyancy-driven flow can happen for essentially all openings while
wind-driven flow can only happen when there are pressure differences across
windows on opposite sides of a Room.
_
Simple ZoneVentilation is computed using the following formulas:
_
VentilationWind = WindCoefficient * OpeningArea * Schedule * WindSpeed
VentilationStack = StackDischargeCoefficient * OpeningArea * ScheduleValue * 
    SQRT(2 * GravityAccelration * HeightNPL * (|(TempZone - TempOutdoors)| / TempZone)) 
TotalVentilation = SQRT((VentilationWind)^2 + (VentilationStack)^2)
_
Note that the (OpeningArea) term is derived from the _fract_area_oper_ and the area
of each aperture while the (HeightNPL) term is derived from the _fract_height_oper_
and the height of each aperture.  The "NPL" stands for "Neutral Plane" and the
whole term represents the height from midpoint of lower opening to the neutral
pressure level of the window (computed as 1/4 of the height of each Aperture in
the translation from honeybee to IDF).
_
More complex airflow phenomena can be modeled by using this component in conjunction
with with the Airflow Network (AFN) component. Note that the window opening
properties assigned by this component are still relevant for such AFN simulations.
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
            insect screens, etc. (Default: 0.45, for unobstructed windows with
            insect screens). This value should be lowered if windows are of an
            awning or casement type and not allowed to fully open. Some common
            values for this coefficient include the following.
            -
                * 0.0 - Completely discount stack ventilation from the calculation.
                * 0.45 - For unobstructed windows with an insect screen.
                * 0.65 - For unobstructed windows with NO insect screen.
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
ghenv.Component.Message = '1.6.0'
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
        discharge = 0.45 if len(_discharge_coeff_) == 0 else longest_list(_discharge_coeff_, i)
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
                        try:
                            orient_angles.append(ap.horizontal_orientation())
                        except ZeroDivisionError:
                            orient_angles.append(0)
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
            'Make sure that you have set the is_operable property of Apertures to True.')