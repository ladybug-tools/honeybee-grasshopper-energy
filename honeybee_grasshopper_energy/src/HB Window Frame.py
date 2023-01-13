# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a window frame matrial that can be assigned to a Window Construction by
plugging it into the frame_ input of the "HB Window Construction" component.
-

    Args:
        _name: Text to set the name for the frame material and to be incorporated into
            a unique material identifier.
        _width: Number for the width of frame in plane of window [m]. The frame
            width is assumed to be the same on all sides of window.
        _conductance: Number for the thermal conductance of the frame material measured
            from inside to outside of the frame surface (no air films) and taking
            2D conduction effects into account [W/m2-K]. Values for typical frame
            materials are as follows.
                * Aluminum with Thermal Break - 56.4 W/m2-K
                * Aluminum One-Sided (Flush) - 10.7 W/m2-K
                * Wood - 3.5 W/m2-K
                * Vinyl - 2.3 W/m2-K
        _edge_to_cent_: Number between 0 and 4 for the ratio of the glass conductance near
            the frame (excluding air films) divided by the glass conductance
            at the center of the glazing (excluding air films). This is used
            only for multi-pane glazing constructions. This ratio should
            usually be greater than 1.0 since the spacer material that separates
            the glass panes is usually more conductive than the gap between panes.
            A value of 1 effectively indicates no spacer. Values should usually be
            obtained from the LBNL WINDOW program so that the unique characteristics
            of the window construction can be accounted for. (Default: 1).
        outside_proj_: Number for the distance that the frame projects outward from the
            outside face of the glazing [m]. This is used to calculate shadowing
            of frame onto glass, solar absorbed by the frame, IR emitted and
            absorbed by the frame, and convection from frame. (Default: 0).
        inside_proj_: Number for the distance that the frame projects inward from the
            inside face of the glazing [m]. This is used to calculate solar
            absorbed by the frame, IR emitted and absorbed by the frame, and
            convection from frame. (Default: 0).
        _therm_absp_: A number between 0 and 1 for the fraction of incident long
            wavelength radiation that is absorbed by the material. (Default: 0.9).
        _sol_absp_: A number between 0 and 1 for the fraction of incident solar
            radiation absorbed by the material. (Default: 0.7).
        _vis_absp_: A number between 0 and 1 for the fraction of incident
            visible wavelength radiation absorbed by the material.
            Default value is the same as the _sol_absp_.

    Returns:
        frame: A window frame material that can be assigned to a Honeybee
            Window construction.
"""

ghenv.Component.Name = 'HB Window Frame'
ghenv.Component.NickName = 'WindowFrame'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '1 :: Constructions'
ghenv.Component.AdditionalHelpFromDocStrings = '6'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.material.frame import EnergyWindowFrame
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set the default material properties
    _edge_to_cent_ = 1 if _edge_to_cent_ is None else _edge_to_cent_
    outside_proj_ = 0 if outside_proj_ is None else outside_proj_
    inside_proj_ = 0 if inside_proj_ is None else inside_proj_
    _therm_absp_ = 0.9 if _therm_absp_ is None else _therm_absp_
    _sol_absp_ = 0.7 if _sol_absp_ is None else _sol_absp_
    name = clean_and_id_ep_string('OpaqueNoMassMaterial') if _name_ is None else \
        clean_ep_string(_name_)

    # create the material
    frame = EnergyWindowFrame(
        name, _width, _conductance, _edge_to_cent_, outside_proj_, inside_proj_,
        _therm_absp_, _sol_absp_, _vis_absp_)
    if _name_ is not None:
        frame.display_name = _name_
