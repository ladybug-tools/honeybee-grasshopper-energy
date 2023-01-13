# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Set Honeybee Rooms to be conditioned or unconditioned with a heating/cooling system.
_
If _conditioned is True and the connected rooms are not currently conditioned,
an Ideal Air System will be assigned to them. Otherwise, if they are already
conditioned, the existing HVAC system will be left as it is.
-

    Args:
        _rooms: Honeybee Rooms to have their conditioned property set.
        _conditioned: Boolean to indicate whether the rooms are conditioned with a
            heating/cooling system.

    Returns:
        rooms: Rooms that have had their interinal loads removed to reflect a
            plenum space.
"""

ghenv.Component.Name = 'HB Set Conditioned'
ghenv.Component.NickName = 'Conditioned'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '4 :: HVAC'
ghenv.Component.AdditionalHelpFromDocStrings = '1'


try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    rooms = [room.duplicate() for room in _rooms]  # duplicate to avoid editing input
    if _conditioned:
        for room in rooms:
            if not room.properties.energy.is_conditioned:
                room.properties.energy.add_default_ideal_air()
    else:
        for room in rooms:
            room.properties.energy.hvac = None
