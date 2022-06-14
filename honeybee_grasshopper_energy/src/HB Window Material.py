# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a simple window material to describe an entire glazing system, including
glass, gaps, and frame. This material can be plugged into the "HB Window
Construction" component.
-

    Args:
        _name: Text to set the name for the material and to be incorporated into
            a unique material identifier.
        _u_factor: A number for the U-factor of the glazing system [W/m2-K]
            including standard air gap resistances on either side of the
            glazing system.
        _shgc: A number between 0 and 1 for the solar heat gain coefficient
            of the glazing system. This includes both directly transmitted solar
            heat as well as solar heat that is absorbed by the glazing system and
            conducts towards the interior.
        _t_vis_: A number between 0 and 1 for the visible transmittance of the
            glazing system. (Default: 0.6).

    Returns:
        mat: A window material that describes an entire glazing system, including
            glass, gaps, and frame and can be assigned to a Honeybee Window
            construction.
"""

ghenv.Component.Name = 'HB Window Material'
ghenv.Component.NickName = 'WindowMat'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '1 :: Constructions'
ghenv.Component.AdditionalHelpFromDocStrings = '6'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.material.glazing import EnergyWindowMaterialSimpleGlazSys
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set the default material properties
    _t_vis_ = 0.6 if _t_vis_ is None else _t_vis_
    name = clean_and_id_ep_string('WindowMaterial') if _name_ is None else \
        clean_ep_string(_name_)

    # create the material
    mat = EnergyWindowMaterialSimpleGlazSys(name, _u_factor, _shgc, _t_vis_)
    if _name_ is not None:
        mat.display_name = _name_
