# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a ProgramType object by blending other ProgramTypes together using a weighted
average based on program ratios.
-

    Args:
        _name_: Text to set the name for the ProgramType and to be incorporated
            into a unique ProgramType identifier.
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

ghenv.Component.Name = 'HB Blend ProgramTypes'
ghenv.Component.NickName = 'BlendPrograms'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.programtype import ProgramType
    from honeybee_energy.lib.programtypes import program_type_by_identifier, \
        building_program_type_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set default ratios to None
    _ratios_ = _ratios_ if len(_ratios_) != 0 else None
    name = clean_and_id_ep_string('ProgramType') if _name_ is None else \
        clean_ep_string(_name_)

    # get programs from library if a name is input
    for i, prog in enumerate(_programs):
        if isinstance(prog, str):
            try:
                _programs[i] = building_program_type_by_identifier(prog)
            except ValueError:
                _programs[i] = program_type_by_identifier(prog)

    # create blended program
    program = ProgramType.average(name, _programs, _ratios_)
    if _name_ is not None:
        program.display_name = _name_