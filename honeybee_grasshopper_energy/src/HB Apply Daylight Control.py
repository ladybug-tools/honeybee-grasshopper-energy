# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Apply simple daylight controls to Rooms.
_
Such simple controls will dim the lights in the energy simulation according to
whether the illuminance at a sensor location is at a target illuminance setpoint.
The method used to estimate illuiminance is fairly simple and, for more detailed
control over the parameters used to compute illuminance, the "HB Daylight Control
Schedule" component under HB-Radiance should be used.
-

    Args:
        _rooms: Honeybee Rooms to which simple daylight controls should be assigned.
        _sensor_points_: A list of point objects that align with the input _rooms and
            assign the position of the daylight sensor within the Room.
            This point should lie within the Room volume and a warning will
            be thrown and no daylight controls assigned for any point that
            lies outside the corresponding room. If unspecified, the
            sensor will be assigned to the center of the room at 0.8 meters
            above the floor. Note that such a center point might lie outside
            rooms that are significantly concave and no daylight controls
            will be assigned to these rooms in this case.
        _ill_setpoint_: A number for the illuminance setpoint in lux beyond which
            electric lights are dimmed if there is sufficient daylight.
            Some common setpoints are listed below. (Default: 300 lux).
            -
            50 lux - Corridors and hallways.
            150 lux - Computer work spaces (screens provide illumination).
            300 lux - Paper work spaces (reading from surfaces that need illumination).
            500 lux - Retail spaces or museums illuminating merchandise/artifacts.
            1000 lux - Operating rooms and workshops where light is needed for safety.

        _control_fract_: A number between 0 and 1 that represents the fraction of
            the Room lights that are dimmed when the illuminance at the sensor
            position is at the specified illuminance. 1 indicates that all lights are
            dim-able while 0 indicates that no lights are dim-able. Deeper rooms
            should have lower control fractions to account for the face that the
            lights in the back of the space do not dim in response to suitable
            daylight at the front of the room. (Default: 1).
        _min_power_in_: A number between 0 and 1 for the the lowest power the lighting
            system can dim down to, expressed as a fraction of maximum
            input power. (Default: 0.3).
        _min_light_out_: A number between 0 and 1 the lowest lighting output the lighting
            system can dim down to, expressed as a fraction of maximum
            light output. (Default: 0.2).
        off_at_min_: Boolean to note whether lights should switch off completely when
            they get to the minimum power input. (Default: False).

    Returns:
        report: Reports, errors, warnings, etc.
        rooms: The input Rooms with simple daylight controls assigned to them.
"""

ghenv.Component.Name = 'HB Apply Daylight Control'
ghenv.Component.NickName = 'DaylightControl'
ghenv.Component.Message = '1.6.1'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:  # import the honeybee-energy extension
    from honeybee_energy.load.daylight import DaylightingControl
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_point3d
    from ladybug_rhino.config import conversion_to_meters, tolerance
    from ladybug_rhino.grasshopper import all_required_inputs, longest_list, \
        give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    rooms = [room.duplicate() for room in _rooms]

    # set default values and perform checks
    dist_from_floor = 0.8 / conversion_to_meters()
    if len(_sensor_points_) != 0:
        assert len(_sensor_points_) == len(_rooms), 'Number of sensor points ({}) ' \
            'must align exactly with the number of rooms ({}).'.format(
                len(_sensor_points_), len(_rooms))
    _ill_setpoint_ = [300] if len(_ill_setpoint_) == 0 else _ill_setpoint_
    _control_fract_ = [1] if len(_control_fract_) == 0 else _control_fract_
    _min_power_in_ = [0.3] if len(_min_power_in_) == 0 else _min_power_in_
    _min_light_out_ = [0.2] if len(_min_light_out_) == 0 else _min_light_out_
    off_at_min_ = [False] if len(off_at_min_) == 0 else off_at_min_

    # loop through the rooms and assign daylight sensors
    unassigned_rooms = []
    if len(_sensor_points_) == 0:
        for i, room in enumerate(rooms):
            dl_control = room.properties.energy.add_daylight_control_to_center(
                dist_from_floor, longest_list(_ill_setpoint_, i),
                longest_list(_control_fract_, i), longest_list(_min_power_in_, i),
                longest_list(_min_light_out_, i), longest_list(off_at_min_, i),
                tolerance)
            if dl_control is None:
                unassigned_rooms.append(room.display_name)
    else:
        for i, room in enumerate(rooms):
            sensor_pt = to_point3d(_sensor_points_[i])
            if room.geometry.is_point_inside(sensor_pt):
                dl_control = DaylightingControl(
                    sensor_pt, longest_list(_ill_setpoint_, i),
                    longest_list(_control_fract_, i), longest_list(_min_power_in_, i),
                    longest_list(_min_light_out_, i), longest_list(off_at_min_, i))
                room.properties.energy.daylighting_control = dl_control
            else:
                unassigned_rooms.append(room.display_name)

    # give a warning about any rooms to which a sensor could not be assinged
    for room in unassigned_rooms:
        msg = 'Sensor point for room "{}" does not lie within the room volume.\n' \
            'No daylight sensors have been added to this room.'.format(room)
        print(msg)
        give_warning(ghenv.Component, msg)
