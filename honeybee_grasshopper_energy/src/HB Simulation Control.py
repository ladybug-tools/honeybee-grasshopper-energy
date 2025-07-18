# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create simulation controls with instructions for which types of EnergyPlus
calculations to run.
-

    Args:
        _do_zone_sizing_: Boolean for whether the zone sizing calculation
            should be run. Default: True.
        _do_system_sizing_: Boolean for whether the system sizing calculation
            should be run. Default: True.
        _do_plant_sizing_: Boolean for whether the plant sizing calculation
            should be run. Default: True.
        _for_sizing_period_: Boolean for whether the simulation should
            be run for the sizing periods. Default: False.
        _for_run_period_: Boolean for whether the simulation should
            be run for the run periods. Default: True.

    Returns:
        sim_control: A SimulationControl object that can be connected to the
            "HB Simulation Parameter" component in order to specify which
            types of EnergyPlus calculations to run.
"""

ghenv.Component.Name = 'HB Simulation Control'
ghenv.Component.NickName = 'SimControl'
ghenv.Component.Message = '1.9.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from honeybee_energy.simulation.control import SimulationControl
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import turn_off_old_tag
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
turn_off_old_tag(ghenv.Component)


# set default values
_do_zone_sizing_ = _do_zone_sizing_ if _do_zone_sizing_ is not None else True
_do_system_sizing_ = _do_system_sizing_ if _do_system_sizing_ is not None else True
_do_plant_sizing_ = _do_plant_sizing_ if _do_plant_sizing_ is not None else True
_for_sizing_period_ = _for_sizing_period_ if _for_sizing_period_ is not None else False
_for_run_period_ = _for_run_period_ if _for_run_period_ is not None else True

# create the object
sim_control = SimulationControl(_do_zone_sizing_, _do_system_sizing_, _do_plant_sizing_,
                                _for_sizing_period_, _for_run_period_)