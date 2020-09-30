# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create parameters with criteria for sizing the heating and cooling system.
-

    Args:
        ddy_file_: An optional path to a .ddy file on your system, which contains
            information about the design days used to size the hvac system. If None,
            honeybee will look for a .ddy file next to the .epw and extract all
            99.6% and 0.4% design days.
        filter_ddays_: Boolean to note whether the design days in the ddy_file_
            should be filtered to only include 99.6% and 0.4% design days. If None
            or False, all design days in the ddy_file_ will be incorporated into
            the sizing parameters. This can also be the integer 2 to filter for
            99.0% and 1.0% design days.
        _heating_fac_: A number that will get multiplied by the peak heating load
            for each zone in the model in order to size the heating system for
            the model. Must be greater than 0. Default: 1.25.
        _cooling_fac_: A number that will get multiplied by the peak cooling load
            for each zone in the model in order to size the cooling system for
            the model. Must be greater than 0. Default: 1.15.
    
    Returns:
        sizing: Parameters with criteria for sizing the heating and cooling system.
            These can be connected to the "HB Simulation Parameter" component in
            order to specify settings for the EnergyPlus simulation.
"""

ghenv.Component.Name = "HB Sizing Parameter"
ghenv.Component.NickName = 'SizingPar'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    from honeybee_energy.simulation.sizing import SizingParameter
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))


# set default sizing factors
heating_fac = 1.25 if _heating_fac_ is None else _heating_fac_
cooling_fac = 1.15 if _cooling_fac_ is None else _cooling_fac_

# create the object
sizing = SizingParameter(None, heating_fac, cooling_fac)

# apply design days from ddy
if ddy_file_ is not None:
    if filter_ddays_ == 1:
        sizing.add_from_ddy_996_004(ddy_file_)
    elif filter_ddays_ == 2:
        sizing.add_from_ddy_990_010(ddy_file_)
    else:
        sizing.add_from_ddy(ddy_file_)
