# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Apply ProgramType objects to Rooms.
-

    Args:
        _rooms: Honeybee Rooms to which the input load objects should be assigned.
        _program: A ProgramType object to apply to the input rooms,
    
    Returns:
        report: Reports, errors, warnings, etc.
        rooms: The input Rooms with their loads edited.
"""

ghenv.Component.Name = "HB Apply ProgramType"
ghenv.Component.NickName = 'ApplyProgram'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:
    from honeybee_energy.lib.programtypes import program_type_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, longest_list
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    rooms = [obj.duplicate() for obj in _rooms]

    # apply the program to the rooms
    for i, room in enumerate(rooms):
        prog = longest_list(_program, i)
        if isinstance(prog, str):  # get the program object if it is a string
            prog = program_type_by_identifier(prog)
        room.properties.energy.program_type = prog