# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create an EnergyPlus opaque construction. Material inputs can be either the
identifiers of materials within the library or a custom material made with any
of the EnergyPlus Material components.
_
Note that the _materials should be ordered from outermost (exterior) layer to the
innermost (interior) layer.
-

    Args:
        _name: Text to set the name for the Construction and to be incorporated
            into a unique Construction identifier.
        _materials: List of materials in the construction (from exterior to interior).
            These materials can be either fully-detailed material objects built
            with the material components or text for a material identifier to be
            looked up in the opaque material library.  Note that a native Grasshopper
            "Merge" component can be used to help order the materials correctly
            for the input here.
    
    Returns:
        constr: An opaque construction that can be assigned to Honeybee
            Faces or ConstructionSets.
"""

ghenv.Component.Name = "HB Opaque Construction"
ghenv.Component.NickName = 'OpaqueConstr'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = "1 :: Constructions"
ghenv.Component.AdditionalHelpFromDocStrings = "4"

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.construction.opaque import OpaqueConstruction
    from honeybee_energy.lib.materials import opaque_material_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    material_objs = []
    for material in _materials:
        if isinstance(material, str):
            material = opaque_material_by_identifier(material)
        material_objs.append(material)

    constr = OpaqueConstruction(clean_and_id_ep_string(_name), material_objs)
    constr.display_name = _name
