# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Assign photovoltaic properties to a honeybee Shade such that it will generate
electricity in energy simulations.
-

    Args:
        _shades: Honeybee Shades to which photovoltaic properties will be assigned.
        _rated_efficiency_: A number between 0 and 1 for the rated nameplate efficiency
            of the photovoltaic solar cells under standard test conditions (STC).
            _
            Standard test conditions are 1,000 Watts per square meter solar
            irradiance, 25 degrees C cell temperature, and ASTM G173-03 standard
            spectrum. Nameplate efficiencies reported by manufacturers are typically
            under STC.
            _
            Standard poly- or mono-crystalline silicon modules tend to have
            rated efficiencies in the range of 14-17%. Premium high efficiency
            mono-crystalline silicon modules with anti-reflective coatings can
            have efficiencies in the range of 18-20%. Thin film photovoltaic
            modules typically have efficiencies of 11% or less. (Default: 0.15
            for standard silicon solar cells).
        _active_fraction_: The fraction of the parent Shade geometry that is covered in active
            solar cells. This fraction includes the difference between the PV
            panel (aka. PV module) area and the active cells within the panel
            as well as any losses for how the (typically rectangular) panels
            can be arranged on the Shade geometry. When the parent Shade
            geometry represents just the solar panels, this fraction is typically
            around 0.9 given that the framing elements of the panel reduce the
            overall active area. (Default: 0.9).
        _module_type_: Text or an integer to indicate the type of solar module. This is used
            to determine the temperature coefficients used in the simulation of the
            photovoltaic modules. Choose from the three options below. If unspecified,
            the module_type will be inferred from the rated_efficiency of these
            PVProperties using the rated efficiencies listed below.
            _
                * 0 - Standard - 12% <= rated_efficiency < 18%
                * 1 - Premium - rated_efficiency >= 18%
                * 2 - ThinFilm - rated_efficiency < 12%
        _mounting_type_: Text or an integer to indicate the type of mounting and/or tracking used
            for the photovoltaic array. Note that the OneAxis options have an axis
            of rotation that is determined by the azimuth of the parent Shade
            geometry. Also note that, in the case of one or two axis tracking,
            shadows on the (static) parent Shade geometry still reduce the
            electrical output, enabling the simulation to account for large
            context geometry casting shadows on the array. However, the effects
            of smaller detailed shading may be improperly accounted for and self
            shading of the dynamic panel geometry is only accounted for via the
            tracking_gcr property. Choose from the following. (Default: FixedOpenRack).
            _
                * 0 - FixedOpenRack - ground or roof mounting where the air flows freely 
                * 1 - FixedRoofMounted - mounting flush with the roof with limited air flow
                * 2 - OneAxis - a fixed tilt and azimuth, which define an axis of rotation
                * 3 - OneAxisBacktracking - same as OneAxis but with controls to reduce self-shade
                * 4 - TwoAxis - a dynamic tilt and azimuth that track the sun
        _loss_fraction_: A number between 0 and 1 for the fraction of the electricity output
            lost due to factors other than EPW climate conditions, panel
            efficiency/type, active area, mounting, and inverter conversion
            from DC to AC.
            _
            Factors that should be accounted for in this input include soiling,
            snow, wiring losses, electrical connection losses, manufacturer
            defects/tolerances/mismatch in cell characteristics, losses from power
            grid availability, and losses due to age or light-induced degradation.
            _
            Losses from these factors tend to be between 10-20% but can vary widely
            depending on the installation, maintenance and the grid to which the
            panels are connected. The loss_fraction_from_components staticmethod
            on this class can be used to estimate this value from the various
            factors that it is intended to account for. (Default: 0.14).
        tracking_gcr_: A number between 0 and 1 that ONLY APPLIES TO ARRAYS WITH ONE AXIS
            mounting_type.
            _
            The ground coverage ratio (GCR) is the ratio of module surface area
            to the area of the ground beneath the array, which is used to account
            for self shading of single-axis panels as they move to track the sun.
            A GCR of 0.5 means that, when the modules are horizontal, half of the
            surface below the array is occupied by the array. An array with wider
            spacing between rows of modules has a lower GCR than one with narrower
            spacing. A GCR of 1 would be for an array with no space between modules,
            and a GCR of 0 for infinite spacing between rows. Typical values
            range from 0.3 to 0.6. (Default: 0.4).
        _name_: An optional text name for the photovoltaic properties. This can be useful
            for keeping track of different photovoltaics when using several of
            these components. If unspecified, a unique one will be generated.

    Returns:
        report: Reports, errors, warnings, etc.
        shades: The input Shades with photovoltaic properties assigned.
