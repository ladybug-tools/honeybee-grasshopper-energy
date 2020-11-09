# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Get a ConstructionSet from the standards library using a climate zone, building
vintage and construction type.
-

    Args:
        _climate_zone: An integer between 1 and 8 for the ASHRAE climate zone in
            which the building is located. ASHRAE climate zones exist for all
            locations on Earth and can typically be looked up online or within
            the .stat file that downloads next to the .epw file. The climate zone
            is used to determine the amount of code-recommended insulation and
            solar heat gain protection for the construction set. The Honeybee
            "Climate Zones" component lists all of the climate zones supported
            by the library.
        _vintage_: Text for the building vintage to search (eg. "2013", "pre_1980",
            etc.). The Honeybee "Building Vintages" component lists all of the
            vintages available in the library. Default: "2013" (for ASHRAE 90.1 2013).
            Note that vintages are often called "templates" within the OpenStudio
            standards gem and so this property effective maps to the standards
            gem "template".
        _constr_type_: Text for the construction type of the set. (eg. "SteelFramed",
            "WoodFramed", "Mass", "Metal Building"). The Honeybee "Construction Types"
            component lists all of the construction types available in the library.
            Default: "SteelFramed".
    
    Returns:
        constr_set: A ConstructionSet identifier that can be applied to Honeybee Rooms.
"""

ghenv.Component.Name = 'HB Construction Set by Climate'
ghenv.Component.NickName = 'ConstrSetClimate'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from honeybee_energy.lib.programtypes import STANDARDS_REGISTRY
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

CONSTRUCTION_TYPES = ('SteelFramed', 'WoodFramed', 'Mass', 'Metal Building')


if all_required_inputs(ghenv.Component):
    # check the climate zone
    _climate_zone = _climate_zone[0]  # strip out any qualifiers like A, C, or C
    assert 1 <= int(_climate_zone) <=8, 'Input _climate_zone "{}" is not valid. ' \
        'Climate zone must be between 1 and 8.'.format(_climate_zone)
    
    # check and set the default vintage
    if _vintage_ is not None:
        assert _vintage_ in STANDARDS_REGISTRY.keys(), \
            'Input _vintage_ "{}" is not valid. Choose from:\n' \
            '{}'.format(_vintage_, '\n'.join(STANDARDS_REGISTRY.keys()))
    else:
        _vintage_ = '2013'
    
    # check and set the default _constr_type_
    if _constr_type_ is not None:
        assert _constr_type_ in CONSTRUCTION_TYPES, \
            'Input _constr_type_ "{}" is not valid. Choose from:\n' \
            '{}'.format(_vintage_, '\n'.join(CONSTRUCTION_TYPES))
    else:
        _constr_type_ = 'SteelFramed'
    
    # join vintage, climate zone and construction type into a complete string
    constr_set = '{}::{}{}::{}'.format(_vintage_, 'ClimateZone', _climate_zone, _constr_type_)