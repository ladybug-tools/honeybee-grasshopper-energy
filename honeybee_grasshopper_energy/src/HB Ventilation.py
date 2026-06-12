# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2026, Ladybug Tools.
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
        _method_: Text to set how the different ventilation criteria are reconciled
            against one another. Choose from the options below. (Default: Sum).
            * Sum
            * Max
        effectiveness_cool_: A positive number to note the air distribution effectiveness
            of the ventilation system when it operates in cooling mode
            (or how well the system is able to mix the air when cooling).
            A value of 1 means that air is well mixed and specified air flows are not
            adjusted in the course of simulation. Values less than 1 indicate systems
            that do not mix the air as well and so the specified airflows are increased.
            Values greater than 1 indicate systems that are particularly good at
            delivering outdoor air to the breathing zone of a room and so the
            specified airflows can be reduced. (Default: 1).
        effectiveness_heat_: A positive number to note the air distribution effectiveness
            of the ventilation system when it operates in heating mode
            (or how well the system is able to mix the air when heating).
            A value of 1 means that air is well mixed and specified air flows are not
            adjusted in the course of simulation. Values less than 1 indicate systems
            that do not mix the air as well and so the specified airflows are increased.
            Values greater than 1 indicate systems that are particularly good at
            delivering outdoor air to the breathing zone of a room and so the
            specified airflows can be reduced. (Default: 1).
        secondary_recirc_: A number that is greater than or equal to zero, which notes
            the fraction of a zone's recirculation air that does not directly
            mix with the outdoor air. Used in cases where a central ventilation
            system supplies several zones and the return air is not collected
            through ducts back to the central air handler (eg. a plenum return
            system is used). This means unused outdoor ventilation air from other
            zones in the central system can be credited to the room. (Default: 0).

    Returns:
        vent: An Ventilation object that can be used to create a ProgramType or
            be assigned directly to a Room.
"""

ghenv.Component.Name = 'HB Ventilation'
ghenv.Component.NickName = 'Ventilation'
ghenv.Component.Message = '1.10.1'
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
    from ladybug_rhino.grasshopper import turn_off_old_tag
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
turn_off_old_tag(ghenv.Component)


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
_method_ = _method_ if _method_ is not None else 'Sum'
effectiveness_cool_ = 1 if effectiveness_cool_ is None else effectiveness_cool_
effectiveness_heat_ = 1 if effectiveness_heat_ is None else effectiveness_heat_
secondary_recirc_ = 0 if secondary_recirc_ is None else secondary_recirc_

# create the Ventilation object
vent = Ventilation(
    name, _flow_per_person_, _flow_per_area_, _flow_per_zone_, _ach_,
    _schedule_, _method_, effectiveness_cool_, effectiveness_heat_,
    secondary_recirc_
)
if _name_ is not None:
    vent.display_name = _name_
