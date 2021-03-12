# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a material for a shade layer in a window construction (like a roller shade).
This material can be plugged into the "HB Window Construction" component.
_
Reflectance and emissivity properties are assumed to be the same on both sides of
the shade. Shades are considered to be perfect diffusers.
-

    Args:
        _name: Text to set the name for the material and to be incorporated into
            a unique material identifier.
        _thickness: Number for the thickness of the shade layer in meters.
        _transmittance_:  Number between 0 and 1 for the transmittance of both solar
            radiation and visible light through the shade. (Default: 0.4, which
            is typical of a white diffusing shade).
        _reflectance_: Number between 0 and 1 for the reflectance of both solar
            radiation and visible light off of the shade. (Default: 0.5,
            which is typical of a white diffusing shade).
        _t_infrared_: Long-wave hemisperical transmittance of the shade. (Default: 0).
        _emissivity_: Number between 0 and 1 for the infrared hemispherical
            emissivity of the shade. (Default: 0.9, which is typical of most
            diffusing shade materials).
        _conductivity_: Number for the thermal conductivity of the shade in
            W/m-K. (Default: 0.05, typical of cotton shades).
        _dist_to_glass_: A number between 0.001 and 1.0 for the distance between the
            shade and neighboring glass layers [m]. (Default: 0.05 (50 mm)).
        _open_mult_: Factor between 0 and 1 that is multiplied by the area at the top,
            bottom and sides of the shade for air flow calculations. (Default: 0.5).
        _permeability_: The fraction of the shade surface that is open to air flow.
            Must be between 0 and 0.8. (Default: 0 for no permeability).

    Returns:
        mat: A material for a shade layer in a window construction (like a roller
            shade) that can be assigned to a Honeybee Window construction.
"""

ghenv.Component.Name = 'HB Shade Material'
ghenv.Component.NickName = 'ShadeMat'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '1 :: Constructions'
ghenv.Component.AdditionalHelpFromDocStrings = '6'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.material.shade import EnergyWindowMaterialShade
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set the default material properties
    _transmittance_ = 0.4 if _transmittance_ is None else _transmittance_
    _reflectance_ = 0.5 if _reflectance_ is None else _reflectance_
    _t_infrared_ = 0 if _t_infrared_ is None else _t_infrared_
    _emissivity_ = 0.9 if _emissivity_ is None else _emissivity_
    _conductivity_ = 0.9 if _conductivity_ is None else _conductivity_
    _dist_to_glass_ = 0.05 if _dist_to_glass_ is None else _dist_to_glass_
    _open_mult_ = 0.5 if _open_mult_ is None else _open_mult_
    _permeability_ = 0.0 if _permeability_ is None else _permeability_
    name = clean_and_id_ep_string('ShadeMaterial') if _name_ is None else \
        clean_ep_string(_name_)

    # create the material
    mat = EnergyWindowMaterialShade(
        name, _thickness, _transmittance_, _reflectance_,
        _transmittance_, _reflectance_, _t_infrared_, _emissivity_, _conductivity_,
        _dist_to_glass_, _open_mult_, _permeability_)
    if _name_ is not None:
        mat.display_name = _name_
