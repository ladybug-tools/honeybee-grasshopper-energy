# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Normalize Zone-level data collections from an energy simulation by the by the
floor area of the corresponding honeybee Rooms.
-

    Args:
        _data: A list of HourlyContinuousCollections of the same data type, which
            will be normalized by room floor area. Data collections can be of any class
            (eg. MonthlyCollection, DailyCollection) but they should originate
            from an energy simulation sql (with header metadata that has 'Zone' or
            'System' keys). These keys will be used to match the data in the collections
            to the input rooms.
        _model: An array of honeybee Rooms or a honeybee Model, which will
            be matched to the data collections. The length of these Rooms does
            not have to match the data collections and this object will only
            output collections for rooms that are found to be matching.

    Returns:
        total_data: The total results normalized by the floor area of all connected
            rooms. This accounts for the fact that some rooms have more floor
            area (or have a multiplier) and therefore get a greater weighting.
        room_data: The results normalized by the floor area of each individual room.
"""

ghenv.Component.Name = "HB Normalize by Floor Area"
ghenv.Component.NickName = 'NormByFlr'
ghenv.Component.Message = '1.1.1'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '6 :: Result'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug.header import Header
    from ladybug.datacollection import HourlyContinuousCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.result.match import match_rooms_to_data
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
    from ladybug_rhino.config import conversion_to_meters
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # extract any rooms from input Models and convert geo to meters if necessary
    rooms = []
    for hb_obj in _model:
        if isinstance(hb_obj, Model):
            rooms.extend(hb_obj.rooms)
        else:
            rooms.append(hb_obj)
    m_convert = conversion_to_meters()
    if m_convert != 1:  # duplicate and scale all objects to meters
        rooms = [room.duplicate() for room in rooms]
        [room.scale(m_convert) for room in rooms]

    # match the data with the rooms
    match_tups = match_rooms_to_data(_data, rooms)

    # divide the individual data collections by floor area
    total_area = 0
    room_data = []
    for tup in match_tups:
        total_flr_area = tup[0].floor_area * tup[2]  # includes effect of multiplier
        total_area += total_flr_area
        try:
            room_data.append(tup[1].normalize_by_area(total_flr_area, 'm2'))
        except ZeroDivisionError:  # no floor area; not normalizable
            pass

    # sum all collections together and normalize them by the total
    if len(match_tups) != 0:
        summed_vals = [val for val in match_tups[0][1]]
        for data_i in match_tups[1:]:
            for i, val in enumerate(data_i[1]):
                summed_vals[i] += val
    else:  # just assume all of the data corresponds with all input rooms
        summed_vals = [0 for val in _data[0]]
        total_area = sum(room.floor_area for room in rooms)
        for d in _data:
            for i, val in enumerate(d):
                summed_vals[i] += val
    try:
        total_data = _data[0].duplicate()
        total_data.values = summed_vals
        total_data = total_data.normalize_by_area(total_area, 'm2')
        total_data.header.metadata = {'type': _data[0].header.metadata['type']}
    except ZeroDivisionError:  # no floors in the model
        give_warning(ghenv.Component, 'No floors were found in the input _model.')
