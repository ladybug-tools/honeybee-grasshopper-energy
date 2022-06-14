# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a list of interior constructions that can be used to edit or create a
ConstructionSet object.
-

    Args:
        _interior_wall_: A construction object for interior walls (or text for
            the identifier of the construction within the library).
        _ceiling_: A construction object for ceilings (or text for the identifier of
            the construction within the library).
        _interior_floor_: A construction object for interior floors (or text for
            the identifier of the construction within the library).
        _interior_window_: A construction object for all apertures with a Surface
            boundary condition. This can also be text for the identifier of the
            construction within the library.
        _interior_door_: A construction object for all opaque doors with a Surface
            boundary condition. This can also be text for the identifier of the
            construction within the library.
        _int_glass_door_: A construction object for all glass doors with a Surface
            boundary condition. This can also be text for the identifier of the
            construction within the library.
    
    Returns:
        interior_set: A list of interior constructions that can be used to edit
            or create a ConstructionSet object.
"""

ghenv.Component.Name = 'HB Interior Construction Subset'
ghenv.Component.NickName = 'InteriorSubset'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:  # import honeybee_energy dependencies
    from honeybee_energy.construction.opaque import OpaqueConstruction
    from honeybee_energy.construction.window import WindowConstruction
    from honeybee_energy.construction.dynamic import WindowConstructionDynamic
    from honeybee_energy.lib.constructions import opaque_construction_by_identifier, \
        window_construction_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))
try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def opaque_constr(construction, input_name):
    """Get an OpaqueConstrucion from the library if it's a string."""
    if isinstance(construction, str):
        return opaque_construction_by_identifier(construction)
    else:
        assert isinstance(construction, OpaqueConstruction), \
            'Expected OpaqueConstruction for {}. Got {}'.format(
                input_name, type(construction))
    return construction


def window_constr(construction, input_name):
    """Get a WindowConstrucion from the library if it's a string."""
    if isinstance(construction, str):
        return window_construction_by_identifier(construction)
    else:
        win_cls = (WindowConstruction, WindowConstructionDynamic)
        assert isinstance(construction, win_cls), \
            'Expected WindowConstruction for {}. Got {}'.format(
                input_name, type(construction))
    return construction


def check_symmetric(constr_type, construction):
    """Give a warning on the component that a construction is asymmetric."""
    if not construction.is_symmetric:   # check whether the construction is symmetric.
        message = 'Input {} is asymmetric (materials in reversed order ' \
            'do not equal those in the current order).\nThis can cause issues if the ' \
            'resulting constr_set is applied across multiple Rooms.\nMaterials: {}'.format(
                constr_type, construction.layers)
        give_warning(ghenv.Component, message)


# go through each input construction
if _interior_wall_ is not None:
    _interior_wall_ = opaque_constr(_interior_wall_, '_interior_wall_')
    check_symmetric('_interior_wall_', _interior_wall_)
if _ceiling_ is not None:
    _ceiling_ = opaque_constr(_ceiling_, '_ceiling_')
if _interior_floor_ is not None:
    _interior_floor_ = opaque_constr(_interior_floor_, '_interior_floor_')
if _interior_window_ is not None:
    _interior_window_ = window_constr(_interior_window_, '_interior_window_')
    check_symmetric('_interior_window_', _interior_window_)
if _interior_door_ is not None:
    _interior_door_ = opaque_constr(_interior_door_, '_interior_door_')
    check_symmetric('_interior_door_', _interior_door_)
if _int_glass_door_ is not None:
    _int_glass_door_ = window_constr(_int_glass_door_, '_int_glass_door_')
    check_symmetric('_int_glass_door_', _int_glass_door_)

# check whether the ceiling has the revered materials of the floor
if _ceiling_ is not None or _interior_floor_ is not None:
    if _ceiling_ is None or _interior_floor_ is  None or \
            _ceiling_.layers != list(reversed(_interior_floor_.layers)):
        warn = '_ceiling_ does not have materials in reversed ' \
            ' order of the _interior_floor_.\nThis can cause issues if the ' \
            'resulting constr_set is applied across multiple Rooms.'
        give_warning(ghenv.Component, warn)
        print(warn)

# return the final list from the component
interior_set = [_interior_wall_, _ceiling_, _interior_floor_, _interior_window_,
                _interior_door_, _int_glass_door_]
