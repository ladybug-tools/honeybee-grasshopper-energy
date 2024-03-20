# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Set the properites of a Model's electric load center, which governs how on-site
electricity generation is converted and distributed.
-

    Args:
        _model: A Honeybee Model for which the electric load center properties will be set.
            This Model should include on-site power generation objects, like
            Shades with PV properties assigned, in order for the inputs here
            to have an effect on the simulation.
        _inverter_eff_: A number between 0 and 1 for the load centers's inverter nominal
            rated DC-to-AC conversion efficiency. An inverter converts DC power,
            such as that output by photovoltaic panels, to AC power, such as
            that distributed by the electrical grid and is available from
            standard electrical outlets. Inverter efficiency is defined as the
            inverter's rated AC power output divided by its rated DC power
            output. (Default: 0.96).
        _dc_to_ac_size_: A positive number (typically greater than 1) for the ratio of the
            inverter's DC rated size to its AC rated size. Typically, inverters
            are not sized to convert the full DC output under standard test
            conditions (STC) as such conditions rarely occur in reality and
            therefore unnecessarily add to the size/cost of the inverter. For a
            system with a high DC to AC size ratio, during times when the 
            DC power output exceeds the inverter's rated DC input size, the inverter
            limits the array's power output by increasing the DC operating voltage,
            which moves the arrays operating point down its current-voltage (I-V)
            curve. The default value of 1.1 is reasonable for most systems. A
            typical range is 1.1 to 1.25, although some large-scale systems have
            ratios of as high as 1.5. The optimal value depends on the system's
            location, array orientation, and module cost. (Default: 1.1).

    Returns:
        model: The input Honeybee Model with the electric load center properties set.
"""

ghenv.Component.Name = 'HB Electric Load Center'
ghenv.Component.NickName = 'ElectricCenter'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '4 :: HVAC'
ghenv.Component.AdditionalHelpFromDocStrings = '6'

try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # duplicate the input Model to avoid editing it
    model = _model.duplicate()

    # set default properties
    _inverter_eff_ = 0.96 if _inverter_eff_ is None else _inverter_eff_
    _dc_to_ac_size_ = 1.1 if _dc_to_ac_size_ is None else _dc_to_ac_size_
    model.properties.energy.electric_load_center.inverter_efficiency = _inverter_eff_
    model.properties.energy.electric_load_center.inverter_dc_to_ac_size_ratio = _inverter_eff_
