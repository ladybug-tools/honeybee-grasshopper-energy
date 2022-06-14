# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create an EnergyPlus shade construction. Note that Shade objects in EnergyPlus
do not have layers and are only defined by their exterior reflectance.
-

    Args:
        _name: Text to set the name for the Construction and to be incorporated
            into a unique Construction identifier.
        _sol_ref_: A number between 0 and 1 for the solar reflectance
            of the construction. Default: 0.2.
        _vis_ref_: A number between 0 and 1 for the visible reflectance
            of the construction. Default: 0.2.
        specular_: A boolean to note whether the reflection off the shade
            should be diffuse (False) or specular (True). Set to True if the
            construction is representing a glass facade or a mirror
            material. Default: False.

    Returns:
        constr: A shade construction that can be assigned to Honeybee
            Shades or ConstructionSets.
"""

ghenv.Component.Name = "HB Shade Construction"
ghenv.Component.NickName = 'ShadeConstr'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = "1 :: Constructions"
ghenv.Component.AdditionalHelpFromDocStrings = "4"

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.construction.shade import ShadeConstruction
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

if all_required_inputs(ghenv.Component):
    # set default values
    _sol_ref_ = 0.2 if _sol_ref_ is None else _sol_ref_
    _vis_ref_ = 0.2 if _vis_ref_ is None else _vis_ref_
    specular_ = False if specular_ is None else specular_
    name = clean_and_id_ep_string('ShadeConstruction') if _name_ is None else \
        clean_ep_string(_name_)

    # create the construction
    constr = ShadeConstruction(name, _sol_ref_, _vis_ref_, specular_)
    if _name_ is not None:
        constr.display_name = _name_
