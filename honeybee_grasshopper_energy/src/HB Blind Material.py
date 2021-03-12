# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a material for a blind layer in a window construction.
This material can be plugged into the "HB Window Construction" component.
_
Window blind properties consist of flat, equally-spaced slats.
-

    Args:
        _name: Text to set the name for the material and to be incorporated into
            a unique material identifier.
        _vertical_: Set to "True" to have the blinds be vertically-oriented and set to
            "False" to have them be horizontally-oriented. (Default: False
            for horizontal).
        _slat_width_: The width of slat measured from edge to edge [m]. (Default: 0.025 m).
        _slat_separation_: The distance between each of the slats [m]. (Default: 0.01875 m).
        _slat_thickness_: A number between 0 and 0.1 for the thickness of the slat
            in meters. (Default: 0.001 m).
        _slat_angle_: A number between 0 and 180 for the angle between the slats
            and the glazing normal in degrees. 90 signifies slats that are
            perpendicular to the glass. (Default: 45).
        _conductivity_: Number for the thermal conductivity of the blind material
            [W/m-K]. (Default: 221, typical of aluminum blinds).
        _transmittance_:  Number between 0 and 1 for the transmittance of solar
            radiation and visible light through the blind material. (Default: 0).
        _reflectance_: Number between 0 and 1 for the reflectance of solar
            radiation and visible light off of the blind material. (Default: 0.5,
            which is typical of a painted white blind).
        _t_infrared_: Long-wave hemisperical transmittance of the blind material. (Default: 0).
        _emissivity_: Number between 0 and 1 for the infrared hemispherical emissivity
            of the blind material. (Default: 0.9, which is typical of most
            painted blinds).
        _dist_to_glass_: A number between 0.001 and 1.0 for the distance between the
            blind edge and neighboring glass layers [m]. (Default: 0.05 m).
        _open_mult_: Factor between 0 and 1 that is multiplied by the area at the top,
            bottom and sides of the blind for air flow calculations. (Default: 0.5).

    Returns:
        mat: A material for a blind layer in a window construction that can be
            assigned to a Honeybee Window construction.
"""

ghenv.Component.Name = 'HB Blind Material'
ghenv.Component.NickName = 'BlindMat'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '1 :: Constructions'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.material.shade import EnergyWindowMaterialBlind
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set the default material properties
    orientation = 'Vertical' if _vertical_ else 'Horizontal'
    _slat_width_ = 0.025 if _slat_width_ is None else _slat_width_
    _slat_separation_ = 0.01875 if _slat_separation_ is None else _slat_separation_
    _slat_thickness_ = 0.001 if _slat_thickness_ is None else _slat_thickness_
    _slat_angle_ = 45 if _slat_angle_ is None else _slat_angle_
    _conductivity_ = 221 if _conductivity_ is None else _conductivity_
    _transmittance_ = 0 if _transmittance_ is None else _transmittance_
    _reflectance_ = 0.5 if _reflectance_ is None else _reflectance_
    _t_infrared_ = 0 if _t_infrared_ is None else _t_infrared_
    _emissivity_ = 0.9 if _emissivity_ is None else _emissivity_
    _dist_to_glass_ = 0.05 if _dist_to_glass_ is None else _dist_to_glass_
    _open_mult_ = 0.5 if _open_mult_ is None else _open_mult_
    name = clean_and_id_ep_string('BlindMaterial') if _name_ is None else \
        clean_ep_string(_name_)

    # create the material
    mat = EnergyWindowMaterialBlind(
        name, orientation, _slat_width_, _slat_separation_,
        _slat_thickness_, _slat_angle_, _conductivity_, _transmittance_,
        _reflectance_, _transmittance_,  _reflectance_, _t_infrared_, _emissivity_,
        _dist_to_glass_, _open_mult_)
    if _name_ is not None:
        mat.display_name = _name_
