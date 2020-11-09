# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a standard opaque material, which can be plugged into the "HB Opaque
Construction" component.
-

    Args:
        _name: Text to set the name for the material and to be incorporated into
            a unique material identifier.
        _thickness: Number for the thickness of the material layer [m].
        _conductivity: Number for the thermal conductivity of the material [W/m-K].
        _density: Number for the density of the material [kg/m3].
        _spec_heat: Number for the specific heat of the material [J/kg-K].
        _roughness_: Text describing the relative roughness of the material.
            Must be one of the following: 'VeryRough', 'Rough', 'MediumRough',
            'MediumSmooth', 'Smooth', 'VerySmooth'.
            Default: 'MediumRough'.
        _therm_absp_: A number between 0 and 1 for the fraction of incident
            long wavelength radiation that is absorbed by the material.
            Default: 0.9.
        _sol_absp_: A number between 0 and 1 for the fraction of incident solar
            radiation absorbed by the material. Default: 0.7.
        _vis_absp_: A number between 0 and 1 for the fraction of incident
            visible wavelength radiation absorbed by the material.
            Default value is the same as the _sol_absp_.
    
    Returns:
        mat: A standard opaque material that can be assigned to a Honeybee
            Opaque construction.
"""

ghenv.Component.Name = "HB Opaque Material"
ghenv.Component.NickName = 'OpaqueMat'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = "1 :: Constructions"
ghenv.Component.AdditionalHelpFromDocStrings = "5"

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.material.opaque import EnergyMaterial
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set the default material properties
    _roughness_ = 'MediumRough' if _roughness_ is None else _roughness_
    _therm_absp_ = 0.9 if _therm_absp_ is None else _therm_absp_
    _sol_absp_ = 0.7 if _sol_absp_ is None else _sol_absp_

    # create the material
    mat = EnergyMaterial(
        clean_and_id_ep_string(_name), _thickness, _conductivity, _density,
        _spec_heat, _roughness_, _therm_absp_, _sol_absp_, _vis_absp_)
    mat.display_name = _name
