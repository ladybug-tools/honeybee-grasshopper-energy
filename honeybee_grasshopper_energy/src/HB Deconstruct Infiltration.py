# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Deconstruct an Infiltration object into its constituient properties.
-

    Args:
        _infil: An Infiltration object to be deconstructed.
    
    Returns:
        name: Text string for the infiltration display name.
        flow_per_ext_area: A numerical value for the intensity of infiltration
            in m3/s per square meter of exterior surface area. Typical values for
            this property are as follows (note all values are at typical building
            pressures of ~4 Pa):
                * 0.0001 (m3/s per m2 facade) - Tight building
                * 0.0003 (m3/s per m2 facade) - Average building
                * 0.0006 (m3/s per m2 facade) - Leaky building
        schedule: A fractional schedule for the infiltration over the course
            of the year. The fractional values will get multiplied by the
            flow_per_exterior_area to yield a complete infiltration profile.
"""

ghenv.Component.Name = "HB Deconstruct Infiltration"
ghenv.Component.NickName = 'DecnstrInfiltration'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = "0"

try:
    from honeybee_energy.load.infiltration import Infiltration
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _infil is not None:
    # check the input
    assert isinstance(_infil, Infiltration), \
        'Expected Infiltration object. Got {}.'.format(type(_infil))
    
    # get the properties of the object
    name = _infil.display_name
    flow_per_ext_area = _infil.flow_per_exterior_area
    schedule = _infil.schedule
