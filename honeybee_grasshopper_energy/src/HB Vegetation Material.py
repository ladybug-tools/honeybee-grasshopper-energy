# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a vegetation material representing both plants and soil, which can be
plugged into the "HB Opaque Construction" component.
_
Note that the underlying models for this material were developed using horizontal
roofs and caution should be taken when applying ito to vertical walls.
-

    Args:
        _name_: Text to set the name for the material and to be incorporated into
            a unique material identifier.
        _plant_height_: A number between 0.005 and 1.0 for the height of plants in the
            vegetation layer [m]. (Default: 0.2 m).
        _leaf_area_ind_: A number between 0.001 and 5.0 for the projected leaf area per unit
            area of soil surface (aka. Leaf Area Index or LAI). Note that
            the fraction of vegetation cover is calculated directly from LAI
            using an empirical relation. (Default: 1.0).
        _leaf_reflect_: A number between 0.05 and 0.5 for the fraction of incident solar
            radiation that is reflected by the leaf surfaces. Solar radiation
            includes the visible spectrum as well as infrared and ultraviolet
            wavelengths. Typical values are 0.18 to 0.25. (Default: 0.22).
        _leaf_emiss_: A number between 0.8 and 1.0 for the ratio of thermal radiation
            emitted from leaf surfaces to that emitted by an ideal black
            body at the same temperature. (Default: 0.95).
        _soil_reflect_: A number between 0 and 1 for the fraction of incident solar
            radiation reflected by the soil material. (Default: 0.3).
        _soil_emiss_: A number between 0 and 1 for the fraction of incident long wavelength
            radiation that is absorbed by the soil material. (Default: 0.9).
        _stomat_resist_: A number between 50 and 300 for the resistance of the plants
            to moisture transport [s/m]. Plants with low values of stomatal resistance
            will result in higher evapotranspiration rates than plants with high
            resistance. (Default: 180).
        _thickness_: Number for the thickness of the soil layer [m]. (Default: 0.1).
        _conductivity_: Number for the thermal conductivity of the soil [W/m-K]. (Default: 0.35).
        _density_: Number for the density of the soil [kg/m3]. (Default: 1100).
        _spec_heat_: Number for the specific heat of the soil [J/kg-K]. (Default: 1200).

    Returns:
        mat: A vegetation material that can be assigned to a Honeybee
            Opaque construction.
"""

ghenv.Component.Name = 'HB Vegetation Material'
ghenv.Component.NickName = 'VegetationMat'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '1 :: Constructions'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.material.opaque import EnergyMaterialVegetation
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))


# set the default material properties
_plant_height_ = 0.2 if _plant_height_ is None else _plant_height_
_leaf_area_ind_ = 1.0 if _leaf_area_ind_ is None else _leaf_area_ind_
_leaf_reflect_ = 0.22 if _leaf_reflect_ is None else _leaf_reflect_
_leaf_emiss_ = 0.95 if _leaf_emiss_ is None else _leaf_emiss_
soil_abs = 0.7 if _soil_reflect_ is None else 1 - _soil_reflect_
_soil_emiss_ = 0.9 if _soil_emiss_ is None else _soil_emiss_
_stomat_resist_ = 180 if _stomat_resist_ is None else _stomat_resist_
_thickness_ = 0.1 if _thickness_ is None else _thickness_
_conductivity_ = 0.35 if _conductivity_ is None else _conductivity_
_density_ = 1100 if _density_ is None else _density_
_spec_heat_ = 1200 if _spec_heat_ is None else _spec_heat_
name = clean_and_id_ep_string('VegetationMaterial') if _name_ is None else \
    clean_ep_string(_name_)

# create the material
mat = EnergyMaterialVegetation(
    name, _thickness_, _conductivity_, _density_, _spec_heat_, 'MediumRough',
    _soil_emiss_, soil_abs, None, _plant_height_, _leaf_area_ind_,
    _leaf_reflect_, _leaf_emiss_, _stomat_resist_
)
if _name_ is not None:
    mat.display_name = _name_
