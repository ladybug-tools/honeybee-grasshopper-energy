# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Deconstruct an opaque or window construction into its constituient materials.
-

    Args:
        _constr: An opaque or window construction to be deconstructed. This can
            also be text for an opaque or window construction to be looked
            up in the construction library.

    Returns:
        materials: List of material objects that make up the construction
            (ordered from outside to inside).
        layers: List of material names that make up the construction
            (ordered from outside to inside).
        r_val_si: R-value of the construction in m2-K/W. Note that R-values do NOT
            include the resistance of air films on either side of the construction.
        r_val_ip: R-value of the construction in h·ft2·°F/Btu. Note that R-values do NOT
            include the resistance of air films on either side of the construction.
        u_fac_si: U-factor of the construction in W/m2-K.  Note that U-factors
            include the resistance of air films on either side of the construction.
        u_fac_ip: U-factor of the construction in Btu/h·ft2·°F.  Note that U-factors
            include the resistance of air films on either side of the construction.
        t_sol: The unshaded shortwave solar transmittance of the construction at normal
            incidence. Note that 'unshaded' in this case means that all blind +
            shade materials in the construction are ignored. Also note that the
            solar transmittance ouput here is only for shortwave solar irradiation.
            So it is NOT the same as SHGC or G-Value, which also includes the solar
            heat that is absorbed by the construction and then conducts to the indoors.
        t_vis: The unshaded visible transmittance of the window at normal incidence.
            Note that 'unshaded' in this case means that all blind + shade
            materials in the construction are ignored.
"""

ghenv.Component.Name = "HB Deconstruct Construction"
ghenv.Component.NickName = 'DecnstrConstr'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "Energy"
ghenv.Component.SubCategory = "1 :: Construction"
ghenv.Component.AdditionalHelpFromDocStrings = "2"


try:  # import the honeybee-energy dependencies
    from honeybee_energy.construction.opaque import OpaqueConstruction
    from honeybee_energy.construction.window import WindowConstruction
    from honeybee_energy.lib.constructions import opaque_construction_by_name
    from honeybee_energy.lib.constructions import window_construction_by_name
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))
try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
try:
    from ladybug.datatype.rvalue import RValue
    from ladybug.datatype.uvalue import UValue
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # check the input
    if isinstance(_constr, str):
        try:
            _constr = opaque_construction_by_name(_constr)
        except ValueError:
            _constr = window_construction_by_name(_constr)
    else:
        assert isinstance(_constr, (OpaqueConstruction, WindowConstruction)), \
            'Expected OpaqueConstruction or WindowConstruction. ' \
            'Got {}.'.format(type(_constr))
    
    # get the materials, r-value and u-factor
    materials = _constr.materials
    layers = _constr.layers
    r_val_si = _constr.r_value
    r_val_ip = RValue().to_ip([r_val_si], 'm2-K/W')[0][0]
    u_fac_si = _constr.u_factor
    u_fac_ip = UValue().to_ip([u_fac_si], 'W/m2-K')[0][0]
    
    # get the transmittance
    if isinstance(_constr, WindowConstruction):
        t_sol = _constr.unshaded_solar_transmittance
        t_vis = _constr.unshaded_visible_transmittance
    else:
        t_sol = 0
        t_vis = 0
