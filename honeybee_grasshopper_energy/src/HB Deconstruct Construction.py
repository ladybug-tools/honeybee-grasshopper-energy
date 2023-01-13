# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


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
        layers: List of material identifiers that make up the construction
            (ordered from outside to inside).
        r_val_si: R-value of the construction in m2-K/W. Note that R-values do NOT
            include the resistance of air films on either side of the construction.
        r_val_ip: R-value of the construction in h-ft2-F/Btu. Note that R-values do NOT
            include the resistance of air films on either side of the construction.
        u_fac_si: U-factor of the construction in W/m2-K.  Note that U-factors
            include the resistance of air films on either side of the construction.
        u_fac_ip: U-factor of the construction in Btu/h-ft2-F.  Note that U-factors
            include the resistance of air films on either side of the construction.
        shgc: The estimated solar heat gain coefficient (SHGC) of the construction.
            This value is produced by finding the solution to the relationship between
            U-value, Solar Transmittance, and SHGC as defined for the simple glazing
            system material in EnergyPlus. More information can be found
            at https://bigladdersoftware.com/epx/docs/9-5/engineering-reference/
            on this partticular sub-page of the engineering reference:
            window-calculation-module.html#step-4.-determine-layer-solar-transmittance
        t_sol: The unshaded shortwave solar transmittance of the construction at normal
            incidence. Note that 'unshaded' in this case means that all blind +
            shade materials in the construction are ignored.
        t_vis: The unshaded visible transmittance of the window at normal incidence.
            Note that 'unshaded' in this case means that all blind + shade
            materials in the construction are ignored.
"""

ghenv.Component.Name = 'HB Deconstruct Construction'
ghenv.Component.NickName = 'DecnstrConstr'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '1 :: Constructions'
ghenv.Component.AdditionalHelpFromDocStrings = '2'


try:  # import the honeybee-energy dependencies
    from honeybee_energy.construction.opaque import OpaqueConstruction
    from honeybee_energy.construction.window import WindowConstruction
    from honeybee_energy.construction.windowshade import WindowConstructionShade
    from honeybee_energy.construction.dynamic import WindowConstructionDynamic
    from honeybee_energy.lib.constructions import opaque_construction_by_identifier
    from honeybee_energy.lib.constructions import window_construction_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
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
            _constr = opaque_construction_by_identifier(_constr)
        except ValueError:
            _constr = window_construction_by_identifier(_constr)
    else:
        con_cls  = (OpaqueConstruction, WindowConstruction, WindowConstructionShade)
        assert isinstance(_constr, con_cls), \
            'Expected OpaqueConstruction, WindowConstruction, or WindowConstructionShade. ' \
            'Got {}.'.format(type(_constr))

    # get the materials, r-value and u-factor
    materials = _constr.materials
    layers = _constr.layers
    r_val_si = _constr.r_value
    r_val_ip = RValue().to_ip([r_val_si], 'm2-K/W')[0][0]
    u_fac_si = _constr.u_factor
    u_fac_ip = UValue().to_ip([u_fac_si], 'W/m2-K')[0][0]

    # give a warning if there's a negative R-value for a vertical surface
    if r_val_si <= 0:
        msg = 'Construction "{}" has an overall R-value that is less than the\n' \
            'resistance of vertically-oriented air films. This indicates that the ' \
            'construction is only suitable for horizontal/skylight geometry.'.format(
                _constr.display_name)
        print(msg)
        give_warning(ghenv.Component, msg)

    # get the transmittance
    win_types = (WindowConstruction, WindowConstructionShade, WindowConstructionDynamic)
    if isinstance(_constr, win_types):
        shgc = _constr.shgc
        t_sol = _constr.solar_transmittance
        t_vis = _constr.visible_transmittance
    else:
        shgc = 0
        t_sol = 0
        t_vis = 0
