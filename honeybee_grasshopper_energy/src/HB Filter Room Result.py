# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Filter data collections of energy simulation results using a list of Rooms to
which the simulations relate.
_
This can be used in combination with components like "HB Rooms by Attribute" to
get simulation resutls for subset of rooms (eg. all of the offices).
-

    Args:
        _data: A list of data collections output from an energy simulation, which
            will be filtered based on the input _rooms. Data collections can be
            of any class (eg. MonthlyCollection, DailyCollection) but they
            should originate from an energy simulation sql (with header
            metadata that has 'Zone' or 'System' keys). These keys will be
            used to match the data in the collections to the input rooms.
        _rooms: Honeybee Rooms, which will be matched with the input _data. This can
            also be an enitre Model.
        norm_: Boolean to note whether results should be normalized by the Room floor
            area if the data type of the data_colections supports it. (Default: False)

    Returns:
        data: The input _data filtered by the connected _rooms (and optionally normalized
            by the floor area of each individual room).
"""

ghenv.Component.Name = 'HB Filter Room Result'
ghenv.Component.NickName = 'FilterRoomResult'
ghenv.Component.Message = '1.8.1'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '6 :: Result'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.room import Room
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.result.match import match_rooms_to_data
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
    from ladybug_rhino.config import conversion_to_meters
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # extract any rooms from input Models and convert geo to meters if necessary
    rooms = []
    for hb_obj in _rooms:
        if isinstance(hb_obj, Room):
            rooms.append(hb_obj)
        elif isinstance(hb_obj, Model):
            rooms.extend(hb_obj.rooms)
        else:
            raise TypeError(
                'Expected Honeybee Room or Model. Got {}.'.format(type(hb_obj)))
    m_convert = conversion_to_meters()
    if norm_ and m_convert != 1:  # duplicate and scale all objects to meters
        rooms = [room.duplicate() for room in rooms]
        [room.scale(m_convert) for room in rooms]

    # match the data with the rooms
    match_tups = match_rooms_to_data(_data, rooms, space_based=True)

    # divide the individual data collections by floor area if requested
    if norm_:
        data = []
        for tup in match_tups:
            total_flr_area = tup[0].floor_area * tup[2]  # includes effect of multiplier
            try:
                data.append(tup[1].normalize_by_area(total_flr_area, 'm2'))
            except ZeroDivisionError:  # no floor area; not normalizable
                pass
    else:
        data = [tup[1] for tup in match_tups]
