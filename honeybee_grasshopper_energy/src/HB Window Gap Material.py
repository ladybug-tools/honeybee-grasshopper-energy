# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a window gas gap material that corresponds to a layer in a window construction.
This material can be plugged into the "HB Window Construction" component.
-

    Args:
        _name_: Text to set the name for the material and to be incorporated into
            a unique material identifier.
        _thickness_: Number for the thickness of the air gap layer in
            meters. (Default: 0.0125 m).
        _gas_types_: A list of text describing the types of gas in the gap.
            Text must be one of the following: 'Air', 'Argon', 'Krypton', 'Xenon'.
            Default: ['Air']
        _gas_ratios_: A list of text describing the volumetric fractions of gas
            types in the mixture.  This list must align with the gas_types
            input list. Default: Equal amout of gases for each type.

    Returns:
        mat: A window gas gap material that describes a layer in a window construction
            and can be assigned to a Honeybee Window construction.
"""

ghenv.Component.Name = 'HB Window Gap Material'
ghenv.Component.NickName = 'GapMat'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '1 :: Constructions'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.material.gas import EnergyWindowMaterialGas, \
        EnergyWindowMaterialGasMixture
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set the default material properties
    _thickness_ = 0.0125 if _thickness_ is None else _thickness_
    _gas_types_ = ['Air'] if len(_gas_types_) == 0 else _gas_types_
    _gas_ratios_ = [1 / len(_gas_types_)] * len(_gas_types_) if \
        len(_gas_ratios_) == 0 else _gas_ratios_
    assert len(_gas_types_) == len(_gas_ratios_), \
        'Length of _gas_types_ does not equal length of _gas_ratios_.'
    name = clean_and_id_ep_string('GapMaterial') if _name_ is None else \
        clean_ep_string(_name_)

    # create the material
    if len(_gas_types_) == 1:
        mat = EnergyWindowMaterialGas(name, _thickness_, _gas_types_[0])
    else:
        mat = EnergyWindowMaterialGasMixture(name, _thickness_, _gas_types_, _gas_ratios_)
    if _name_ is not None:
        mat.display_name = _name_
