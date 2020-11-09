# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Apply a customized IdealAirSystem to Honeybee Rooms.
-

    Args:
        _rooms: Honeybee Rooms to which the input ideal air properties will
            be assigned. This can also be a Honeybee Model for which all
            conditioned Rooms will be assigned the ideal air system.
        _economizer_: Text to indicate the type of air-side economizer used on
            the ideal air system. Economizers will mix in a greater amount of
            outdoor air to cool the zone (rather than running the cooling system)
            when the zone needs cooling and the outdoor air is cooler than the zone.
            Choose from the options below. Default: DifferentialDryBulb.
                * NoEconomizer
                * DifferentialDryBulb
                * DifferentialEnthalpy
        dcv_: Boolean to note whether demand controlled ventilation should be
            used on the system, which will vary the amount of ventilation air
            according to the occupancy schedule of the zone. Default: False.
        sensible_hr_: A number between 0 and 1 for the effectiveness of sensible
            heat recovery within the system. Default: 0.
        latent_hr_: A number between 0 and 1 for the effectiveness of latent heat
            recovery within the system. Default: 0.
        _heat_temp_: A number for the maximum heating supply air temperature
            [C]. Default: 50, which is typical for many air-based HVAC systems.
        _cool_temp_: A number for the minimum cooling supply air temperature
            [C]. Default: 13, which is typical for many air-based HVAC systems.
        _heat_limit_: A number for the maximum heating capacity in Watts. This
            can also be the text 'autosize' to indicate that the capacity should
            be determined during the EnergyPlus sizing calculation. This can also
            be the text 'NoLimit' to indicate no upper limit to the heating
            capacity. Default: 'autosize'.
        _cool_limit_: A number for the maximum cooling capacity in Watts. This
            can also be the text 'autosize' to indicate that the capacity should
            be determined during the EnergyPlus sizing calculation. This can also
            be the text 'NoLimit' to indicate no upper limit to the cooling
            capacity. Default: 'autosize'.
    
    Returns:
        rooms: The input Rooms with their Ideal Air Systems edited.
"""

ghenv.Component.Name = "HB IdealAir"
ghenv.Component.NickName = 'IdealAir'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '4 :: HVAC'
ghenv.Component.AdditionalHelpFromDocStrings = '1'


try:  # import the honeybee extension
    from honeybee.altnumber import autosize, no_limit
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.hvac.idealair import IdealAirSystem
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

# dictionary to get alterante number types
alt_numbers = {
    'nolimit': no_limit,
    'NoLimit': no_limit,
    'autosize': autosize,
    'Autosize': autosize,
    None: autosize
    }

if all_required_inputs(ghenv.Component):
    # extract any rooms from input Models and duplicate the rooms
    rooms = []
    for hb_obj in _rooms:
        if isinstance(hb_obj, Model):
            rooms.extend([room.duplicate() for room in hb_obj.rooms])
        else:
            rooms.append(hb_obj.duplicate())

    for room in rooms:
        if room.properties.energy.is_conditioned:
            # check to be sure the assigned HVAC system is an IdealAirSystem
            if not isinstance(room.properties.energy.hvac, IdealAirSystem):
                room.properties.energy.add_default_ideal_air()
            
            # create the customized ideal air system
            new_ideal_air = room.properties.energy.hvac.duplicate()
            if _economizer_ is not None:
                new_ideal_air.economizer_type = _economizer_
            if dcv_ is not None:
                new_ideal_air.demand_controlled_ventilation = dcv_
            if sensible_hr_ is not None:
                new_ideal_air.sensible_heat_recovery = sensible_hr_
            if latent_hr_ is not None:
                new_ideal_air.latent_heat_recovery = latent_hr_
            if _heat_temp_ is not None:
                new_ideal_air.heating_air_temperature = _heat_temp_
            if _cool_temp_ is not None:
                new_ideal_air.cooling_air_temperature = _cool_temp_
            try:
                new_ideal_air.heating_limit = alt_numbers[_heat_limit_]
            except KeyError:
                new_ideal_air.heating_limit = _heat_limit_
            try:
                new_ideal_air.cooling_limit = alt_numbers[_cool_limit_]
            except KeyError:
                new_ideal_air.cooling_limit = _cool_limit_
            
            # assign the HVAC to the Room
            room.properties.energy.hvac = new_ideal_air
