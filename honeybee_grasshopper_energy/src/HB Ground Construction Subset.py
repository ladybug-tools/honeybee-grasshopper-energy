# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a list of ground constructions that can be used to edit or create a
ConstructionSet object.
-

    Args:
        _ground_wall_: A construction object for underground walls (or text for
            the identifier of the construction within the library).
        _ground_roof_: A construction object for underground roofs (or text for
            the identifier of the construction within the library).
        _ground_floor_: A construction object for ground-contact floors (or text
            for the identifier of the construction within the library).
    
    Returns:
        ground_set: A list of ground constructions that can be used to edit
            or create a ConstructionSet object.
"""

ghenv.Component.Name = "HB Ground Construction Subset"
ghenv.Component.NickName = 'GroundSubset'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = "4"

try:  # import honeybee_energy dependencies
    from honeybee_energy.construction.opaque import OpaqueConstruction
    from honeybee_energy.lib.constructions import opaque_construction_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))


def opaque_constr(construction, input_name):
    """Get an OpaqueConstrucion from the library if it's a string."""
    if isinstance(construction, str):
        return opaque_construction_by_identifier(construction)
    else:
        assert isinstance(construction, OpaqueConstruction), \
            'Expected OpaqueConstruction for {}. Got {}'.format(
                input_name, type(construction))
    return construction


# go through each input construction
if _ground_wall_ is not None:
    _ground_wall_ = opaque_constr(_ground_wall_, '_ground_wall_')
if _ground_roof_ is not None:
    _ground_roof_ = opaque_constr(_ground_roof_, '_ground_roof_')
if _ground_floor_ is not None:
    _ground_floor_ = opaque_constr(_ground_floor_, '_ground_floor_')


# return the final list from the component
ground_set = [_ground_wall_, _ground_roof_, _ground_floor_]
