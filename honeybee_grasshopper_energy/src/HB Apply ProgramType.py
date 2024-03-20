# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Apply ProgramType objects to Rooms or a Model.
-

    Args:
        _rooms: Honeybee Rooms to which the input program should be assigned.
            This can also be a Honeybee Model for which all Rooms will be
            assigned the ProgramType.
        _program: A ProgramType object to apply to the input rooms. This can also be
            text for the program of the Rooms (to be looked up in the
            ProgramType library) such as that output from the "HB List Programs"
            component.
        overwrite_: A Boolean to note whether any loads assigned specifically to the
            Room, which overwrite the loads of ProgramType should be reset so
            that they are determined by the input program. (Default: False).

    Returns:
        report: Reports, errors, warnings, etc.
        rooms: The input Rooms with their loads edited.
"""

ghenv.Component.Name = "HB Apply ProgramType"
ghenv.Component.NickName = 'ApplyProgram'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:
    from honeybee.model import Model
    from honeybee.room import Room
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from honeybee_energy.lib.programtypes import program_type_by_identifier, \
        building_program_type_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, longest_list, \
        give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    rooms = [obj.duplicate() for obj in _rooms]

    # extract any rooms from the input Models
    hb_objs = []
    for hb_obj in rooms:
        if isinstance(hb_obj, Model):
            hb_objs.extend(hb_obj.rooms)
        elif isinstance(hb_obj, Room):
            hb_objs.append(hb_obj)
        else:
            raise ValueError(
                'Expected Honeybee Room or Model. Got {}.'.format(type(hb_obj)))

    # apply the program to the rooms
    for i, room in enumerate(hb_objs):
        prog = longest_list(_program, i)
        if isinstance(prog, str):  # get the program object if it is a string
            try:
                prog = building_program_type_by_identifier(prog)
            except ValueError:
                prog = program_type_by_identifier(prog)
        room.properties.energy.program_type = prog
        if overwrite_:
            room.properties.energy.reset_loads_to_program()
        elif overwrite_ is None and room.properties.energy.has_overridden_loads:
            msg = 'Room "{}" has loads assigned specifically to it, which override ' \
                'the assigned program.\nIf resetting all loads to be assigned by ' \
                'the input program is desired, then the overwrite_ option\non this ' \
                'component should be set to True.'.format(room.display_name)
            print(msg)
            give_warning(ghenv.Component, msg)