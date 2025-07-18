# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Parse a zone sizing (ZSZ) csv result file from an energy simulation to get data
collections for the cooling/heating load over the peak design day.
-

    Args:
        _zsz: Full path to a zone sizing (ZSZ) csv result file that was
            generated by EnergyPlus.
    
    Returns:
        cooling_load: a list of HourlyContinuousCollections for zone cooling load.
            There will be one data collection per conditioned zone in the model.
        heating_load: a list of HourlyContinuousCollections for zone heating load.
            There will be one data collection per conditioned zone in the model.
"""

ghenv.Component.Name = 'HB Read Zone Sizing'
ghenv.Component.NickName = 'ReadZSZ'
ghenv.Component.Message = '1.9.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '6 :: Result'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from honeybee_energy.result.zsz import ZSZ
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    zsz_obj = ZSZ(_zsz)
    cooling_load = zsz_obj.cooling_load_data
    heating_load = zsz_obj.heating_load_data
