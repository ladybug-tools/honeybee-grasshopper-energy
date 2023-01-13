# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create an ServiceHotWater object that can be used to specify hot water usage in
a ProgramType.
-

    Args:
        _name_: Text to set the name for the ServiceHotWater and to be incorporated
            into a unique ServiceHotWater identifier. If None, a unique name will
            be generated.
        _flow_per_area: A numerical value for the total volume flow rate of water
            per unit area of floor (L/h-m2).
        _schedule: A fractional schedule for the use of hot water over the course of
            the year. The fractional values will get multiplied by the
            _flow_per_area to yield a complete water usage profile.
        _target_temp_: The target temperature of the water out of the tap in Celsius.
            This the temperature after the hot water has been mixed with cold
            water from the water mains. The default value assumes that the
            flow_per_area on this object is only for water straight out
            of the water heater. (Default: 60C).
        _sensible_fract_: A number between 0 and 1 for the fraction of the total
            hot water load given off as sensible heat in the zone. (Default: 0.2).
        _latent_fract_: A number between 0 and 1 for the fraction of the total
            hot water load that is latent (as opposed to sensible). (Default: 0.05).

    Returns:
        hot_water: A ServiceHotWater object that can be used to specify hot water usage
            in a ProgramType.
"""

ghenv.Component.Name = 'HB Service Hot Water'
ghenv.Component.NickName = 'ServiceHotWater'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.load.hotwater import ServiceHotWater
    from honeybee_energy.lib.schedules import schedule_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # make a default ServiceHotWater name if none is provided
    name = clean_and_id_ep_string('ServiceHotWater') if _name_ is None else \
        clean_ep_string(_name_)

    # get the schedule
    if isinstance(_schedule, str):
        _schedule = schedule_by_identifier(_schedule)

    # get default radiant, latent, and lost fractions
    _target_temp_ = _target_temp_ if _target_temp_ is not None else 60
    _sensible_fract_ = _sensible_fract_ if _sensible_fract_ is not None else 0.2
    _latent_fract_ = _latent_fract_ if _latent_fract_ is not None else 0.05

    # create the ServiceHotWater object
    hot_water = ServiceHotWater(name, _flow_per_area, _schedule, _target_temp_,
                                _sensible_fract_, _latent_fract_)
    if _name_ is not None:
        hot_water.display_name = _name_