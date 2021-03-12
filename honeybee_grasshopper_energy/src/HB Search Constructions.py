# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Search for available Constructions within the honeybee energy standards library.
-

    Args:
        keywords_: Optional keywords to be used to narrow down the output list of
            constructions. If nothing is input here, all available constructions
            will be output.
        join_words_: If False or None, this component will automatically split
            any strings of multiple keywords (spearated by spaces) into separate
            keywords for searching. This results in a greater liklihood of
            finding an item in the search but it may not be appropropriate for
            all cases. You may want to set it to True when you are searching for
            a specific phrase that includes spaces. Default: False.
    
    Returns:
        opaque_constrs: A list of opaque constructions within the honeybee energy
            standards library (filtered by keywords_ if they are input).
        window_constrs: A list of window constructions within the honeybee energy
            standards library (filtered by keywords_ if they are input).
        shade_constrs: A list of shade constructions within the honeybee energy
            standards library (filtered by keywords_ if they are input).
"""

ghenv.Component.Name = "HB Search Constructions"
ghenv.Component.NickName = 'SearchConstrs'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = "1 :: Constructions"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:  # import the honeybee-core dependencies
    from honeybee.search import filter_array_by_keywords
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.lib.constructions import OPAQUE_CONSTRUCTIONS
    from honeybee_energy.lib.constructions import WINDOW_CONSTRUCTIONS
    from honeybee_energy.lib.constructions import SHADE_CONSTRUCTIONS
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))


if len(keywords_) == 0:
    opaque_constrs = sorted(OPAQUE_CONSTRUCTIONS)
    window_constrs = sorted(WINDOW_CONSTRUCTIONS)
    shade_constrs = sorted(SHADE_CONSTRUCTIONS)
else:
    split_words = True if join_words_ is None else not join_words_
    opaque_constrs = sorted(filter_array_by_keywords(
        OPAQUE_CONSTRUCTIONS, keywords_, split_words))
    window_constrs = sorted(filter_array_by_keywords(
        WINDOW_CONSTRUCTIONS, keywords_, split_words))
    shade_constrs = sorted(filter_array_by_keywords(
        SHADE_CONSTRUCTIONS, keywords_, split_words))
