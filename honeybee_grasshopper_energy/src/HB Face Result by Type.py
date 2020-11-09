# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Separate data collections of energy simulation results by object and face type.
Input data must be for Faces, Apertures, Doors, or any combination of these objects.
_
This component can also be used to normalize such data by area.
-

    Args:
        _data: A list of data collections output from an energy simulation, which
            will be separated by object and face type. Data collections can be
            of any class (eg. MonthlyCollection, DailyCollection) but they
            should all have headers with metadata dictionaries with 'Surface'
            keys. These keys will be used to match the data in the collections
            to the input faces.
        _hb_objs: An array of honeybee Rooms, Faces, Apertures or Doors, which will
            be matched with the _data. This can also be an entire Model.
        norm_: Boolean to note whether results should be normalized by the face/sub-face
            area if the data type of the data_colections supports it. (Default: False)

    Returns:
        walls: Data collections with results for Walls with an Outdoors or Ground
            boundary condition.
        interior_walls: Data collections with results for Walls with a Surface or
            Adiabatic boundary condition.
        roofs: Data collections with results for RoofCeilings with an Outdoors or
            Ground boundary condition.
        ceilings: Data collections with results for RoofCeilings with a Surface
            or Adiabatic boundary condition.
        exterior_floors: Data collections with results for Floors with an Outdoors
            or Ground boundary condition.
        interior_floors: Data collections with results for Floors with a Surface
            or Adiabatic boundary condition.
        apertures: Data collections with results for Apertures with an Outdoors
            boundary condition.
        interior_apertures: Data collections with results for Apertures with a
            Surface boundary condition.
        doors: Data collections with results for Doors with an Outdoors boundary
            condition.
        interior_doors: Data collections with results for Doors with a Surface
            boundary condition.
"""

ghenv.Component.Name = 'HB Face Result by Type'
ghenv.Component.NickName = 'FaceResultByType'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '6 :: Result'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from honeybee.model import Model
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.aperture import Aperture
    from honeybee.door import Door
    from honeybee.boundarycondition import Surface, Adiabatic
    from honeybee.facetype import Wall, RoofCeiling, Floor, AirBoundary
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.result.match import match_faces_to_data
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
    from ladybug_rhino.config import conversion_to_meters
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def matched_areas(matched_objects):
    """Get an iterator of the areas from a list of matched objects."""
    flat_faces = (obj[0] for obj in matched_objects)
    flat_geo = (face.geometry if not isinstance(face, Face)
                else face.punched_geometry for face in flat_faces)
    return (face.area for face in flat_geo)


if all_required_inputs(ghenv.Component):
    # extract any faces from input Rooms or Models and convert geo to meters
    faces = []
    for hb_obj in _hb_objs:
        if isinstance(hb_obj, Model):
            for room in hb_obj.rooms:
                faces.extend(room.faces)
        elif isinstance(hb_obj, Room):
            faces.extend(hb_obj.faces)
        else:
            faces.append(hb_obj)
    m_convert = conversion_to_meters()
    if m_convert != 1:  # duplicate and scale all objects to meters
        faces = [face.duplicate() for face in faces]
        [face.scale(m_convert) for face in faces]

    # match the data with the faces
    matched_tups = match_faces_to_data(_data, faces)

    # normalize the data if requested
    if norm_:
        norm_types = [tup[1].header.data_type.normalized_type for tup in matched_tups]
        new_tups = []
        for area, nt, tup in zip(matched_areas(matched_tups), norm_types, matched_tups):
            if nt is None:  # data is not normalizable
                new_tups.append(tup)
            else:
                new_tups.append((tup[0], tup[1].normalize_by_area(area, 'm2')))
        matched_tups = new_tups

    # lists to be filled with data collections
    walls = []
    interior_walls = []
    roofs = []
    ceilings = []
    exterior_floors = []
    interior_floors = []
    apertures = []
    interior_apertures = []
    doors = []
    interior_doors = []

    # loop through the tuples and sort them by object and face type
    for tup in matched_tups:
        obj, data = tup
        bc = obj.boundary_condition
        if isinstance(obj, Face):
            if isinstance(obj.type, Wall):
                if isinstance(bc, (Surface, Adiabatic)):
                    interior_walls.append(data)
                else:
                    walls.append(data)
            elif isinstance(obj.type, RoofCeiling):
                if isinstance(bc, (Surface, Adiabatic)):
                    ceilings.append(data)
                else:
                    roofs.append(data)
            elif isinstance(obj.type, Floor):
                if isinstance(bc, (Surface, Adiabatic)):
                    interior_floors.append(data)
                else:
                    exterior_floors.append(data)
        elif isinstance(obj, Aperture):
            if isinstance(bc, Surface):
                interior_apertures.append(data)
            else:
                apertures.append(data)
        elif isinstance(obj, Door):
            if isinstance(bc, Surface):
                interior_doors.append(data)
            else:
                doors.append(data)
