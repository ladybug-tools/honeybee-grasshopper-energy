# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Deconstruct a construction set into its constituient interior constructions.
-

    Args:
        _constr_set: A construction set to be deconstructed. This can also be
            text for a construction set to be looked up in the construction
            set library.

    Returns:
        interior_wall: A construction object for the set's interior walls.
        ceiling: A construction object for the set's interior roofs.
        interior_floor: A construction object for the set's interior floors.
        interior_window: A construction object for all apertures with a Surface
            boundary condition.
        interior_door: A construction object for all opaque doors with a Surface
            boundary condition.
        int_glass_door: A construction object for all glass doors with a Surface
            boundary condition.
"""

ghenv.Component.Name = "HB Deconstruct ConstructionSet Interior"
ghenv.Component.NickName = 'DecnstrConstrSetInt'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = "1 :: Constructions"
ghenv.Component.AdditionalHelpFromDocStrings = "2"


try:  # import the honeybee-energy dependencies
    from honeybee_energy.constructionset import ConstructionSet
    from honeybee_energy.lib.constructionsets import construction_set_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))
try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # check the input
    if isinstance(_constr_set, str):
        _constr_set = construction_set_by_identifier(_constr_set)
    else:
        assert isinstance(_constr_set, ConstructionSet), \
            'Expected ConstructionSet. Got {}.'.format(type(_constr_set))
    
    interior_wall = _constr_set.wall_set.interior_construction
    ceiling = _constr_set.roof_ceiling_set.interior_construction
    interior_floor = _constr_set.floor_set.interior_construction
    interior_window = _constr_set.aperture_set.interior_construction
    interior_door = _constr_set.door_set.interior_construction
    int_glass_door = _constr_set.door_set.interior_glass_construction
