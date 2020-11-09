# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Apply a transmittance schedule to Honeybee Shade objects. Alternatively, it can
assign a transmittance schedule to all of the child shades of an Aperture, Door,
Face, or a Room.
_
This component supports the assigning of different schedules based on cardinal
orientation, provided that a list of transmittance schedule are input to
the _trans_sch. 
-

    Args:
        _hb_objs: Honeybee Shades, Apertures, Door, Faces, or Rooms to which the
            input _trans_sch should be assigned. For the case of a Honeybee Aperture,
            Door, Face or Room, the ShadeConstruction will be assigned to only the
            child shades directly assigned to that object. So passing in a Room
            will not change the schedule of shades assigned to Apertures
            of the Room's Faces. If this is the desired outcome, then the Room
            should be deconstructed into its child objects before using
            this component.
        _trans_sch: A Honeybee ScheduleRuleset or ScheduleFixedInterval to be
            applied to the input _hb_objs. This can also be text for a schedule
            to be looked up in the shade schedule library. If an array of text
            or schedule objects are input here, different schedules will be
            assigned based on cardinal direction, starting with north and
            moving clockwise.
    
    Returns:
        hb_objs: The input honeybee objects with their shade transmittance
            schedules edited.
"""

ghenv.Component.Name = "HB Apply Shade Schedule"
ghenv.Component.NickName = 'ApplyShadeSch'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '2 :: Schedules'
ghenv.Component.AdditionalHelpFromDocStrings = '3'


try:  # import the honeybee-energy extension
    from honeybee_energy.lib.schedules import schedule_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.shade import Shade
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.aperture import Aperture
    from honeybee.door import Door
    from honeybee.orientation import angles_from_num_orient, face_orient_index
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    hb_objs = [obj.duplicate() for obj in _hb_objs]

    # process the input schedule
    for i, sch in enumerate(_trans_sch):
        if isinstance(sch, str):
            _trans_sch[i] = schedule_by_identifier(sch)

    # error message for unrecognized object
    error_msg = 'Input _hb_objs must be a Room, Face, Aperture, Door, or Shade. Not {}.'

    # assign the schedules
    if len(_trans_sch) == 1:
        for obj in hb_objs:
            if isinstance(obj, Shade):
                obj.properties.energy.transmittance_schedule = _trans_sch[0]
            elif isinstance(obj, (Aperture, Face, Room, Door)):
                for shd in obj.shades:
                    shd.properties.energy.transmittance_schedule = _trans_sch[0]
            else:
                raise TypeError(error_msg.format(type(obj)))
    else:  # assign schedules based on cardinal direction
        angles = angles_from_num_orient(len(_trans_sch))
        for obj in hb_objs:
            if isinstance(obj, (Aperture, Face, Door)):
                orient_i = face_orient_index(obj, angles)
                if orient_i is not None:
                    for shd in obj.shades:
                        shd.properties.energy.transmittance_schedule = _trans_sch[orient_i]
            elif isinstance(obj, Shade):
                obj.properties.energy.transmittance_schedule = _trans_sch[0]
            elif isinstance(obj, Room):
                 for shd in obj.shades:
                    shd.properties.energy.transmittance_schedule = _trans_sch[0]
            else:
                raise TypeError(error_msg.format(type(obj)))
