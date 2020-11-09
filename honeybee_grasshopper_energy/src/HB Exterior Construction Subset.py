# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a list of exterior constructions that can be used to edit or create a
ConstructionSet object.
-

    Args:
        _exterior_wall_: A construction object for exterior walls (or text for
            the identifier of the construction within the library).
        _exterior_roof_: A construction object for exterior roofs (or text for
            the identifier of the construction within the library).
        _exposed_floor_: A construction object for exposed floors (or text for
            the identifier of the construction within the library).
    
    Returns:
        exterior_set: A list of exterior constructions that can be used to edit
            or create a ConstructionSet object.
"""

ghenv.Component.Name = "HB Exterior Construction Subset"
ghenv.Component.NickName = 'ExteriorSubset'
ghenv.Component.Message = '1.1.0'
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
if _exterior_wall_ is not None:
    _exterior_wall_ = opaque_constr(_exterior_wall_, '_exterior_wall_')
if _exterior_roof_ is not None:
    _exterior_roof_ = opaque_constr(_exterior_roof_, '_exterior_roof_')
if _exposed_floor_ is not None:
    _exposed_floor_ = opaque_constr(_exposed_floor_, '_exposed_floor_')


# return the final list from the component
exterior_set = [_exterior_wall_, _exterior_roof_, _exposed_floor_]
