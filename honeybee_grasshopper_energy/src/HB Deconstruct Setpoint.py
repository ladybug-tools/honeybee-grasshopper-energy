# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Deconstruct a Setpoint object into its constituient properties.
-

    Args:
        _setpoint: A Setpoint object to be deconstructed.
    
    Returns:
        name: Text string for the setpoint display name.
         heating_sch: A temperature schedule for the heating setpoint.
            The type limit of this schedule should be temperature and the
            values should be the temperature setpoint in degrees Celcius.
        cooling_sch: A temperature schedule for the cooling setpoint.
            The type limit of this schedule should be temperature and the
            values should be the temperature setpoint in degrees Celcius.
        humid_setpt: A numerical value between 0 and 100 for the relative humidity
            humidifying setpoint [%]. This value will be constant throughout the
            year. If None, no humidification will occur.
        dehumid_setpt: A numerical value between 0 and 100 for the relative humidity
            dehumidifying setpoint [%]. This value will be constant throughout the
            year. If None, no dehumidification will occur beyond that which is needed
            to create air at the cooling supply temperature.
"""

ghenv.Component.Name = "HB Deconstruct Setpoint"
ghenv.Component.NickName = 'DecnstrSetpoint'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = "0"

try:
    from honeybee_energy.load.setpoint import Setpoint
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _setpoint is not None:
    # check the input
    assert isinstance(_setpoint, Setpoint), \
        'Expected Setpoint object. Got {}.'.format(type(_setpoint))

    # get the properties of the object
    name = _setpoint.display_name
    heating_sch = _setpoint.heating_schedule
    cooling_sch = _setpoint.cooling_schedule
    humid_setpt = _setpoint.humidifying_setpoint
    dehumid_setpt = _setpoint.dehumidifying_setpoint
