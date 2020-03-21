# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Search for available ProgramTypes within the honeybee energy standards library.
_
Note that the Room ProgramTypes output from this component effectively map to
space types within OpenStudio.
-

    Args:
        _bldg_prog: Text for the building program to search (eg. "LargeOffice",
            "MidriseApartment", etc.). The Honeybee "Building Programs" component
            lists all of the building programs available in the library.
        _vintage_: Text for the building vintage to search (eg. "2013", "pre_1980",
            etc.). The Honeybee "Building Vintages" component lists all of the
            vintages available in the library. Default: "2013" (for ASHRAE 90.1 2013).
            Note that vintages are often called "templates" within the OpenStudio
            standards gem and so this property effective maps to the standards
            gem "template".
        keywords_: Optional keywords to be used to narrow down the output list of
            room programs. If nothing is input here, all available room programs
            will be output.
    
    Returns:
        room_prog: A list of room program names that meet the input criteria and
            can be applied to Honeybee Rooms.
"""

ghenv.Component.Name = "HB Search Programs"
ghenv.Component.NickName = 'SearchProg'
ghenv.Component.Message = '0.1.2'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    from honeybee.search import filter_array_by_keywords
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.lib.programtypes import STANDARDS_REGISTRY
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set the default vintage
    _vintage_ = _vintage_ if _vintage_ is not None else '2013'
    
    try:  # get the available programs for the vintage
        vintage_subset = STANDARDS_REGISTRY[_vintage_]
    except KeyError:
        raise ValueError(
            'Input _vintage_ "{}" is not valid. Choose from:\n'
            '{}'.format(_vintage_, '\n'.join(STANDARDS_REGISTRY.keys())))
    
    try:  # get the available programs for the building type
        room_programs = vintage_subset[_bldg_prog]
    except KeyError:
        raise ValueError(
            'Input _bldg_prog "{}" is not avaible for vintage "{}". Choose from:\n'
             '{}'.format(_bldg_prog, _vintage_, '\n'.join(vintage_subset.keys())))
    
    # apply any keywords
    if keywords_ != []:
        room_programs = filter_array_by_keywords(room_programs, keywords_, False)
    
    # join vintage, building program and room programs into a complete string
    room_prog = ['{}::{}::{}'.format(_vintage_, _bldg_prog, rp) for rp in room_programs]