# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a Ventilation object that can be used to create a ProgramType or be
assigned directly to a Room.
_
Note the the 4 ventilation types (_flow_per_person_, _flow_per_area_, _flow_per_zone_,
_ach_) are ultimately summed together to yeild the ventilation design flow rate used
in the simulation.
-

    Args:
        _name_: Text to set the name for the Ventilation and to be incorporated
            into a unique Ventilation identifier. If None, a unique name will
            be generated.
        _flow_per_person_: A numerical value for the intensity of ventilation
            in m3/s per person. Note that setting this value here does not mean
            that ventilation is varied based on real-time occupancy but rather
            that the design level of ventilation is determined using this value
            and the People object of the zone. To vary ventilation in real time,
            the ventilation schedule should be used. Most ventilation standards
            support that a value of 0.01 m3/s (10 L/s or ~20 cfm) per person is
            sufficient to remove odors. Accordingly, setting this value to 0.01
            and using 0 for the following ventilation terms will often be suitable
            for many applications. Default: 0.
        _flow_per_area_: A numerical value for the intensity of ventilation in m3/s
            per square meter of floor area. Default: 0.
        _flow_per_zone_: A numerical value for the design level of ventilation
            in m3/s for the entire zone. Default: 0.
        _ach_: A numberical value for the design level of ventilation
            in air changes per hour (ACH) for the entire zone. This is particularly
            helpful for hospitals, where ventilation standards are often given
            in ACH. Default: 0.
        _schedule_: An optional fractional schedule for the ventilation over the
            course of the year. The fractional values will get multiplied by
            the total design flow rate (determined from the fields above and the
            calculation_method) to yield a complete ventilation profile. Setting
            this schedule to be the occupancy schedule of the zone will mimic demand
            controlled ventilation. If None, the design level of ventilation will
            be used throughout all timesteps of the simulation. Default: None.
    
    Returns:
        vent: An Ventilation object that can be used to create a ProgramType or
            be assigned directly to a Room.
"""

ghenv.Component.Name = "HB Ventilation"
ghenv.Component.NickName = 'Ventilation'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = "3"

import uuid

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.load.ventilation import Ventilation
    from honeybee_energy.lib.schedules import schedule_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


# make a default Ventilation name if none is provided
if _name_ is None:
    name = "Ventilation_{}".format(uuid.uuid4())
else:
    name = clean_and_id_ep_string(_name_)

# get the schedule
if isinstance(_schedule_, str):
    _schedule_ = schedule_by_identifier(_schedule_)

# get default _flow_per_person_, _flow_per_area_, and _ach_
_flow_per_person_ = _flow_per_person_ if _flow_per_person_ is not None else 0.0
_flow_per_area_ = _flow_per_area_ if _flow_per_area_ is not None else 0.0
_flow_per_zone_ = _flow_per_zone_ if _flow_per_zone_ is not None else 0.0
_ach_ = _ach_ if _ach_ is not None else 0.0

# create the Ventilation object
vent = Ventilation(name, _flow_per_person_, _flow_per_area_,
                    _flow_per_zone_, _ach_, _schedule_)
if _name_ is not None:
    vent.display_name = _name_
