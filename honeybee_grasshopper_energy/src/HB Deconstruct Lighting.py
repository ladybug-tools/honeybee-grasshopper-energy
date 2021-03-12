# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Deconstruct a Lighting object into its constituient properties.
-

    Args:
        _lighting: A Lighting object to be deconstructed.
    
    Returns:
        name: Text string for the lighting display name.
         watts_per_area: A numerical value for the lighting power density in
            Watts per square meter of floor area.
        schedule: A fractional for the use of lights over the course of the year.
            The fractional values will get multiplied by the watts_per_area to
            yield a complete lighting profile.
        radiant_fract: A number between 0 and 1 for the fraction of the total
            lighting load given off as long wave radiant heat.
        visible_fract: A number between 0 and 1 for the fraction of the total
            lighting load given off as short wave visible light.
        return_fract: A number between 0 and 1 for the fraction of the total
            lighting load that goes into the zone return air.
        baseline: The baseline lighting power density in W/m2 of floor area. This
            baseline is useful to track how much better the installed lights
            are in comparison to a standard like ASHRAE 90.1.
"""

ghenv.Component.Name = "HB Deconstruct Lighting"
ghenv.Component.NickName = 'DecnstrLighting'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = "0"

try:
    from honeybee_energy.load.lighting import Lighting
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _lighting is not None:
    # check the input
    assert isinstance(_lighting, Lighting), \
        'Expected Lighting object. Got {}.'.format(type(_lighting))

    # get the properties of the object
    name = _lighting.display_name
    watts_per_area = _lighting.watts_per_area
    schedule = _lighting.schedule
    radiant_fract = _lighting.radiant_fraction
    visible_fract = _lighting.visible_fraction
    return_fract = _lighting.return_air_fraction
    baseline = _lighting.baseline_watts_per_area
