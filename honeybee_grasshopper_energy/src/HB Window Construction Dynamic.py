# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create an EnergyPlus window construction with any number of dynamic states.
-

    Args:
        _name_: Text to set the name for the Construction and to be incorporated
            into a unique Construction identifier.
        constructions: A list of WindowConstruction objects that define the various
            states that the dynamic window can assume. Inputs can be either
            the identifiers of constructions within the library or custom
            constructions made with the "HB Window Construction" component.
            Note that a native Grasshopper "Merge" component can be used to
            help order the constructions correctly for the input here since
            the order here determines how the construction states are refenced
            in the schedule.
        _schedule: A control schedule that dictates which constructions that are active
            at given times throughout the simulation. Inputs can be either
            the identifiers of schedules within the library or custom
            schedules made with any of the honeybee schedule components.
            The values of the schedule should be intergers and range from 0 to one
            less then the number of constructions. Zero indicates that the first
            construction is active, one indicates that the second on is active, etc.
            The schedule type limits of this schedule should be "Control Level."
            If building custom schedule type limits that describe a particular
            range of states, the type limits should be "Discrete" and the unit
            type should be "Mode," "Control," or some other fractional unit.

    Returns:
        constr: A dynamic window construction that can be assigned to Honeybee
            Apertures or ConstructionSets.
"""

ghenv.Component.Name = 'HB Window Construction Dynamic'
ghenv.Component.NickName = 'WindowConstrDyn'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = "1 :: Constructions"
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.construction.dynamic import WindowConstructionDynamic
    from honeybee_energy.lib.constructions import window_construction_by_identifier
    from honeybee_energy.lib.schedules import schedule_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    name = clean_and_id_ep_string('DynamicWindowConstruction') if _name_ is None else \
        clean_ep_string(_name_)

    # get objects from the library if they are strings
    constr_objs = []
    for con in _constructions:
        if isinstance(con, str):
            con = window_construction_by_identifier(con)
        constr_objs.append(con)
    if isinstance(_schedule, str):
        _schedule = schedule_by_identifier(_schedule)

    # create the construction object
    constr = WindowConstructionDynamic(name, constr_objs, _schedule)
    if _name_ is not None:
        constr.display_name = _name_
