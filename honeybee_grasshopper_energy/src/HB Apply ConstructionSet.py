# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Apply ConstructionSet to Honeybee Rooms.
-

    Args:
        _rooms: Honeybee Rooms to which the input _constr_set should be assigned.
        _constr_set: A Honeybee ConstructionSet to be applied to the input _room.
            This can also be text for a construction set to be looked up in the
            construction set library.
    
    Returns:
        rooms: The input Rooms with their construction sets edited.
"""

ghenv.Component.Name = "HB Apply ConstructionSet"
ghenv.Component.NickName = 'ApplyConstrSet'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '1 :: Constructions'
ghenv.Component.AdditionalHelpFromDocStrings = '3'


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
    
    # process the input construction set if it's a string
    if isinstance(_constr_set, str):
        _constr_set = construction_set_by_identifier(_constr_set)
    
    # assign the construction set
    for rm in rooms:
        rm.properties.energy.construction_set = _constr_set
