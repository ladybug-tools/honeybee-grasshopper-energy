# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Apply ConstructionSet to Honeybee Rooms or a Model.
-

    Args:
        _rooms: Honeybee Rooms to which the input _constr_set should be assigned.
            This can also be a Honeybee Model for which all Rooms will be
            assigned the ConstructionSet.
        _constr_set: A Honeybee ConstructionSet to be applied to the input _room.
            This can also be text for a construction set to be looked up in the
            construction set library.

    Returns:
        rooms: The input Rooms with their construction sets edited.
"""

ghenv.Component.Name = "HB Apply ConstructionSet"
ghenv.Component.NickName = 'ApplyConstrSet'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '1 :: Constructions'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:  # import the honeybee extension
    from honeybee.model import Model
    from honeybee.room import Room
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.lib.constructionsets import construction_set_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    rooms = [obj.duplicate() for obj in _rooms]

    # extract any rooms from the input Models
    hb_objs = []
    for hb_obj in rooms:
        if isinstance(hb_obj, Model):
            hb_objs.extend(hb_obj.rooms)
        elif isinstance(hb_obj, Room):
            hb_objs.append(hb_obj)
        else:
            raise ValueError(
                'Expected Honeybee Room or Model. Got {}.'.format(type(hb_obj)))

    # process the input construction set if it's a string
    if isinstance(_constr_set, str):
        _constr_set = construction_set_by_identifier(_constr_set)

    # assign the construction set
    for rm in hb_objs:
        rm.properties.energy.construction_set = _constr_set
