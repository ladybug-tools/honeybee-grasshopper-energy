# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Deconstruct a Ventilation object into its constituient properties.
_
Note the the 4 ventilation types (_flow_per_person_, _flow_per_area_, _flow_per_zone_,
_ach_) are ultimately summed together to yeild the ventilation design flow rate used
in the simulation.
-

    Args:
        _vent: An Ventilation object to be deconstructed.
    
    Returns:
        name: Text string for the ventilation display name.
        flow_per_person: A numerical value for the intensity of ventilation
            in m3/s per person. Note that setting this value here does not mean
            that ventilation is varied based on real-time occupancy but rather
            that the design level of ventilation is determined using this value
            and the People object of the zone. To vary ventilation in real time,
            the ventilation schedule should be used. Most ventilation standards
            support that a value of 0.01 m3/s (10 L/s or ~20 cfm) per person is
            sufficient to remove odors.
        flow_per_area: A numerical value for the intensity of ventilation in m3/s
            per square meter of floor area.
        flow_per_zone: A numerical value for the design level of ventilation
            in m3/s for the entire zone.
        ach: A numberical value for the design level of ventilation in air changes
            per hour (ACH) for the entire zone. This is particularly helpful
            for hospitals, where ventilation standards are often given in ACH.
        schedule: An optional fractional schedule for the ventilation over the
            course of the year. The fractional values will get multiplied by
            the total design flow rate (determined from the fields above and the
            calculation_method) to yield a complete ventilation profile. If None,
            the design level of ventilation is used throughout all timesteps of
            the simulation.
"""

ghenv.Component.Name = "HB Deconstruct Ventilation"
ghenv.Component.NickName = 'DecnstrVentilation'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = "0"

try:
    from honeybee_energy.load.ventilation import Ventilation
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _vent is not None:
    # check the input
    assert isinstance(_vent, Ventilation), \
        'Expected Ventilation object. Got {}.'.format(type(_vent))

    # get the properties of the object
    name = _vent.display_name
    flow_per_person = _vent.flow_per_person
    flow_per_area = _vent.flow_per_area
    flow_per_zone = _vent.flow_per_zone
    ach = _vent.air_changes_per_hour
    schedule = _vent.schedule
