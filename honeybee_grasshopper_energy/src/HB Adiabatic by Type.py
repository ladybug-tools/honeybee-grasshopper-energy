# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Make boundary conditions of Rooms or Faces adiabatic by face type.
-

    Args:
        _hb_objs: Honeybee Faces or Rooms to which adiabatic boundary conditions
            will be assigned.
        exterior_walls_: If True, all exterior walls of the input Rooms or Faces
            will be set to adiabatic. This can also be a list of boolean values
            and different adiabatic values will be assigned based on the cardinal 
            direction, starting with north and moving clockwise.
        roofs_: If True, all exterior roofs of the input Rooms or Faces will be
            set to adiabatic.
        exposed_floors_: If True, all exposed floors of the input Rooms or Faces
            will be set to adiabatic.
        interior_walls_: If True, all interior walls of the input Rooms or Faces
            will be set to adiabatic.
        interior_floors_: If True, all interior floors and ceilings of the input
            Rooms or Faces will be set to adiabatic.
    
    Returns:
        hb_objs: The input honeybee objects with their boundary conditions edited.
"""

ghenv.Component.Name = "HB Adiabatic by Type"
ghenv.Component.NickName = 'AdiabaticByType'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = "5"


try:  # import the core honeybee dependencies
    from honeybee.boundarycondition import Outdoors, Ground, Surface, boundary_conditions
    from honeybee.facetype import Wall, RoofCeiling, Floor
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.orientation import angles_from_num_orient, face_orient_index
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def check_type(face, boundary_c, face_type):
    """Check whether a given Face is of a certain type."""
    return isinstance(face.boundary_condition, boundary_c) and \
        isinstance(face.type, face_type)


def check_and_assign_adiabatic_to_face(face):
    """Check if a face if of a relevant type and assign Adiabatic if so."""
    
    # assign the adiabatic property to roofs
    if roofs_ and check_type(face, (Outdoors, Ground), RoofCeiling):
        face.boundary_condition = boundary_conditions.adiabatic
    
    # assign the adiabatic property to exposed floors
    if exposed_floors_ and check_type(face, (Outdoors, Ground), Floor):
        face.boundary_condition = boundary_conditions.adiabatic
    
    # assign the adiabatic property to exposed floors
    if interior_walls_ and check_type(face, Surface, Wall):
        face.boundary_condition = boundary_conditions.adiabatic
    
    # assign the adiabatic property to exposed floors
    if interior_floors_ and check_type(face, Surface, (RoofCeiling, Floor)):
        face.boundary_condition = boundary_conditions.adiabatic


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    hb_objs = [obj.duplicate() for obj in _hb_objs]
    
    # assign the adiabatic property to the walls
    if len(exterior_walls_) > 0:
        angles = angles_from_num_orient(len(exterior_walls_))
        for obj in hb_objs:
            if isinstance(obj, Room):
                for face in obj.faces:
                    if check_type(face, (Outdoors, Ground), Wall):
                        orient_i = face_orient_index(face, angles)
                        if orient_i is not None and exterior_walls_[orient_i]:
                            face.boundary_condition = boundary_conditions.adiabatic
            else:  # assume it is a Face
                if check_type(obj, (Outdoors, Ground), Wall):
                    orient_i = face_orient_index(obj, angles)
                    if orient_i is not None and exterior_walls_[orient_i]:
                        obj.boundary_condition = boundary_conditions.adiabatic
    
    # assign the adiabatic property to all of the other face types
    for obj in hb_objs:
        if isinstance(obj, Room):
            for face in obj.faces:
                check_and_assign_adiabatic_to_face(face)
        else:  # assume it is a Face
            check_and_assign_adiabatic_to_face(obj)
