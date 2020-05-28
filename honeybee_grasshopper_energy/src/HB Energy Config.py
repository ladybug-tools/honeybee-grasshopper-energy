# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Check the local configuration of the engines and data sets used by the honeybee
energy plugin. This is useful for verifying that everything has been installed
correctly and that the versions of the engines are as expected.
-

    Returns:
        os_install: The path to OpenStudio installation folder if it exists.
        ep_install: The path to EnergyPlus installation folder if it exists.
        hb_os_gem: The path to the honeybee_openstudio_gem if it exists. This gem
            contains libraries and measures for translating between Honeybee
            JSON schema and OpenStudio Model schema (OSM).
        standards: The path to the library of standards if it exists. This library
            contains the default Constructions, ConstructionSets, Schedules, and
            ProgramTypes. It can be extended by dropping IDF or Honeybee JOSN
            files into the appropriate sub-folder.
"""

ghenv.Component.Name = 'HB Energy Config'
ghenv.Component.NickName = 'EnergyConfig'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from honeybee_energy.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))


os_install = folders.openstudio_path
ep_install = folders.energyplus_path
hb_os_gem = folders.honeybee_openstudio_gem_path
standards = folders.standards_data_folder
