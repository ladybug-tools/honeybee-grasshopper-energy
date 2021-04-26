# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Convert infiltration flow per exterior area measured at a particular blower door pressure
to flow per exterior area measured at a typical building pressure.
_
This is accomplished by computing a normalized-area air mass flow coefficient that
is derived the power law relationship between pressure and air flow.
    Cqa = Qblow / dPblow^n
And then using the coefficient to approximate air flow at typical building pressure.
    Qbldg = Cqa * dPbldg^n
.
where:
    Cqa: Air mass flow coefficient per unit meter at 1 Pa [kg/m2/s/P^n]
    Qblow: Blower-induced volumetric air flow rate per area [m3/s/m2]
    dPblow: Blower-induced change in pressure across building envelope orifice [Pa]
    Qbldg: Typical building volumetric air flow rate per area [m3/s/m2]
    dPbldg: Typical building change in pressure across building envelope orifice [Pa]
    d: Air density [1.2041 kg/m3]
    n: Air mass flow exponent [0.65]
-

    Args:
        _infilt_per_exterior: A numerical value for the intensity of air flow induced by
            blower pressure in m3/s per square meter of exterior surface area.
        _blower_pressure_: A number representing the pressure differential in Pascals (Pa)
            between indoors/outdoors at which the specified _infilt_per_exterior
            occurs. Typical pressures induced by blower doors are 75 Pa and
            50 Pa. (Default: 75).
        _bldg_pressure_: The reference air pressure difference across building envelope
            under typical conditions in Pascals. (Default: 4).

    Returns:
        infilt: The intensity of infiltration in m3/s per square meter of exterior
            surface area at the input _bldg_pressure_.
        C_qa: Air mass flow coefficient per square meter at 1 Pa [kg/m2/s/P^n].
"""

ghenv.Component.Name = 'HB Blower Pressure Converter'
ghenv.Component.NickName = 'BlowerPresure'
ghenv.Component.Message = '1.2.1'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from honeybee_energy.properties.room import RoomEnergyProperties
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set default values
    _blower_pressure_ = 75 if _blower_pressure_ is None else _blower_pressure_
    _bldg_pressure_ = 4 if _bldg_pressure_ is None else _bldg_pressure_

    # compute coeffiecient and airflow
    C_qa = RoomEnergyProperties.solve_norm_area_flow_coefficient(
        _infilt_per_exterior, air_density=1, delta_pressure=_blower_pressure_)
    infilt = C_qa * (_bldg_pressure_ ** 0.65)
