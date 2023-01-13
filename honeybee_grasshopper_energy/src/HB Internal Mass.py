# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Assign internal thermal masses to Rooms, which can be used to account for the
effects of furniture inside Rooms or other massive building components like
staircases, hearths, etc.
_
The component accepts either Rhino geometry (representing furniture or massive
elements) or a numerical value of the mass's surface area. Several of these
components can be used in a series to descibe different internal masses made
of different materials.
_
Note that internal masses assigned this way cannot "see" solar radiation that
may potentially hit them and, as such, caution should be taken when using this
component with internal mass objects that are not always in shade. Masses are
factored into the the thermal calculations of the Room by undergoing heat
transfer with the indoor air.
-

    Args:
        _rooms: Honeybee Rooms to which internal masses should be assigned.
        _geo_or_area: A list of Rhino breps or meshes representing the surfaces of internal
            masses that are exposed to the air of the Room. Alternatively, this can
            be a number or list of numbers representing the surface area of the
            internal masses (in square meters) that are exposed to the Room air.
            _
            In the case of Rhino geometry representing the surfaces of internal
            masses, this component will determine which Room the geometry is in.
            However, geometry must lie COMPLETELY inside a single Room and
            cannot span between Rooms or span outside the building. If a geometry
            lies between two Rooms, it should be split in two along the boundary
            between the Rooms. Also note that geometries are assumed to have only
            one side exposed to the Room air so, if they are meant to represent
            a 2-sided object, the geometry should be duplicated and offset.
            _
            In the case of numbers representing the the surface area of the
            internal masses, inputs can be either a single number (which will be
            used to put internal masses into all Rooms using the specified
            surface area), or it can be a list of numbers that matches the input
            Rooms, which can be used to assign different amounts of mass surface
            area to different Rooms. All numbers are assumed to be in square meters.
        _construction: An OpaqueConstruction object that represents the material
            that the internal thermal mass is composed of. This can also be
            text for the identifier of the construction within the library.
        _name_: An optional text name for the internal mass. This can be useful for
            keeping track of different internal masses when using several of
            these components in series. If unspecified, a unique one will be
            generated.

    Returns:
        report: Reports, errors, warnings, etc.
        rooms: The input Rooms with internal masses assigned.
"""

ghenv.Component.Name = 'HB Internal Mass'
ghenv.Component.NickName = 'InternalMass'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import honeybee_energy dependencies
    from honeybee_energy.internalmass import InternalMass
    from honeybee_energy.construction.opaque import OpaqueConstruction
    from honeybee_energy.lib.constructions import opaque_construction_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_face3d
    from ladybug_rhino.config import conversion_to_meters
    from ladybug_rhino.grasshopper import all_required_inputs, longest_list, \
        document_counter
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects and process the construction
    rooms = [room.duplicate() for room in _rooms]
    if isinstance(_construction, str):
        _construction = opaque_construction_by_identifier(_construction)

    # determine whether the input _geo_or_area is geometry or floats
    try:
        areas = [float(num) for num in _geo_or_area]
    except AttributeError:  # assume that the input is a list of geometry
        geo = [f for geo in _geo_or_area for f in to_face3d(geo)]
        conversion = conversion_to_meters() ** 2
        areas = [0 for room in rooms]
        for i, room in enumerate(rooms):
            for face in geo:
                if room.geometry.is_point_inside(face.center):
                    areas[i] += face.area * conversion

    # create the internal mass objects and assign them to the rooms
    for i, room in enumerate(rooms):
        area = longest_list(areas, i)
        if area != 0:
            if len(_name_) == 0:  # make a default Room name
                display_name = 'Internal Mass {}'.format(document_counter('mass_count'))
            else:
                display_name = '{}_{}'.format(longest_list(_name_, i), i + 1) \
                    if len(_name_) != len(_rooms) else longest_list(_name_, i)
            name = clean_ep_string(display_name)
            mass = InternalMass(name, _construction, area)
            mass.display_name = display_name
            room.properties.energy.add_internal_mass(mass)
            print('Internal mass with area {} m2 has been added to room '
                  '"{}"'.format(round(area, 3), room.display_name))
