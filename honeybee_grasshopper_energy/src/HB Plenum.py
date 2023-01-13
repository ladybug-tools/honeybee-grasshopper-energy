# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Turn Honeybee Rooms into Plenums with no internal loads.
_
This includes removing all people, lighting, equipment, hot water, and mechanical
ventilation. By default, the heating/cooling system and setpoints will also be
removed but they can optionally be kept. Infiltration is kept by default but
can optionally be removed as well.
_
This is useful to appropriately assign properties for closets, underfloor spaces,
and drop ceilings.
-

    Args:
        _rooms: Honeybee Rooms to be converted into plenums.
        conditioned_: Boolean to indicate whether the plenum is conditioned with a
            heating/cooling system. If True, the setpoints of the Room will also
            be kept in addition to the heating/cooling system (Default: False).
        remove_infilt_: Boolean to indicate whether infiltration should be removed from
            the Rooms. If False, infiltration will be preserved and will be the
            only load assinged to the plenum. (Default: False).
        include_floor_: Boolean to indicate whether the floor area of the plenum contributes
            to the Model it is a part of. Note that this will not affect the
            floor_area property of this Room but it will ensure the Room's
            floor area is excluded from any calculations when the Room is part
            of a Model and when it is simulated in EnergyPlus.

    Returns:
        rooms: Rooms that have had their interinal loads removed to reflect a
            plenum space.
"""

ghenv.Component.Name = 'HB Plenum'
ghenv.Component.NickName = 'Plenum'
ghenv.Component.Message = '1.6.0'
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
        room.properties.energy.make_plenum(conditioned_, remove_infilt_, include_floor_)
