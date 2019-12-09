# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create an EnergyPlus opaque construction. Layer inputs can be either the name of
a material within the material library or a custom material made with any of the
EnergyPlus Material components.
_
Note that _layer_1 is always the outermost (exterior) layer and the last layer
in the component is always the innermost (interior) layer.
_
To add more layers in the construction, zoom into the component and hit the
lowest "+" sign that shows up on the input side. 
_
To remove layers from the construction, zoom into the component and hit the
lowest "-" sign that shows up on the input side.
-

    Args:
        _name: A unique name for the opaque construction.
        _layer_1: The first outer-most material layer of the construction.
        _layer_2: The second outer-most material layer of the construction.
        _layer_3: The third outer-most material layer of the construction.
    Returns:
        constr: An opaque construction that can be assigned to Honeybee
            Faces or ConstructionSets.
"""

ghenv.Component.Name = "HB Opaque Construction"
ghenv.Component.NickName = 'OpaqueConstr'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "Energy"
ghenv.Component.SubCategory = "1 :: Construction"
ghenv.Component.AdditionalHelpFromDocStrings = "3"


try:  # import the honeybee-energy dependencies
    from honeybee_energy.construction.opaque import OpaqueConstruction
    from honeybee_energy.lib.materials import opaque_material_by_name
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))
try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

# check that max material layers has not been exceeded
num_inputs = ghenv.Component.Params.Input.Count
if num_inputs > 11:
    raise ValueError("Maximum number of layers in an EnergyPlus opaque construction is 10.\n"
          "Remove the last input you just added to the component.")

# set the names of the component inputs
layer_text = ('first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh',
              'eigth', 'ninth', 'tenth')
description = 'The {} outer-most material layer of the construction.'
for i in range(1, num_inputs):
    input_name = '_layer_' + str(i)
    ghenv.Component.Params.Input[i].NickName = input_name
    ghenv.Component.Params.Input[i].Name = input_name
    ghenv.Component.Params.Input[i].Description = description.format(layer_text[i - 1])


if all_required_inputs(ghenv.Component):
    material_objs = []
    for i in range(1, num_inputs):
        layer_name = ghenv.Component.Params.Input[i].NickName
        exec('material = ' + layer_name)  # Python is wonderful
        if isinstance(material, str):
            material = opaque_material_by_name(material)
        material_objs.append(material)
    
    constr = OpaqueConstruction(_name, material_objs)
