# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Apply OpaqueConstruction to Honeybee Faces, Doors or Room walls.
_
This component supports the assigning of different constructions based on cardinal
orientation, provided that a list of OpaqueConstructions are input to the _constr. 
-

    Args:
        _hb_objs: Honeybee Faces, Doors, Rooms or a Model to which the input _constr should
            be assigned. For the case of a Room or a Model, the construction
            will only be applied to the Room's outdoor walls. Note that, if you
            need to assign a construction to all the roofs, floors, etc. of a
            Room, the best practice is to create a ConstructionSet and assing that
            to the Room.
        _constr: A Honeybee OpaqueConstruction to be applied to the input _hb_objs.
            This can also be text for a construction to be looked up in the opaque
            construction library. If an array of text or construction objects
            are input here, different constructions will be assigned based on
            cardinal direction, starting with north and moving clockwise.
    
    Returns:
        hb_objs: The input honeybee objects with their constructions edited.
"""

ghenv.Component.Name = "HB Apply Opaque Construction"
ghenv.Component.NickName = 'ApplyOpaqueConstr'
ghenv.Component.Message = '1.9.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '1 :: Constructions'
ghenv.Component.AdditionalHelpFromDocStrings = '3'


try:  # import the honeybee-energy extension
    from honeybee_energy.lib.constructions import opaque_construction_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.boundarycondition import Outdoors
    from honeybee.facetype import Wall
    from honeybee.model import Model
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.door import Door
    from honeybee.orientation import angles_from_num_orient, face_orient_index
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def is_exterior_wall(face):
    """Check whether a given Face is an exterior Wall."""
    return isinstance(face.boundary_condition, Outdoors) and \
        isinstance(face.type, Wall)


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    hb_objs = [obj.duplicate() for obj in _hb_objs]

    # process the input constructions
    for i, constr in enumerate(_constr):
        if isinstance(constr, str):
            _constr[i] = opaque_construction_by_identifier(constr)

    # error message for unrecognized object
    error_msg = 'Input _hb_objs must be a Room, Face, or Door. Not {}.'

    # assign the constructions
    if len(_constr) == 1:  # assign indiscriminately, even if it's horizontal
        for obj in hb_objs:
            if isinstance(obj, (Face, Door)):
                obj.properties.energy.construction = _constr[0]
            elif isinstance(obj, (Room, Model)):
                for face in obj.faces:
                    if is_exterior_wall(face):
                        face.properties.energy.construction = _constr[0]
            else:
                raise TypeError(error_msg.format(type(obj)))
    else:  # assign constructions based on cardinal direction
        angles = angles_from_num_orient(len(_constr))
        for obj in hb_objs:
            if isinstance(obj, (Face, Door)):
                orient_i = face_orient_index(obj, angles)
                if orient_i is not None:
                    obj.properties.energy.construction = _constr[orient_i]
            elif isinstance(obj, (Room, Model)):
                 for face in obj.faces:
                     if is_exterior_wall(face):
                         orient_i = face_orient_index(face, angles)
                         if orient_i is not None:
                            face.properties.energy.construction = _constr[orient_i]
            else:
                raise TypeError(error_msg.format(type(obj)))

