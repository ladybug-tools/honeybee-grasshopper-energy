# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create an EnergyPlus window construction. Material inputs can be either the
identifiers of materials within the library or a custom material made with any
of the EnergyPlus Material components.
_
Note that the _materials should be ordered from outermost (exterior) layer to the
innermost (interior) layer.
-

    Args:
        _name_: Text to set the name for the Construction and to be incorporated
            into a unique Construction identifier.
        _materials: List of materials in the construction (from exterior to interior).
            These materials can be either fully-detailed material objects built
            with the material components or text for a material identifier to be
            looked up in the window material library. Note that a native Grasshopper
            "Merge" component can be used to help order the materials correctly
            for the input here.
        frame_: An optional window frame material to denote the frame that surrounds
            the window construction. Frame materials can be created using the
            "HB Window Frame" component.

    Returns:
        constr: A window construction that can be assigned to Honeybee
            Apertures or ConstructionSets.
"""

ghenv.Component.Name = "HB Window Construction"
ghenv.Component.NickName = 'WindowConstr'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = "1 :: Constructions"
ghenv.Component.AdditionalHelpFromDocStrings = "4"

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.construction.window import WindowConstruction
    from honeybee_energy.lib.materials import window_material_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    name = clean_and_id_ep_string('WindowConstruction') if _name_ is None else \
        clean_ep_string(_name_)

    material_objs = []
    for material in _materials:
        if isinstance(material, str):
            material = window_material_by_identifier(material)
        material_objs.append(material)

    constr = WindowConstruction(name, material_objs, frame_)
    if _name_ is not None:
        constr.display_name = _name_
