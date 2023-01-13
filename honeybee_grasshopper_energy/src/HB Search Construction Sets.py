# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Search for available ConstructionSets within the honeybee energy standards library.
-

    Args:
        keywords_: Optional keywords to be used to narrow down the output list of
            construction sets. If nothing is input here, all available
            construction sets will be output.
        join_words_: If False or None, this component will automatically split
            any strings of multiple keywords (spearated by spaces) into separate
            keywords for searching. This results in a greater liklihood of
            finding an item in the search but it may not be appropropriate for
            all cases. You may want to set it to True when you are searching for
            a specific phrase that includes spaces. (Default: False).
    
    Returns:
        constr_sets: A list of ConstructionSet identifiers that can be applied
            to Honeybee Rooms.
"""

ghenv.Component.Name = 'HB Search Construction Sets'
ghenv.Component.NickName = 'SearchConstrSet'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:  # import the honeybee-core dependencies
    from honeybee.search import filter_array_by_keywords
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.lib.constructionsets import CONSTRUCTION_SETS
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))


if len(keywords_) == 0:
    constr_sets = sorted(CONSTRUCTION_SETS)
else:
    split_words = True if join_words_ is None else not join_words_
    constr_sets = sorted(filter_array_by_keywords(
        CONSTRUCTION_SETS, keywords_, split_words))
