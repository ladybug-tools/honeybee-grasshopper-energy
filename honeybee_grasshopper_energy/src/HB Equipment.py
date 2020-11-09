# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create an Equipment object that can be used to create a ProgramType or be assigned
directly to a Room.
-

    Args:
        _name_: Text to set the name for the Equipment and to be incorporated
            into a unique Equipment identifier. If None, a unique name will
            be generated.
         _watts_per_area: A numerical value for the equipment power density in
            Watts per square meter of floor area.
        _schedule: A fractional for the use of equipment over the course of the year.
            The fractional values will get multiplied by the _watts_per_area to
            yield a complete equipment profile.
        radiant_fract_: A number between 0 and 1 for the fraction of the total
            equipment load given off as long wave radiant heat. Default: 0.
        latent_fract_: A number between 0 and 1 for the fraction of the total
            equipment load that is latent (as opposed to sensible). Default: 0.
        lost_fract_: A number between 0 and 1 for the fraction of the total
            equipment load that is lost outside of the zone and the HVAC system.
            Typically, this is used to represent heat that is exhausted directly
            out of a zone (as you would for a stove). Default: 0.
        gas_: Set to "True" to have the output Equipment object be for GasEquipment
            (as opposed to ElectricEquipment).
    
    Returns:
        equip: An Equipment object that can be used to create a ProgramType or
            be assigned directly to a Room.
"""

ghenv.Component.Name = "HB Equipment"
ghenv.Component.NickName = 'Equipment'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = "3"

import uuid

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.load.equipment import ElectricEquipment, GasEquipment
    from honeybee_energy.lib.schedules import schedule_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # make a default Equipment name if none is provided
    if _name_ is None:
        name = "Equipment_{}".format(uuid.uuid4())
    else:
        name = clean_and_id_ep_string(_name_)

    # get the schedule
    if isinstance(_schedule, str):
        _schedule = schedule_by_identifier(_schedule)

    # get default radiant, latent, and lost fractions
    radiant_fract_ = radiant_fract_ if radiant_fract_ is not None else 0.0
    latent_fract_ = latent_fract_ if latent_fract_ is not None else 0.0
    lost_fract_ = lost_fract_ if lost_fract_ is not None else 0.0

    # create the Equipment object
    if gas_:
        equip = GasEquipment(name, _watts_per_area, _schedule,
                             radiant_fract_, latent_fract_, lost_fract_)
    else:
        equip = ElectricEquipment(name, _watts_per_area, _schedule,
                                  radiant_fract_, latent_fract_, lost_fract_)
    if _name_ is not None:
        equip.display_name = _name_