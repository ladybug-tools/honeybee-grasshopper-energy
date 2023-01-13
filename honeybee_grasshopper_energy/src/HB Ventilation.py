# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

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
        _flow_per_person_: A numerical value for the intensity of outdoor air ventilation
            in m3/s per person. This will be added to the _flow_per_area_,
            _flow_per_zone_ and _ach_ to produce the final minimum outdoor
            air specification. Note that setting this value here does not mean
            that ventilation is varied based on real-time occupancy but rather
            that the minimum level of ventilation is determined using this value
            and the People object of the Room. To vary ventilation on a timestep
            basis, a ventilation schedule should be used or the dcv_ option
            should be selected on the HVAC system if it is available. (Default: 0).
        _flow_per_area_: A numerical value for the intensity of ventilation in m3/s per square
            meter of floor area. This will be added to the _flow_per_person_,
            _flow_per_zone_ and _ach_ to produce the final minimum outdoor
            air specification. (Default: 0).
        _flow_per_zone_: A numerical value for the design level of ventilation in m3/s for
            the entire zone. This will be added to the _flow_per_person_,
            _flow_per_area_ and _ach_ to produce the final minimum outdoor
            air specification. (Default: 0).
        _ach_: A numberical value for the design level of ventilation in air changes per hour
            (ACH) for the entire zone. This will be added to the _flow_per_person_,
            _flow_per_area_ and _flow_per_zone_ to produce the final minimum outdoor
            air specification. (Default: 0).
        _schedule_: An optional fractional schedule for the ventilation over the course
            of the year. The fractional values will get multiplied by the
            total design flow rate (determined from the fields above and the
            calculation_method) to yield a complete ventilation profile. Setting
            this schedule to be the occupancy schedule of the zone will mimic
            demand controlled ventilation. If None, a constant design level of
            ventilation will be used throughout all timesteps of the
            simulation. (Default: None).

    Returns:
        vent: An Ventilation object that can be used to create a ProgramType or
            be assigned directly to a Room.
"""

ghenv.Component.Name = 'HB Ventilation'
ghenv.Component.NickName = 'Ventilation'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
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
name = clean_and_id_ep_string('Ventilation') if _name_ is None else \
    clean_ep_string(_name_)

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
