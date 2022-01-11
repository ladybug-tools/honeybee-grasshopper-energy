# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a window material to describe a single glass pane corresponding to a
layer in a window construction. This material can be plugged into the "HB Window
Construction" component.
-

    Args:
        _name: Text to set the name for the material and to be incorporated into
            a unique material identifier.
        _thickness: Number for the thickness of the glass layer [m]. Typical values
            range from 0.003 meters (3 mm) to 0.012 meters (12 mm).
        _transmittance_: Number between 0 and 1 for the transmittance of both solar
            radiation and visible light through the glass at normal
            incidence. (Default: 0.85 for clear uncoated glass).
        _reflectance_: Number between 0 and 1 for the reflectance of both solar
            radiation and visible light off of the front side of the glass at
            normal incidence. (Default: 0.075 for clear uncoated glass).
        _t_infrared_: Long-wave transmittance of the glass at normal
            incidence. (Default: 0).
        _emiss_front_: Number between 0 and 1 for the infrared hemispherical
            emissivity of the front side of the glass. (Defaul: 0.84, which
            is typical of clear glass).
        _emiss_back_: Number between 0 and 1 for the infrared hemispherical
            emissivity of the back side of the glass. (Default: 0.84, which
            is typical of clear glass).
        _conductivity_: Number for the thermal conductivity of the glass in
            W/m-K. (Default: 0.9, whih is typical of clear glass).

    Returns:
        mat: A window material that describes a single glass pane and can be
            assigned to a Honeybee Window construction.
"""

ghenv.Component.Name = 'HB Glass Material'
ghenv.Component.NickName = 'GlassMat'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '1 :: Constructions'
ghenv.Component.AdditionalHelpFromDocStrings = '6'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.material.glazing import EnergyWindowMaterialGlazing
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set the default material properties
    _transmittance_ = 0.85 if _transmittance_ is None else _transmittance_
    _reflectance_ = 0.075 if _reflectance_ is None else _reflectance_
    _t_infrared_ = 0 if _t_infrared_ is None else _t_infrared_
    _emiss_front_ = 0.84 if _emiss_front_ is None else _emiss_front_
    _emiss_back_ = 0.84 if _emiss_back_ is None else _emiss_back_
    _conductivity_ = 0.9 if _conductivity_ is None else _conductivity_
    name = clean_and_id_ep_string('GlassMaterial') if _name_ is None else \
        clean_ep_string(_name_)

    # create the material
    mat = EnergyWindowMaterialGlazing(
        name, _thickness, _transmittance_, _reflectance_,
        _transmittance_, _reflectance_, _t_infrared_, _emiss_front_, _emiss_back_,
        _conductivity_)
    if _name_ is not None:
        mat.display_name = _name_
