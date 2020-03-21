# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a People object that can be used to create a ProgramType or be assigned
directly to a Room.
-

    Args:
        _name_: Text string for the people definition name. If None, a unique
            name will be generated.
         _ppl_per_area: A numerical value for the number of people per square
            meter of floor area.
        _occupancy_sch: A fractional schedule for the occupancy over the course
            of the year. The fractional values in this schedule will get multiplied
            by the _people_per_area to yield a complete occupancy profile.
        _activity_sch_: A schedule for the activity of the occupants over the
            course of the year. The type limt of this schedule should be "Power"
            and the values of the schedule equal to the number of Watts given off
            by an individual person in the room. If None, it will a default constant
            schedule with 120 Watts per person will be used, which is typical of
            awake, adult humans who are seated.
    
    Returns:
        people: A People object that can be used to create a ProgramType or
            be assigned directly to a Room.
"""

ghenv.Component.Name = "HB People"
ghenv.Component.NickName = 'People'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = "3"

import uuid

try:
    from honeybee_energy.load.people import People
    from honeybee_energy.lib.schedules import schedule_by_name
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # make a default People name if none is provided
    if _name_ is None:
        _name_ = "People_{}".format(uuid.uuid4())
    
    # get the schedules
    if isinstance(_occupancy_sch, str):
        _occupancy_sch = schedule_by_name(_occupancy_sch)
    if isinstance(_activity_sch_, str):
        _activity_sch_ = schedule_by_name(_activity_sch_)
    
    # create the People object
    people = People(_name_, _ppl_per_area, _occupancy_sch, _activity_sch_)
