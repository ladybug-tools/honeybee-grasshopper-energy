# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a Ventilation Control object to dictate the temperature setpoints and
schedule for ventilative cooling (eg. opening windows).
_
Note the all of the default setpoints of this object are set to always perform
ventilative cooling such that one can individually decide which setpoints
are relevant to a given ventilation strategy.
-

    Args:
        min_in_temp_: A number between -100 and 100 for the minimum indoor
            temperature at which to ventilate in Celsius. Typically,
            this variable is used to initiate ventilation with values
            around room temperature above which the windows will open
            (eg. 22 C). (Default: -100 C).
        max_in_temp_: A number between -100 and 100 for the maximum indoor
            temperature at which to ventilate in Celsius. This can be
            used to set a maximum temperature at which point ventilation is
            stopped and a cooling system is turned on. (Default: 100 C).
        min_out_temp_: A number between -100 and 100 for the minimum outdoor
            temperature at which to ventilate in Celsius. This can be used
            to ensure ventilative cooling doesn't happen during the winter even
            if the Room is above the min_in_temp. (Default: -100 C).
        max_out_temp_: A number between -100 and 100 for the maximum outdoor
            temperature at which to ventilate in Celsius. This can be used
            to set a limit for when it is considered too hot outside for
            ventilative cooling. (Default: 100).
        delta_temp_: A number between -100 and 100 for the temperature differential
            in Celsius between indoor and outdoor below which ventilation
            is shut off.  This should usually be a positive number so that
            ventilation only occurs when the outdoors is cooler than the indoors.
            Negative numbers indicate how much hotter the outdoors can be than
            the indoors before ventilation is stopped. (Default: -100).
        _schedule_: An optional schedule for the ventilation over the course of
            the year. This can also be the name of a schedule to be looked up
            in the standards library. Note that this is applied on top of any
            setpoints. The type of this schedule should be On/Off and values
            should be either 0 (no possibility of ventilation) or 1 (ventilation
            possible). (Default: "Always On")

    Returns:
        vent_cntrl: HBZones with their airflow modified.
"""

ghenv.Component.Name = 'HB Ventilation Control'
ghenv.Component.NickName = 'VentControl'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:
    from honeybee_energy.ventcool.control import VentilationControl
    from honeybee_energy.lib.schedules import schedule_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))


# set default values
min_in_temp_ = -100 if min_in_temp_ is None else min_in_temp_
max_in_temp_ = 100 if max_in_temp_ is None else max_in_temp_
min_out_temp_ = -100 if min_out_temp_ is None else min_out_temp_
max_out_temp_ = 100 if max_out_temp_ is None else max_out_temp_
delta_temp_ = -100 if delta_temp_ is None else delta_temp_

# get the schedule if it's just an identifier
if isinstance(_schedule_, str):
    _schedule_ = schedule_by_identifier(_schedule_)

# create the VentilationControl object
vent_cntrl = VentilationControl(
    min_in_temp_, max_in_temp_, min_out_temp_, max_out_temp_, delta_temp_, _schedule_)
