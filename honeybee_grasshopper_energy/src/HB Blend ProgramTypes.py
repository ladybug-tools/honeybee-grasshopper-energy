# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a ProgramType object by blending other ProgramTypes together using a weighted
average based on program ratios.
-

    Args:
        _name: Text string for the new blended program type name.
        _programs: A list of ProgramType objects that will be averaged
            together to make a new ProgramType.
        _ratios_: A list of fractional numbers with the same length as the input
            programs that sum to 1. These will be used to weight each of the
            ProgramType objects in the resulting average. If None, the input
            program objects will be weighted equally. Default: None.
    
    Returns:
        program: A ProgramType object that's a weighted average between the
            input _programs.
"""

ghenv.Component.Name = "HB Blend ProgramTypes"
ghenv.Component.NickName = 'BlendPrograms'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    from honeybee_energy.programtype import ProgramType
    from honeybee_energy.lib.programtypes import program_type_by_name
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set default ratios to None
    _ratios_ = _ratios_ if len(_ratios_) != 0 else None
    
    # get programs from library if a name is input
    for i, prog in enumerate(_programs):
        if isinstance(prog, str):
            _programs[i] = program_type_by_name(prog)
    
    # create blended program
    program = ProgramType.average(_name, _programs, _ratios_)