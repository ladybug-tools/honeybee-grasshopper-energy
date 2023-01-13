# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Apply process loads to Rooms.
_
Examples of process loads include wood burning fireplaces, kilns, manufacturing
equipment, and various industrial processes. They can also be used to represent 
certain specialized pieces of equipment to be separated from the other end uses,
such as MRI machines, theatrical lighting, elevators, etc.
-

    Args:
        _rooms: Honeybee Rooms to which process loads should be assigned.
        _name_: Text to set the name for the Process load and to be incorporated into a
            unique Process load identifier. If None, a unique name will be
            generated.
        _watts: A number for the process load power in Watts.
        _schedule: A fractional schedule for the use of the process over the course of
            the year. The fractional values will get multiplied by the _watts
            to yield a complete process load profile.
        _fuel_type: Text to denote the type of fuel consumed by the process. Using the
            "None" type indicates that no end uses will be associated with the
            process, only the zone gains. Choose from the following.
                * Electricity
                * NaturalGas
                * Propane
                * FuelOilNo1
                * FuelOilNo2
                * Diesel
                * Gasoline
                * Coal
                * Steam
                * DistrictHeating
                * DistrictCooling
                * OtherFuel1
                * OtherFuel2
                * None
        use_category_: Text to indicate the end-use subcategory, which will identify
            the process load in the EUI output. For example, “Cooking”,
            “Clothes Drying”, etc. (Default: General).
        radiant_fract_: A number between 0 and 1 for the fraction of the total
            process load given off as long wave radiant heat. (Default: 0).
        latent_fract_: A number between 0 and 1 for the fraction of the total
            process load that is latent (as opposed to sensible). (Default: 0).
        lost_fract_: A number between 0 and 1 for the fraction of the total
            process load that is lost outside of the zone and the HVAC system.
            Typically, this is used to represent heat that is exhausted directly
            out of a zone (as you would for a stove). (Default: 0).

    Returns:
        report: Reports, errors, warnings, etc.
        rooms: The input Rooms with process loads assigned to them.
"""

ghenv.Component.Name = 'HB Process Load'
ghenv.Component.NickName = 'Process'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:  # import the honeybee extension
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.load.process import Process
    from honeybee_energy.lib.schedules import schedule_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, longest_list
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    rooms = [room.duplicate() for room in _rooms]

    # set default values and check the inputs
    use_category_ = ['Process'] if len(use_category_) == 0 else use_category_
    radiant_fract_ = [0.0] if len(radiant_fract_) == 0 else radiant_fract_
    latent_fract_ = [0.0] if len(latent_fract_) == 0 else latent_fract_
    lost_fract_ = [0.0] if len(lost_fract_) == 0 else lost_fract_
    for i, sched in enumerate(_schedule):
        if isinstance(sched, str):
            _schedule[i] = schedule_by_identifier(sched)

    # loop through the rooms and assign process loads
    for i, room in enumerate(rooms):
        load_watts = longest_list(_watts, i)
        if load_watts != 0:
            name = clean_and_id_ep_string('Process') if len(_name_) == 0 else \
                clean_ep_string(longest_list(_name_, i))
            process = Process(
                '{}..{}'.format(name, room.identifier), load_watts,
                longest_list(_schedule, i), longest_list(_fuel_type, i),
                longest_list(use_category_, i), longest_list(radiant_fract_, i),
                longest_list(latent_fract_, i), longest_list(lost_fract_, i)
            )
            room.properties.energy.add_process_load(process)
