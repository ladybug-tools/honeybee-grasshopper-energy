# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a custom gas gap material that corresponds to a layer in a window construction.
This material can be plugged into the "HB Window Construction" component.
_
This object allows you to specify specific values for conductivity,
viscosity and specific heat through the following formula:
    property = A + (B * T)
where:
    A, B = regression coefficients for the gas
    T = temperature [K]
-

    Args:
        _name: Text to set the name for the material and to be incorporated into
            a unique material identifier.
        _thickness: Number for the thickness of the gas gap layer [m].
            Default: 0.0125
        _conductivity_a: First conductivity coefficient.
            Or condictivity in [W/m-K] if b coefficient is 0.
        _viscosity_a: First viscosity coefficient.
            Or viscosity in [kg/m-s] if b coefficient is 0.
        _specific_heat_a: First specific heat coefficient.
            Or the specific heat in [J/kg-K] if b coefficient is 0.
        _conductivity_b_: Second conductivity coefficient. Default = 0.
        _viscosity_b_: Second viscosity coefficient. Default = 0.
        _specific_heat_b_: Second specific heat coefficient. Default = 0.
        _spec_heat_ratio_: A number for the the ratio of the specific heat at
            contant pressure, to the specific heat at constant volume.
            Default is 1.0 for Air.
        _mol_weight_: Number between 20 and 200 for the mass of 1 mol of
            the substance in grams. Default is 20.0.
    
    Returns:
        mat: A custom gas gap material that describes a layer in a window construction
            and can be assigned to a Honeybee Window construction.
"""

ghenv.Component.Name = "HB Custom Window Gap Material"
ghenv.Component.NickName = 'CustomGapMat'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = "1 :: Constructions"
ghenv.Component.AdditionalHelpFromDocStrings = "6"

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.material.gas import EnergyWindowMaterialGasCustom
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set the default material properties
    _conductivity_b_ = 0 if _conductivity_b_ is None else _conductivity_b_
    _viscosity_b_ = 0 if _viscosity_b_ is None else _viscosity_b_
    _specific_heat_b_ = 0 if _specific_heat_b_ is None else _specific_heat_b_
    _spec_heat_ratio_ = 1.0 if _spec_heat_ratio_ is None else _spec_heat_ratio_
    _mol_weight_ = 20.0 if _mol_weight_ is None else _mol_weight_

    # set the non-exposed inputs
    _conductivity_c_, _viscosity_c_, _specific_heat_c_ = 0, 0, 0

    # create the material
    mat = EnergyWindowMaterialGasCustom(
        clean_and_id_ep_string(_name), _thickness,
        _conductivity_a, _viscosity_a, _specific_heat_a,
        _conductivity_b_, _viscosity_b_, _specific_heat_b_,
        _conductivity_c_, _viscosity_c_, _specific_heat_c_,
        _spec_heat_ratio_, _mol_weight_)
    mat.display_name = _name
