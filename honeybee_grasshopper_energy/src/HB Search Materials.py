# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Search for available Materials within the honeybee energy standards library.
-

    Args:
        keywords_: Optional keywords to be used to narrow down the output list of
            materials. If nothing is input here, all available materials
            will be output.
        join_words_: If False or None, this component will automatically split
            any strings of multiple keywords (spearated by spaces) into separate
            keywords for searching. This results in a greater liklihood of
            finding an item in the search but it may not be appropropriate for
            all cases. You may want to set it to True when you are searching for
            a specific phrase that includes spaces. Default: False.
    
    Returns:
        opaque_mats: A list of opaque materials within the honeybee energy
            standards library (filtered by keywords_ if they are input).
        window_mats: A list of window materials within the honeybee energy
            standards library (filtered by keywords_ if they are input).
"""

ghenv.Component.Name = "HB Search Materials"
ghenv.Component.NickName = 'SearchMats'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = "1 :: Constructions"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:  # import the honeybee-core dependencies
    from honeybee.search import filter_array_by_keywords
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.lib.materials import OPAQUE_MATERIALS
    from honeybee_energy.lib.materials import WINDOW_MATERIALS
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))


if len(keywords_) == 0:
    opaque_mats = sorted(OPAQUE_MATERIALS)
    window_mats = sorted(WINDOW_MATERIALS)
else:
    split_words = True if join_words_ is None else not join_words_
    opaque_mats = sorted(filter_array_by_keywords(OPAQUE_MATERIALS, keywords_, split_words))
    window_mats = sorted(filter_array_by_keywords(WINDOW_MATERIALS, keywords_, split_words))