"""

ghenv.Component.Name = 'HB Photovoltaic Properties'
ghenv.Component.NickName = 'Photovoltaic'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '4 :: HVAC'
ghenv.Component.AdditionalHelpFromDocStrings = '6'

import math

try:  # import the ladybug geometry dependencies
    from ladybug_geometry.geometry3d import Vector3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import honeybee_energy dependencies
    from honeybee_energy.generator.pv import PVProperties
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import angle_tolerance, conversion_to_meters
    from ladybug_rhino.grasshopper import all_required_inputs, \
        document_counter, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

# dictionaries to convert user input to enumerations
MODULE_TYPES = {
    'standard': 'Standard',
    'premium': 'Premium',
    'thinfilm': 'ThinFilm',
    '0': 'Standard',
    '1': 'Premium',
    '2': 'Standard'
}
MOUNTING_TYPES = {
    'fixedopenrack': 'FixedOpenRack',
    'fixedroofmounted': 'FixedRoofMounted',
    'oneaxis': 'OneAxis',
    'oneaxisbacktracking': 'OneAxisBacktracking',
    'twoaxis': 'TwoAxis',
    '0': 'FixedOpenRack',
    '1': 'FixedRoofMounted',
    '2': 'OneAxis',
    '3': 'OneAxisBacktracking',
    '4': 'TwoAxis',
}


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    shades = []
    for shade in _shades:
        shades.append(shade.duplicate())
        if math.degrees(Vector3D(0, 0, 1).angle(shade.normal)) - 90 > angle_tolerance:
            msg = 'Shade "{}" is pointing downwards, which is atypical of photovoltaics.\n' \
                'You will likely want to flip the geometry to have it point upwards to ' \
                'the sky.'.format(shade.display_name)
            print(msg)
            give_warning(ghenv.Component, msg)

    # assign defaults for the PV properties
    display_name = 'Photovoltaic Array {}'.format(document_counter('pv_count')) \
        if _name_ is None else _name_
    pv_id = clean_ep_string(display_name)
    eff = _rated_efficiency_ if _rated_efficiency_ is not None else 0.15
    act_fraction = _active_fraction_ if _active_fraction_ is not None else 0.9
    mod_type = MODULE_TYPES[_module_type_.lower()] \
        if _module_type_ is not None else None
    mount_type = MOUNTING_TYPES[_mounting_type_.lower()] \
        if _mounting_type_ is not None else 'FixedOpenRack'
    loss_fraction = _loss_fraction_ if _loss_fraction_ is not None else 0.14
    gcr = tracking_gcr_ if tracking_gcr_ is not None else 0.4

    # create the base PV properties
    pv_props = PVProperties(pv_id, eff, act_fraction, mod_type, mount_type,
                            loss_fraction, gcr)
    pv_props.display_name = pv_id

    # assign the PV properties to the Shades
    conversion = conversion_to_meters() ** 2
    total_area = 0
    for shade in shades:
        shade.properties.energy.pv_properties = pv_props
        total_area += shade.area * conversion

    # compute the rated DC size from the area and other inputs
    dc_size = int(total_area * eff * act_fraction * 1000)
    msg = 'The combined rated DC size across all input shades is {:,} W.'.format(dc_size)
    print(msg)
