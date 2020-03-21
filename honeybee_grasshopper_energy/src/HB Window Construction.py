# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create an EnergyPlus window construction. Material inputs can be either the name of
a material within the material library or a custom material made with any of the
EnergyPlus Material components.
_
Note that the _materials should be ordered from outermost (exterior) layer to the
innermost (interior) layer.
-

    Args:
        _name: A unique name for the window construction.
        _materials: List of materials in the construction (from exterior to interior).
            These materials can be either fully-detailed material objects built
            with the material components or text for a material name to be looked
            up in the window material library. Note that a native Grasshopper
            "Merge" component can be used to help order the materials correctly
            for the input here.
    
    Returns:
        constr: A window construction that can be assigned to Honeybee
            Apertures or ConstructionSets.
"""

ghenv.Component.Name = "HB Window Construction"
ghenv.Component.NickName = 'WindowConstr'
ghenv.Component.Message = '0.1.1'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = "1 :: Constructions"
ghenv.Component.AdditionalHelpFromDocStrings = "4"


try:  # import the honeybee-energy dependencies
    from honeybee_energy.construction.window import WindowConstruction
    from honeybee_energy.lib.materials import window_material_by_name
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
            material = window_material_by_name(material)
        material_objs.append(material)
    
    constr = WindowConstruction(_name, material_objs)
