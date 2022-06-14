# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Deconstruct a People object into its constituient properties.
-

    Args:
        _people: A People object to deconstruct.
    
    Returns:
        name: Text string for the people object display name.
         ppl_per_area: A numerical value for the number of people per square
            meter of floor area.
        occupancy_sch: A fractional schedule for the occupancy over the course
            of the year. The fractional values in this schedule get multiplied
            by the _people_per_area to yield a complete occupancy profile.
        activity_sch: A schedule for the activity of the occupants over the
            course of the year. The type limt of this schedule are "Power"
            and the values of the schedule equal to the number of Watts given off
            by an individual person in the room.
"""

ghenv.Component.Name = "HB Deconstruct People"
ghenv.Component.NickName = 'DecnstrPeople'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = "0"

try:
    from honeybee_energy.load.people import People
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _people is not None:
    # check the input
    assert isinstance(_people, People), \
        'Expected People object. Got {}.'.format(type(_people))

    # get the properties of the object
    name = _people.display_name
    ppl_per_area = _people.people_per_area
    occupancy_sch = _people.occupancy_schedule
    activity_sch = _people.activity_schedule
