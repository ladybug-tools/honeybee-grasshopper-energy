# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Create a boundary condition representing a custom temperature and/or heat transfer
coefficient on the other side of a face.
-

    Args:
        _temperature_: A temperature value in Celsius to note the temperature on the
            other side of the object. If unspecified, the outdoor air
            temperature will be used.
        heat_coeff_: A value in W/m2-K to indicate the combined convective/radiative film
            coefficient. If equal to 0, then the specified temperature above is
            equal to the exterior surface temperature. Otherwise, the temperature
            above is considered the outside air temperature and this coefficient
            is used to determine the difference between this outside air
            temperature and the exterior surface temperature. (Default: 0).

    Returns:
        bc: A BoundaryCondition object that can be assigned to any honeybee Face object (using
            the "HB Face" component or the "HB Properties by Guide Surface").
"""

ghenv.Component.Name = 'HB Other Side Temperature'
ghenv.Component.NickName = 'OtherTemp'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '0 :: Basic Properties'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.altnumber import autocalculate
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import honeybee_energy dependencies
    from honeybee_energy.boundarycondition import OtherSideTemperature
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))


_temperature_ = _temperature_ if _temperature_ is not None else autocalculate
heat_coeff_ = heat_coeff_ if heat_coeff_ is not None else 0
bc = OtherSideTemperature(_temperature_, heat_coeff_)
