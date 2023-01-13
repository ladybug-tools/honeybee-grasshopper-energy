# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Change the properties of Honeybee Rooms to reflect those of a ground surface.
_
This is particularly useful for setting up outdoor thermal comfort maps that account
for the surface temperature of the ground. Modeling the ground as a room this way
will ensure that shadows other objects cast upon it are accounted for along with
the storage of heat in the ground surface.
_
The turning of a Room into a ground entails:
_
* Setting all constructions to be indicative of a certain soil type.
* Setting all Faces except the roof to have a Ground boundary condition.
* Removing all loads and schedules assigned to the Room.
_
All values for the typical soil_types are taken from the Engineering Toolbox,
specifically these pages:
Soil Conductivity - http://www.engineeringtoolbox.com/thermal-conductivity-d_429.html
Soil Density - http://www.engineeringtoolbox.com/dirt-mud-densities-d_1727.html
Soil Heat Capacity - http://www.engineeringtoolbox.com/specific-heat-capacity-d_391.html
-

    Args:
        _rooms: Honeybee Rooms to be converted into ground objects.
        _soil_constr_: An OpaqueConstruction that reflects the soil type of the ground.
            This can also be text for a construction to be looked up in the opaque
            construction library. If a multi-layered construction is input, the multiple
            layers will only be used for the roof Face of the Room and all other
            Faces will get a construction with the inner-most layer assigned. Some
            common types of soil constructions contained in the default honeybee
            standards library are listed below. (Default: Concrete Pavement).
            _
            Grassy Lawn
            Dry Sand
            Dry Dust
            Moist Soil
            Mud
            Concrete Pavement
            Asphalt Pavement
            Solid Rock

    Returns:
        rooms: Rooms that have had their properties altered to be representative of
            ground conditions.
"""

ghenv.Component.Name = 'HB Ground'
ghenv.Component.NickName = 'Ground'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the honeybee-energy extension
    from honeybee_energy.lib.constructions import opaque_construction_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, longest_list
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate rooms and process the construction
    rooms = [room.duplicate() for room in _rooms]
    _soil_constr_ = _soil_constr_ if len(_soil_constr_) != 0 else ['Concrete Pavement']

    # loop through the rooms and convert them into ground objects
    for i, room in enumerate(rooms):
        soil_con = longest_list(_soil_constr_, i)
        if isinstance(soil_con, str):
            soil_con = opaque_construction_by_identifier(soil_con)
        room.properties.energy.make_ground(soil_con)
