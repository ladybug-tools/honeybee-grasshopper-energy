# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Turn Honeybee Rooms into Plenums with no internal loads.
_
This includes removing all people, lighting equipment, mechanical ventilation. By
default, the heating/cooling system and setpoints will also be removed but they
can optionally be kept. Infiltration is kept by default but can optionally be
removed as well.
_
This is useful to appropriately assign properties for closets, underfloor spaces,
and drop ceilings.
-

    Args:
        _HBZones: Honeybee Rooms to be converted into plenums.
        conditioned_: Boolean to indicate whether the plenum is conditioned with a
            heating/cooling system. If True, the setpoints of the Room will also
            be kept in addition to the heating/cooling system (Default: False).
        remove_infilt_: Boolean to indicate whether infiltration should be removed
            from the Rooms. (Default: False).

    Returns:
        rooms: Rooms that have had their interinal loads removed to reflect a
            plenum space.
"""

ghenv.Component.Name = 'HB Plenum'
ghenv.Component.NickName = 'Plenum'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '5'


try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    rooms = [room.duplicate() for room in _rooms]  # duplicate to avoid editing input

    for room in rooms:
        # remove or add the HVAC system as needed
        if conditioned_ and not room.properties.energy.is_conditioned:
            room.properties.energy.add_default_ideal_air()
        elif not conditioned_:
            room.properties.energy.hvac = None

        # remove the loads and reapply infiltration/setpoints as needed
        infilt = None if remove_infilt_ else room.properties.energy.infiltration
        setpt = room.properties.energy.setpoint if conditioned_ else None
        room.properties.energy.program_type = None
        room.properties.energy.people = None
        room.properties.energy.lighting = None
        room.properties.energy.electric_equipment = None
        room.properties.energy.gas_equipment = None
        room.properties.energy.ventilation = None
        room.properties.energy.infiltration = infilt
        room.properties.energy.setpoint = setpt
