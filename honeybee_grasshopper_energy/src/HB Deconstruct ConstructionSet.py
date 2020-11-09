# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Deconstruct a construction set into its constituient exterior constructions.
-

    Args:
        _constr_set: A construction set to be deconstructed. This can also be
            text for a construction set to be looked up in the construction
            set library.

    Returns:
        exterior_wall: A construction object for the set's exterior walls.
        exterior_roof: A construction object for the set's exterior roofs.
        exposed_floor: A construction object for the set's exposed floors.
        ground_wall: A construction object for the set's underground walls.
        ground_roof: A construction object for the set's underground roofs.
        ground_floor: A construction object for the set's ground-contact floors.
        window: A construction object for apertures with an Outdoors boundary
            condition and a Wall face type for their parent face.
        skylight: A construction object for apertures with an Outdoors boundary
            condition and a RoofCeiling or Floor face type for their parent face.
        operable: A construction object for apertures with an Outdoors boundary
            condition and True is_operable property.
        exterior_door: A construction object for opaque doors with an Outdoors
            boundary condition and a Wall face type for their parent face.
        overhead_door: A construction object for opaque doors with an Outdoors
            boundary condition and a RoofCeiling or Floor face type for their
            parent face.
        glass_door: A construction object for all glass doors with an Outdoors
            boundary condition.
"""

ghenv.Component.Name = "HB Deconstruct ConstructionSet"
ghenv.Component.NickName = 'DecnstrConstrSet'
ghenv.Component.Message = '1.1.0'
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
    
    exterior_wall = _constr_set.wall_set.exterior_construction
    exterior_roof = _constr_set.roof_ceiling_set.exterior_construction
    exposed_floor = _constr_set.floor_set.exterior_construction
    ground_wall = _constr_set.wall_set.ground_construction
    ground_roof = _constr_set.roof_ceiling_set.ground_construction
    ground_floor = _constr_set.floor_set.ground_construction
    window = _constr_set.aperture_set.window_construction
    skylight = _constr_set.aperture_set.skylight_construction
    operable = _constr_set.aperture_set.operable_construction
    exterior_door = _constr_set.door_set.exterior_construction
    overhead_door = _constr_set.door_set.overhead_construction
    glass_door = _constr_set.door_set.exterior_glass_construction
