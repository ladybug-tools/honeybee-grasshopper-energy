# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Apply a ShadeConstruction to Honeybee Shade objects. Alternatively, it can
assign a ShadeConstruction to all of the child shades of an Aperture, Door,
Face, or a Room.
_
This component supports the assigning of different constructions based on cardinal
orientation, provided that a list of ShadeConstructions are input to the _constr. 
-

    Args:
        _hb_objs: Honeybee Shades, Apertures, Doors, Faces, or Rooms to which the
            input _constr should be assigned. For the case of a Honeybee Aperture,
            Door, Face or Room, the ShadeConstruction will be assigned to only the
            child shades directly assigned to that object. So passing in a Room
            will not change the construction of shades assigned to Apertures
            of the Room's Faces. If this is the desired outcome, then the Room
            should be deconstructed into its child objects before using
            this component.
        _constr: A Honeybee ShadeConstruction to be applied to the input _hb_objs.
            This can also be text for a construction to be looked up in the shade
            construction library. If an array of text or construction objects
            are input here, different constructions will be assigned based on
            cardinal direction, starting with north and moving clockwise.
    
    Returns:
        hb_objs: The input honeybee objects with their constructions edited.
"""

ghenv.Component.Name = "HB Apply Shade Construction"
ghenv.Component.NickName = 'ApplyShadeConstr'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '1 :: Constructions'
ghenv.Component.AdditionalHelpFromDocStrings = '3'


try:  # import the honeybee-energy extension
    from honeybee_energy.lib.constructions import shade_construction_by_identifier
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
    
    # process the input constructions
    for i, constr in enumerate(_constr):
        if isinstance(constr, str):
            _constr[i] = shade_construction_by_identifier(constr)
    
    # error message for unrecognized object
    error_msg = 'Input _hb_objs must be a Room, Face, Aperture, Door, or Shade. Not {}.'
    
    # assign the constructions
    if len(_constr) == 1:
        for obj in hb_objs:
            if isinstance(obj, Shade):
                obj.properties.energy.construction = _constr[0]
            elif isinstance(obj, (Aperture, Face, Room, Door)):
                for shd in obj.shades:
                    shd.properties.energy.construction = _constr[0]
            else:
                raise TypeError(error_msg.format(type(obj)))
    else:  # assign constructions based on cardinal direction
        angles = angles_from_num_orient(len(_constr))
        for obj in hb_objs:
            if isinstance(obj, (Aperture, Face, Door)):
                orient_i = face_orient_index(obj, angles)
                if orient_i is not None:
                    for shd in obj.shades:
                        shd.properties.energy.construction = _constr[orient_i]
            elif isinstance(obj, Shade):
                obj.properties.energy.construction = _constr[0]
            elif isinstance(obj, Room):
                 for shd in obj.shades:
                    shd.properties.energy.construction = _constr[0]
            else:
                raise TypeError(error_msg.format(type(obj)))

