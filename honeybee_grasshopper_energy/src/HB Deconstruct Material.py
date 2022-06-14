# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Deconstruct a material into its constituient attributes and values.
-

    Args:
        _mat: A material to be deconstructed. This can also be text for a
            material to be looked up in the material library.

    Returns:
        values: List of values for the attributes that define the material.
        attr_names: List of text that is the same length as the values, which
            notes the attribute name for each value.
        r_val_si: R-value of the material in m2-K/W. Note that R-values do NOT
            include the resistance of air films on either side of the material.
        r_val_ip: R-value of the material in h-ft2-F/Btu. Note that R-values do NOT
            include the resistance of air films on either side of the material.
"""

ghenv.Component.Name = "HB Deconstruct Material"
ghenv.Component.NickName = 'DecnstrMat'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = "1 :: Constructions"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

import re

try:  # import the honeybee-energy dependencies
    from honeybee_energy.reader import parse_idf_string
    from honeybee_energy.lib.materials import opaque_material_by_identifier
    from honeybee_energy.lib.materials import window_material_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))
try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
try:
    from ladybug.datatype.rvalue import RValue
    from ladybug.datatype.uvalue import UValue
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # check the input
    if isinstance(_mat, str):
        try:
            _mat = opaque_material_by_identifier(_mat)
        except ValueError:
            _mat = window_material_by_identifier(_mat)

    # get the values and attribute names
    mat_str = str(_mat)
    values = parse_idf_string(mat_str)
    attr_name_pattern1 = re.compile(r'!- (.*)\n')
    attr_name_pattern2 = re.compile(r'!- (.*)$')
    attr_names = attr_name_pattern1.findall(mat_str) + \
        attr_name_pattern2.findall(mat_str)

    # get the r-value
    try:
        r_val_si = _mat.r_value
        r_val_ip = RValue().to_ip([r_val_si], 'm2-K/W')[0][0]

        # give a warning if there's a negative R-value for a vertical surface
        if r_val_si <= 0:
            msg = 'Material "{}" has an overall R-value that is less than the\n' \
                'resistance of vertically-oriented air films. This indicates that the ' \
                'construction is only suitable for horizontal/skylight geometry.'.format(
                    _mat.display_name)
            print(msg)
            give_warning(ghenv.Component, msg)
    except AttributeError:
        r_val_si = 'varies'
        r_val_ip = 'varies'

    # re-order the E+ attributes of opaque constructions to align with component
    if len(attr_names) == 9:
        values.insert(5, values.pop(1))
        attr_names.insert(5, attr_names.pop(1))
