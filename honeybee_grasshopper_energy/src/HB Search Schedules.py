# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Search for available Schedules within the honeybee energy standards library.
-

    Args:
        keywords_: Optional keywords to be used to narrow down the output list of
            scheduless. If nothing is input here, all available schedules
            will be output.
        join_words_: If False or None, this component will automatically split
            any strings of multiple keywords (spearated by spaces) into separate
            keywords for searching. This results in a greater liklihood of
            finding an item in the search but it may not be appropropriate for
            all cases. You may want to set it to True when you are searching for
            a specific phrase that includes spaces. Default: False.
    
    Returns:
        schedules: A list of Schedules within the honeybee energy standards
            library (filtered by keywords_ if they are input).
        type_limits: A list of all ScheduleTypeLimits within the honeybee energy
            standards library.
"""

ghenv.Component.Name = "HB Search Schedules"
ghenv.Component.NickName = 'SearchSchs'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = "2 :: Schedules"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:  # import the honeybee-core dependencies
    from honeybee.search import filter_array_by_keywords
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.lib.schedules import SCHEDULES
    from honeybee_energy.lib.scheduletypelimits import SCHEDULE_TYPE_LIMITS
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))


if len(keywords_) == 0:
    schedules = sorted(SCHEDULES)
else:
    split_words = True if join_words_ is None else not join_words_
    schedules = sorted(filter_array_by_keywords(SCHEDULES, keywords_, split_words))
type_limits = sorted(SCHEDULE_TYPE_LIMITS)
