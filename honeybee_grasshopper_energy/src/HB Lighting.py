# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create a Lighting object that can be used to create a ProgramType or be assigned
directly to a Room.
-

    Args:
        _name_: Text to set the name for the Lighting and to be incorporated
            into a unique Lighting identifier. If None, a unique name will
            be generated.
         _watts_per_area: A numerical value for the lighting power density in
            Watts per square meter of floor area.
        _schedule: A fractional for the use of lights over the course of the year.
            The fractional values will get multiplied by the _watts_per_area to
            yield a complete lighting profile.
        _radiant_fract_: A number between 0 and 1 for the fraction of the total
            lighting load given off as long wave radiant heat.
            Default: 0.32 (representative of pendant lighting).
        _visible_fract_: A number between 0 and 1 for the fraction of the total
            lighting load given off as short wave visible light.
            Default: 0.25  (representative of pendant lighting).
        return_fract_: A number between 0 and 1 for the fraction of the total
            lighting load that goes into the zone return air (into the zone outlet
            node). Default: 0.0 (representative of pendant lighting).
    
    Returns:
        lighting: A Lighting object that can be used to create a ProgramType or
            be assigned directly to a Room.
"""

ghenv.Component.Name = "HB Lighting"
ghenv.Component.NickName = 'Lighting'
ghenv.Component.Message = '0.1.1'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = "3"

import uuid

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.load.lighting import Lighting
    from honeybee_energy.lib.schedules import schedule_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # make a default Lighting name if none is provided
    if _name_ is None:
        name = "Lighting_{}".format(uuid.uuid4())
    else:
        name = clean_and_id_ep_string(_name_)

    # get the schedule
    if isinstance(_schedule, str):
        _schedule = schedule_by_identifier(_schedule)

    # get default radiant, visible, and return fractions
    return_fract_ = return_fract_ if return_fract_ is not None else 0.0
    _radiant_fract_ = _radiant_fract_ if _radiant_fract_ is not None else 0.32
    _visible_fract_ = _visible_fract_ if _visible_fract_ is not None else 0.25

    # create the Lighting object
    lighting = Lighting(name, _watts_per_area, _schedule,
                        return_fract_, _radiant_fract_, _visible_fract_)
    if _name_ is not None:
        lighting.display_name = _name_