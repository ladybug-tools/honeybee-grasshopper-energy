# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Search for available ProgramTypes within the honeybee energy standards library.
_
Note that the Room ProgramTypes output from this component effectively map to
space types within OpenStudio.
-

    Args:
        bldg_prog_: Text for the building program to search (eg. "LargeOffice",
            "MidriseApartment", etc.). The Honeybee "Building Programs" component
            lists all of the building programs available in the library. If None,
            all ProgramTypes within the library will be output (filtered by
            keywords_ below).
        _vintage_: Text for the building vintage to search (eg. "2019", "pre_1980",
            etc.). The Honeybee "Building Vintages" component lists all of the
            vintages available in the library. Default: "2019" (for ASHRAE 90.1
            2019 | IECC 2015). Note that vintages are often called "templates"
            within the OpenStudio standards gem and so this property effective
            maps to the standards gem "template".
        keywords_: Optional keywords to be used to narrow down the output list of
            room programs. If nothing is input here, all available room programs
            will be output.

    Returns:
        room_prog: A list of room program identifiers that meet the input criteria and
            can be applied to Honeybee Rooms.
"""

ghenv.Component.Name = "HB Search Programs"
ghenv.Component.NickName = 'SearchProg'
ghenv.Component.Message = '1.9.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    from honeybee.search import filter_array_by_keywords
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.lib.programtypes import STANDARDS_REGISTRY
    from honeybee_energy.lib.programtypes import PROGRAM_TYPES
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import turn_off_old_tag
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
turn_off_old_tag(ghenv.Component)


if bldg_prog_ is not None:
    # set the default vintage
    _vintage_ = _vintage_ if _vintage_ is not None else '2019'
    try:  # get the available programs for the vintage
        vintage_subset = STANDARDS_REGISTRY[_vintage_]
    except KeyError:
        raise ValueError(
            'Input _vintage_ "{}" is not valid. Choose from:\n'
            '{}'.format(_vintage_, '\n'.join(STANDARDS_REGISTRY.keys())))
    try:  # get the available programs for the building type
        room_programs = vintage_subset[bldg_prog_]
    except KeyError:
        raise ValueError(
            'Input bldg_prog_ "{}" is not avaible for vintage "{}". Choose from:\n'
             '{}'.format(bldg_prog_, _vintage_, '\n'.join(vintage_subset.keys())))
    # apply any keywords
    if keywords_ != []:
        room_programs = filter_array_by_keywords(room_programs, keywords_, False)
    # join vintage, building program and room programs into a complete string
    room_prog = ['{}::{}::{}'.format(_vintage_, bldg_prog_, rp) for rp in room_programs]
else:
    # return all programs in the library filtered by keyword
    room_prog = sorted(PROGRAM_TYPES)
    if _vintage_ is not None:
        room_prog = filter_array_by_keywords(room_prog, [_vintage_], False)
    if keywords_ != []:
        room_prog = filter_array_by_keywords(room_prog, keywords_, False)
