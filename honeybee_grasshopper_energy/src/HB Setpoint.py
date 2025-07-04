# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a Setpoint object that can be used to create a ProgramType or be assigned
directly to a Room.
-

    Args:
        _name_: Text to set the name for the Setpoint and to be incorporated
            into a unique Setpoint identifier. If None, a unique name will
            be generated.
         _heating_sch: A temperature schedule for the heating setpoint.
            The type limit of this schedule should be temperature and the
            values should be the temperature setpoint in degrees Celcius.
        _cooling_sch: A temperature schedule for the cooling setpoint.
            The type limit of this schedule should be temperature and the
            values should be the temperature setpoint in degrees Celcius.
        humid_setpt_: A numerical value between 0 and 100 for the relative humidity
            humidifying setpoint [%]. This value will be constant throughout the
            year. If None, no humidification will occur.
        dehumid_setpt_: A numerical value between 0 and 100 for the relative humidity
            dehumidifying setpoint [%]. This value will be constant throughout the
            year. If None, no dehumidification will occur beyond that which is needed
            to create air at the cooling supply temperature.
        cutout_difference_: An optional positive number for the temperature difference between the
            cutout temperature and the setpoint temperature. Specifying a non-zero
            number here is useful for modeling the throttling range associated
            with a given setup of setpoint controls and HVAC equipment. Throttling
            ranges describe the range where a zone is slightly over-cooled or
            over-heated beyond the thermostat setpoint. They are used to avoid
            situations where HVAC systems turn on only to turn off a few minutes later,
            thereby wearing out the parts of mechanical systems faster. They can
            have a minor impact on energy consumption and can often have significant
            impacts on occupant thermal comfort, though using the default value
            of zero will often yield results that are close enough when trying
            to estimate the annual heating/cooling energy use. Specifying a value
            of zero effectively assumes that the system will turn on whenever
            conditions are outside the setpoint range and will cut out as soon
            as the setpoint is reached. (Default: 0).

    Returns:
        setpoint: A Setpoint object that can be used to create a ProgramType or
            be assigned directly to a Room.
"""

ghenv.Component.Name = 'HB Setpoint'
ghenv.Component.NickName = 'Setpoint'
ghenv.Component.Message = '1.9.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.load.setpoint import Setpoint
    from honeybee_energy.lib.schedules import schedule_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # make a default Setpoint name if none is provided
    name = clean_and_id_ep_string('Setpoint') if _name_ is None else \
        clean_ep_string(_name_)

    # get the schedules
    if isinstance(_heating_sch, str):
        _heating_sch = schedule_by_identifier(_heating_sch)
    if isinstance(_cooling_sch, str):
        _cooling_sch = schedule_by_identifier(_cooling_sch)

    # create the Setpoint object
    setpoint = Setpoint(name, _heating_sch, _cooling_sch)
    if _name_ is not None:
        setpoint.display_name = _name_

    # assign the humidification and dehumidification setpoints if specified
    if humid_setpt_ is not None:
        setpoint.humidifying_setpoint = humid_setpt_
    if dehumid_setpt_ is not None:
        setpoint.dehumidifying_setpoint = dehumid_setpt_

    # assign the cutout_difference_ if specified
    if cutout_difference_ is not None:
        setpoint.setpoint_cutout_difference = cutout_difference_
