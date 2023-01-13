# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Set up a Honeybee Model to use the EnergyPlus Airflow Network (AFN) for all airflow
in the energy simulation.
_
Compared to the default single-zone methods that Honeybee uses for infiltration
and ventilation, the AFN represents air flow in a manner that is truer to the fluid
dynamic behavior of real buildings. In particular, the AFN more accurately models
the flow of air from one zone to another, accounting for the pressure changes
induced by wind and air density differences. However, using the AFN means that
the simulation will take considerably longer to run compared to the single zone
option and the difference in simuation resuts is only likely to be significant
when the Model contains operable windows or the building is extremely leaky.
_
Passing a Honeybee Model through this component before energy simulation will
result in the following changes to the EnergyPlus IDF:
_
1. All ZoneInfiltration objects will be excluded and, instead, infitration will
be modeled with AFN Crack objects assigned to each opaque Face.
_
2. For all AirBoundary Faces within the Model, ZoneMixing objects will be excluded
and, instead, the air boundary will be modeled with AFN Crack objects that have
very large pressure coefficients derived from the orifice equation and the area
of the air wall.
_
3. For all operable Apertures, ZoneVentilation:WindandStackOpenArea objects will
be excluded and, instead, these opearable apertures will be modeled with AFN
SimpleOpening objects.
_
4. For each Room with a VentilationControl object to specify setpoints at which
the windows open, an Energy Management System (EMS) program will be written to
dictate when the operable Apertures of the Room open.
-

    Args:
        _model: A Honeybee Model for which the Airflow network will be set up.
            This Model should have everything assigned to it that is needed
            for simulation, including solved adjacencies and relevant window-
            opening properties.
        leakage_template_: Text identifying the leakiness of the Model, which is used
            to generate AFNCrack objects that represent infiltration for
            each of the Model's surfaces (Face, Aperture, and Door).
            _
            Choose from the following.
            * Excellent
            * Medium
            * VeryPoor
            _
            These three text values correspond to DesignBuilder's Cracks
            Templates, which provide typical crack flow coefficients and
            exponents for different envelope tightness classifications.
            _
            If None, the exterior airflow leakage parameters will be derived
            from the room infiltration rate specified in the room's energy
            properties, which are in units of m3/s per m2 of facade. This
            derivation from the Room's infiltration will compute air leakage
            parameters for exterior cracks that produce a total air flow rate
            equivalent to the room's infiltration rate at an envelope pressure
            difference of 4 Pa. This default derivation is not as complete of a
            representation of building ariflow dynamics as the DesignBuilder
            Crack Templates are. However, since the airflow leakae parameters are
            derived from values in m3/s-m2 of infiltration, they are easier to
            relate to the results of infiltration blower-door tests, which
            typically express infiltration rates in these units.
        _delta_pressure_: The air pressure difference across the building envelope in
            Pascals, which is used to calculate infiltration crack flow
            coefficients when no leakage tempate is specified. The resulting
            average simulated air pressure difference will roughly equal this
            delta pressure times the nth root of the ratio between the simulated
            and target room infiltration rates. (Default: 4).
        _ref_pressure_: The reference barometric pressure measurement in Pascals
            under which the surface crack data were obtained. (Default: 101325).
        _high_rise_: Booling indicating whether the Model is LowRise or HighRise.
            This parameter is used to estimate building-wide wind pressure
            coefficients for the AFN by approximating the building geometry
            as an extruded rectangle. LowRise corresponds to a building where
            the height is less then three times the width AND length of the
            footprint. HighRise corresponds to a building where height is more
            than three times the width OR length of the footprint. If None,
            this property will be auto-calculated from Room geometry of the
            Model. This default assumption may not be appropriate if the Model
            represents only a portion of a larger Building.
        _long_axis_: A number between 0 and 180 for the clockwise angle difference
            in degrees that the long axis of the building is from true North.
            This parameter is used to estimate building-wide wind pressure
            coefficients for the AFN by approximating the building geometry
            as an extruded rectangle. 0 indicates a North-South long axis while
            90 indicates an East-West long axis. If None, this property will be
            auto-calculated from Room geometry of the Model (either 0 or 90).
            This default assumption may not be appropriate if the Model
            represents only a portion of a larger Building.
        _aspect_ratio_: A number between 0 and 1 for the aspect ratio of the building's
            footprint, defined as the ratio of length of the short axis divided
            by the length of the long axis. This parameter is used to estimate
            building-wide wind pressure coefficients for the AFN by approximating
            the building geometry as an extruded rectangle If None, this
            property will be auto-calculated from Room geometry of the Model
            and the _long_axis_ above. This default assumption may not be
            appropriate if the Model represents only a portion of a larger
            building.

    Returns:
        model: The input Honeybee Model for which the Airflow network has
            been set up.
"""

ghenv.Component.Name = 'HB Airflow Newtwork'
ghenv.Component.NickName = 'AFN'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '3 :: Loads'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

import math
try:
    from ladybug_geometry.geometry3d.pointvector import Vector3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from honeybee_energy.ventcool.afn import generate
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

leakage_tempaltes = {
    'excellent': 'Excellent',
    'medium': 'Medium',
    'verypoor': 'VeryPoor'
}


if all_required_inputs(ghenv.Component):
    # duplicate the input Model to avoid editing it
    model = _model.duplicate()

    # set default properties for the leakage if they are not input
    try:
        leakage = leakage_tempaltes[leakage_template_.lower()] \
            if leakage_template_ is not None else 'Medium'
    except KeyError:
        raise TypeError('leakage_template_ "{}" is not recognized. Choose from: '
                        'Excellent, Medium VeryPoor'.format(leakage_template_))
    use_room_infiltration = True if leakage_template_ is None else False
    pressure = _ref_pressure_ if _ref_pressure_ is not None else 101325
    delta_pressure = _delta_pressure_ if _delta_pressure_ is not None else 4

    # check for operable exterior apertures that are horizontal as E+ cannot simulate these
    up_vec, horiz_aps = Vector3D(0, 0, 1), []
    for ap in model.apertures:
        if ap.is_operable:
            ang = math.degrees(ap.normal.angle(up_vec))
            if ang < 10 or ang > 170:
                ap.is_operable = False
                horiz_aps.append(ap.identifier)
    if len(horiz_aps) != 0:
        msg = 'The following exterior operable apertures are within 10 degrees of ' \
            'being horizontal.\nThese cannot be simulated in EnergyPlus and so they ' \
            'have been set to be inoperable:\n{}'.format('\n'.join(horiz_aps))
        print(msg)
        give_warning(ghenv.Component, msg)

    # generate the AFN leakage for all of the surfaces of the Model
    generate(model.rooms, leakage, use_room_infiltration, pressure, delta_pressure)

    # set up the Model-wide VentilationSimulationParameters for the AFN
    vent_sim_par = model.properties.energy.ventilation_simulation_control
    vent_sim_par.vent_control_type = 'MultiZoneWithoutDistribution'
    if _long_axis_ is not None:  # assing this first so it's in the autocalculation
        vent_sim_par.long_axis_angle = _long_axis_
    model.properties.energy.autocalculate_ventilation_simulation_control()

    # set the properties used to approximate wind pressure coefficients
    if _high_rise_ is not None:
        vent_sim_par.building_type = 'HighRise' if _high_rise_ else 'LowRise'
    if _aspect_ratio_ is not None:
        vent_sim_par.aspect_ratio = _aspect_ratio_
        vent_sim_par.long_axis_angle = _long_axis_
    report = model.properties.energy.ventilation_simulation_control
