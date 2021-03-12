# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a ConstructionSet object containing all energy constructions needed to
create an energy model. ConstructionSets can be assigned to Honeybee Rooms to
specify all default constructions on the Room.
-

    Args:
        _name: Text to set the name for the ConstructionSet and to be incorporated
            into a unique ConstructionSet identifier. If None, a random one will
            be genrated.
        base_constr_set_: An optional ConstructionSet object that will be used
            as the starting point for the new ConstructionSet output from this
            component. This can also be text for the name of a ConstructionSet
            within the library such as that output from the "HB Search Construction
            Sets" component. If None, the Honeybee "Generic Default Construction
            Set" will be used as the base.
        _exterior_subset_: A construction subset list from the "HB Exterior Construction
            Subset" component. Note that None values in this list correspond to
            no change to the given construction in the base_constr_set_.
        _ground_subset_: A construction subset list from the "HB Ground Construction
            Subset" component. Note that None values in this list correspond to
            no change to the given construction in the base_constr_set_.
        _interior_subset_: A construction subset list from the "HB Interior Construction
            Subset" component. Note that None values in this list correspond to
            no change to the given construction in the base_constr_set_.
        _subface_subset_: A construction subset list from the "HB Subface Subset"
            component. Note that None values in this list correspond to no
            change to the given construction in the base_constr_set_.

    Returns:
        constr_set: A ConstructionSet object that can be assigned to Honeybee
            Rooms in order to specify all default constructions on the Room.
"""

ghenv.Component.Name = "HB ConstructionSet"
ghenv.Component.NickName = 'ConstructionSet'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = "3"

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

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
    # get the base construction set
    name = clean_and_id_ep_string('ConstructionSet') if _name_ is None else \
        clean_ep_string(_name_)
    if base_constr_set_ is None:
        constr_set = ConstructionSet(name)
    else:
        if isinstance(base_constr_set_, str):
            base_constr_set_ = construction_set_by_identifier(base_constr_set_)
        constr_set = base_constr_set_.duplicate()
        constr_set.identifier = name
        if _name_ is not None:
            constr_set.display_name = _name_

    # go through each input construction subset and assign it to the set
    if len(_exterior_subset_) != 0:
        assert len(_exterior_subset_) == 3, 'Input _exterior_subset_ is not valid.'
        if _exterior_subset_[0] is not None:
            constr_set.wall_set.exterior_construction = _exterior_subset_[0]
        if _exterior_subset_[1] is not None:
            constr_set.roof_ceiling_set.exterior_construction = _exterior_subset_[1]
        if _exterior_subset_[2] is not None:
            constr_set.floor_set.exterior_construction = _exterior_subset_[2]
    
    if len(_ground_subset_) != 0:
        assert len(_ground_subset_) == 3, 'Input _ground_subset_ is not valid.'
        if _ground_subset_[0] is not None:
            constr_set.wall_set.ground_construction = _ground_subset_[0]
        if _ground_subset_[1] is not None:
            constr_set.roof_ceiling_set.ground_construction = _ground_subset_[1]
        if _ground_subset_[2] is not None:
            constr_set.floor_set.ground_construction = _ground_subset_[2]
    
    if len(_interior_subset_) != 0:
        assert len(_interior_subset_) == 6, 'Input _interior_subset_ is not valid.'
        if _interior_subset_[0] is not None:
            constr_set.wall_set.interior_construction = _interior_subset_[0]
        if _interior_subset_[1] is not None:
            constr_set.roof_ceiling_set.interior_construction = _interior_subset_[1]
        if _interior_subset_[2] is not None:
            constr_set.floor_set.interior_construction = _interior_subset_[2]
        if _interior_subset_[3] is not None:
            constr_set.aperture_set.interior_construction = _interior_subset_[3]
        if _interior_subset_[4] is not None:
            constr_set.door_set.interior_construction = _interior_subset_[4]
        if _interior_subset_[5] is not None:
            constr_set.door_set.interior_glass_construction = _interior_subset_[5]
    
    if len(_subface_subset_) != 0:
        assert len(_subface_subset_) == 6, 'Input _subface_subset_ is not valid.'
        if _subface_subset_[0] is not None:
            constr_set.aperture_set.window_construction = _subface_subset_[0]
        if _subface_subset_[1] is not None:
            constr_set.aperture_set.skylight_construction = _subface_subset_[1]
        if _subface_subset_[2] is not None:
            constr_set.aperture_set.operable_construction = _subface_subset_[2]
        if _subface_subset_[3] is not None:
            constr_set.door_set.exterior_construction = _subface_subset_[3]
        if _subface_subset_[4] is not None:
            constr_set.door_set.overhead_construction = _subface_subset_[4]
        if _subface_subset_[5] is not None:
            constr_set.door_set.exterior_glass_construction = _subface_subset_[5]
