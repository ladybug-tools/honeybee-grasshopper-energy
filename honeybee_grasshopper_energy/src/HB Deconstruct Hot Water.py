# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Deconstruct a ServiceHotWater object into its constituient properties.
-

    Args:
        _hot_water: A ServiceHotWater object to be deconstructed.

    Returns:
        name_: Text string for the service hot water display name.
         flow_per_area: A numerical value for the total volume flow rate of water
            per unit area of floor (L/h-m2).
        schedule: A fractional schedule for the use of hot water over the course of
            the year. The fractional values will get multiplied by the
            _flow_per_area to yield a complete water usage profile.
        target_temp: The target temperature of the water out of the tap in Celsius.
            This the temperature after the hot water has been mixed with cold
            water from the water mains.
        sensible_fract: A number between 0 and 1 for the fraction of the total
            hot water load given off as sensible heat in the zone.
        latent_fract: A number between 0 and 1 for the fraction of the total
            hot water load that is latent (as opposed to sensible).
"""

ghenv.Component.Name = 'HB Deconstruct Hot Water'
ghenv.Component.NickName = 'DecnstrHotWater'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from honeybee_energy.load.hotwater import ServiceHotWater
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _hot_water is not None:
    # check the input
    assert isinstance(_hot_water, ServiceHotWater), \
        'Expected ServiceHotWater object. Got {}.'.format(type(_hot_water))

    # get the properties of the object
    name = _hot_water.display_name
    flow_per_area = _hot_water.flow_per_area
    schedule = _hot_water.schedule
    target_temp = _hot_water.target_temperature
    sensible_fract = _hot_water.sensible_fraction
    latent_fract = _hot_water.latent_fraction
