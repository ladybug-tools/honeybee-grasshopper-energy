# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Set any Faces of Rooms with missing adjacencies to Adiabatic.
_
This is useful when simulating a subset of Rooms from a larger Model.
_
If any of the Faces with missing adjacencies have sub-faces, these will be removed
in order to accommodate the adiabatic condition. Similarly, if the Face is an
AirBoundary, the type will be set to a Wall.
-

    Args:
        _rooms: A list of Honeybee Rooms which will have its adjacencies patched
            with Adiabatic boundary conditions. This can also be an entire
            honyebee Model. Any adjacnecy not found across all of the rooms
            will be replaced with an Adiabatic boundary.

    Returns:
        rooms: Rooms that have had their missing adjacencies patched.
"""

ghenv.Component.Name = 'HB Patch Missing Adjacency'
ghenv.Component.NickName = 'PatchAdj'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.room import Room
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))


try:
    from ladybug_rhino.grasshopper import all_required_inputs
    from ladybug_rhino.config import tolerance, units_system
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # collect all rooms and duplicate them
    rooms = []
    for hb_obj in _rooms:
        if isinstance(hb_obj, Model):
            rooms.extend(hb_obj.rooms)
        elif isinstance(hb_obj, Room):
            rooms.append(hb_obj)
        else:
            raise ValueError('Expected Room or Model object. Got {}.'.format(type(hb_obj)))
    rooms = [room.duplicate() for room in rooms]  # duplicate to avoid editing input

    # patch adjacency across all of the Rooms
    adj_model = Model('patch_adj_model', rooms=rooms, tolerance=tolerance,
                      units=units_system())
    adj_model.properties.energy.missing_adjacencies_to_adiabatic()
    rooms = adj_model.rooms
