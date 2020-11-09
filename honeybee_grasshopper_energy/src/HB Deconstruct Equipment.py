# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Deconstruct an Equipment object into its constituient properties.
-

    Args:
        _equip: An ElectricEquipment or a GasEquipment object to be deconstructed.
    
    Returns:
        name_: Text string for the equipment display name.
         watts_per_area: A numerical value for the equipment power density in
            Watts per square meter of floor area.
        schedule: A fractional for the use of equipment over the course of the year.
            The fractional values will get multiplied by the watts_per_area to
            yield a complete equipment profile.
        radiant_fract: A number between 0 and 1 for the fraction of the total
            equipment load given off as long wave radiant heat.
        latent_fract: A number between 0 and 1 for the fraction of the total
            equipment load that is latent (as opposed to sensible).
        lost_fract: A number between 0 and 1 for the fraction of the total
            equipment load that is lost outside of the zone and the HVAC system.
            Typically, this is used to represent heat that is exhausted directly
            out of a zone (as you would for a stove).
        is_gas: Will be True if the input Equipment object is for GasEquipment;
            False if it is for ElectricEquipment.
"""

ghenv.Component.Name = "HB Deconstruct Equipment"
ghenv.Component.NickName = 'DecnstrEquipment'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = "0"

try:
    from honeybee_energy.load.equipment import ElectricEquipment, GasEquipment
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _equip is not None:
    # check the input
    assert isinstance(_equip, (ElectricEquipment, GasEquipment)), \
        'Expected Equipment object. Got {}.'.format(type(_equip))

    # get the properties of the object
    name = _equip.display_name
    watts_per_area = _equip.watts_per_area
    schedule = _equip.schedule
    radiant_fract = _equip.radiant_fraction
    latent_fract = _equip.latent_fraction
    lost_fract = _equip.lost_fraction
    is_gas = isinstance(_equip, GasEquipment)
