# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a list of exterior subface (apertures + doors) constructions that can be
used to edit or create a ConstructionSet object.
-

    Args:
        _window_: A construction object for apertures with an Outdoors boundary
            condition and a Wall face type for their parent face. This can also
            be text for the identifier of the construction within the library.
        _skylight_: A construction object for apertures with an Outdoors boundary
            condition and a RoofCeiling or Floor face type for their parent face.
            This can also be text for the identifier of the construction within
            the library.
        _operable_: A construction object for apertures with an Outdoors boundary
            condition and True is_operable property. This can also be text for
            the identifier of the construction within the library.
        _exterior_door_: A construction object for opaque doors with an Outdoors
            boundary condition and a Wall face type for their parent face. This
            can also be text for the identifier of the construction within
            the library.
        _overhead_door_: A construction object for opaque doors with an Outdoors
            boundary condition and a RoofCeiling or Floor face type for their
            parent face. This can also be text for the identifier of the construction
            within the library.
        _glass_door_: A construction object for all glass doors with an Outdoors
            boundary condition. This can also be text for the identifier of the
            construction within the library.

    Returns:
        subface_set: A list of exterior subface constructions that can be used
            to edit or create a ConstructionSet object.
"""

ghenv.Component.Name = 'HB Subface Subset'
ghenv.Component.NickName = 'SubfaceSubset'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:  # import honeybee_energy dependencies
    from honeybee_energy.construction.opaque import OpaqueConstruction
    from honeybee_energy.construction.window import WindowConstruction
    from honeybee_energy.construction.windowshade import WindowConstructionShade
    from honeybee_energy.construction.dynamic import WindowConstructionDynamic
    from honeybee_energy.lib.constructions import opaque_construction_by_identifier, \
        window_construction_by_identifier
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


def window_constr(construction, input_name):
    """Get an WindowConstrucion from the library if it's a string."""
    if isinstance(construction, str):
        return window_construction_by_identifier(construction)
    else:
        win_cls = (WindowConstruction, WindowConstructionShade, WindowConstructionDynamic)
        assert isinstance(construction, win_cls), 'Expected WindowConstruction ' \
            'for {}. Got {}'.format(input_name, type(construction))
    return construction


# go through each input construction
if _window_ is not None:
    _window_ = window_constr(_window_, '_window_')
if _skylight_ is not None:
    _skylight_ = window_constr(_skylight_, '_skylight_')
if _operable_ is not None:
    _operable_ = window_constr(_operable_, '_operable_')
if _exterior_door_ is not None:
    _exterior_door_ = opaque_constr(_exterior_door_, '_exterior_door_')
if _overhead_door_ is not None:
    _overhead_door_ = opaque_constr(_overhead_door_, '_overhead_door_')
if _glass_door_ is not None:
    _glass_door_ = window_constr(_glass_door_, '_glass_door_')


# return the final list from the component
subface_set = [_window_, _skylight_, _operable_, _exterior_door_,
               _overhead_door_, _glass_door_]
