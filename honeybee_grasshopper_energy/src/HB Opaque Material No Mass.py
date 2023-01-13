# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create an opaque material that has no mass, which can be plugged into the
"HB Opaque Construction" component.
-

    Args:
        _name: Text to set the name for the material and to be incorporated into
            a unique material identifier.
        _r_value: Number for the R-value of the material [m2-K/W].
        _roughness_: Text describing the relative roughness of a particular material.
            Must be one of the following: 'VeryRough', 'Rough', 'MediumRough',
            'MediumSmooth', 'Smooth', 'VerySmooth'. (Default: 'MediumRough').
        _therm_absp_: A number between 0 and 1 for the fraction of incident long
            wavelength radiation that is absorbed by the material. (Default: 0.9).
        _sol_absp_: A number between 0 and 1 for the fraction of incident solar
            radiation absorbed by the material. (Default: 0.7).
        _vis_absp_: A number between 0 and 1 for the fraction of incident
            visible wavelength radiation absorbed by the material.
            Default value is the same as the _sol_absp_.

    Returns:
        mat: A no-mass opaque material that can be assigned to a Honeybee
            Opaque construction.
"""

ghenv.Component.Name = "HB Opaque Material No Mass"
ghenv.Component.NickName = 'OpaqueMatNoMass'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = "1 :: Constructions"
ghenv.Component.AdditionalHelpFromDocStrings = "5"

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.material.opaque import EnergyMaterialNoMass
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
    name = clean_and_id_ep_string('OpaqueNoMassMaterial') if _name_ is None else \
        clean_ep_string(_name_)

    # create the material
    mat = EnergyMaterialNoMass(name, _r_value, _roughness_, _therm_absp_,
                               _sol_absp_, _vis_absp_)
    if _name_ is not None:
        mat.display_name = _name_
