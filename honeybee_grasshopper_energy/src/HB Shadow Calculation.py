# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create settings for the EnergyPlus Shadow Calculation.
-

    Args:
        _solar_dist_: An integer or text desribing how EnergyPlus should treat beam solar
            radiation and reflectances from surfaces that strike the building surfaces.
            Default - "FullExteriorWithReflections". Choose from the following.
            0 = "MinimalShadowing" - In this case, exterior shadowing is only computed
                for windows and not for other opaque surfaces that might have their
                surface temperature affected by the sun. All beam solar radiation
                entering the zone is assumed to fall on the floor. A simple window
                view factor calculation will be used to distribute incoming diffuse
                solar energy between interior surfaces.
            1 = "FullExterior" - The simulation will perform the solar calculation
                in a manner that only accounts for direct sun and whether it is
                blocked by surrounding context geometry.  For the inside of the
                building, all beam solar radiation entering the zone is assumed
                to fall on the floor. A simple window view factor calculation will
                be used to distribute incoming diffuse solar energy between
                interior surfaces.
            2 = "FullInteriorAndExterior" - The simulation will perform the solar
                calculation in a manner that models the direct sun (and wheter it
                is blocked by outdoor context goemetry.  It will also ray trace
                the direct sun on the interior of zones to distribute it correctly
                between interior surfaces.  Any indirect sun or sun bouncing off
                of objects will not be modled.
            3 = "FullExteriorWithReflections" - The simulation will perform the
                solar calculation in a manner that accounts for both direct sun
                and the light bouncing off outdoor surrounding context.  For the
                inside of the building, all beam solar radiation entering the zone
                is assumed to fall on the floor. A simple window view factor
                calculation will be used to distribute incoming diffuse solar
                energy between interior surfaces.
            4 = "FullInteriorAndExteriorWithReflections" - The simulation will
                perform the solar calculation in a manner that accounts for light
                bounces that happen both outside and inside the zones.  This is the
                most accurate method and is the one assigned by default.  Note that,
                if you use this method, EnergyPlus will give Severe warnings if
                your zones have concave geometry (aka. are "L"-shaped).  Such
                geometries are not supported by this solar distribution calculation
                and it is recommeded that you either break up your zones in this
                case or not use this solar distribution method.
        _calc_method_: Text noting whether CPU-based polygon clipping method or GPU-based
            pixel counting method should be used. For low numbers of shading
            surfaces (less than ~200), PolygonClipping requires less runtime than
            PixelCounting. However, PixelCounting runtime scales significantly
            better at higher numbers of shading surfaces. PixelCounting also has
            no limitations related to zone concavity when used with any
            “FullInterior” solar distribution options. (Default: PolygonClipping).
            Choose from the following:
                * PolygonClipping
                * PixelCounting
        _update_method_: Text describing how often the solar and shading calculations are
            updated with respect to the flow of time in the simulation. (Default: Periodic)
            Choose from the following:
                * Periodic
                * Timestep
        _frequency_: Integer for the number of days in each period in
            which a unique shadow calculation will be performed. This field is only
            used if the AverageOverDaysInFrequency method is used in the previous
            field. Default - 30.
        _max_figures_: Integer for the number of figures used in shadow overlaps.
            Default - 15000.
    
    Returns:
        shadow_calc: A ShadowCalculation object that can be connected to the
            "HB Simulation Parameter" component in order to specify settings
            for the EnergyPlus Shadow Calculation.
"""

ghenv.Component.Name = "HB Shadow Calculation"
ghenv.Component.NickName = 'ShadowCalc'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:
    from honeybee_energy.simulation.shadowcalculation import ShadowCalculation
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))


# dictionary to convert to acceptable solar distributions
SOLAR_DISTRIBUTIONS = {
    '0': 'MinimalShadowing',
    '1': 'FullExterior',
    '2': 'FullInteriorAndExterior',
    '3': 'FullExteriorWithReflections',
    '4': 'FullInteriorAndExteriorWithReflections',
    'MinimalShadowing': 'MinimalShadowing',
    'FullExterior': 'FullExterior',
    'FullInteriorAndExterior': 'FullInteriorAndExterior',
    'FullExteriorWithReflections': 'FullExteriorWithReflections',
    'FullInteriorAndExteriorWithReflections': 'FullInteriorAndExteriorWithReflections'
    }


# process the solar distribution
try:
    _solar_dist_ = SOLAR_DISTRIBUTIONS[_solar_dist_] if _solar_dist_ is not None \
        else 'FullExteriorWithReflections'
except KeyError:
    raise ValueError(' Input _solar_dist_ "{}" is not valid.\nChoose from the '
        'following:\n{}'.format(_solar_dist_, SOLAR_DISTRIBUTIONS.keys()))

# set other default values
_calc_method_ = _calc_method_ if _calc_method_ is not None else 'PolygonClipping'
_update_method_ = _update_method_ if _update_method_ is not None else 'Periodic'
_frequency_ = _frequency_ if _frequency_ is not None else 30
_max_figures_ = _max_figures_ if _max_figures_ is not None else 15000

# create the object
shadow_calc = ShadowCalculation(
    _solar_dist_, _calc_method_, _update_method_, _frequency_, _max_figures_)
