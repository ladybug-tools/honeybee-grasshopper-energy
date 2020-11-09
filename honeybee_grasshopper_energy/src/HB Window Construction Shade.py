# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create an EnergyPlus window construction that includes shades/blinds or a dynamically-
controlled glass pane.
_
The result can be assigned to any Aperture or ConstructionSet just like any other
WindowConstruction.
-

    Args:
        _name: Text to set the name for the Construction and to be incorporated
            into a unique Construction identifier.
        _win_constr: A WindowConstruction object that serves as the "switched off"
            version of the construction (aka. the "bare construction"). The
            shade material and shade location will be used to modify this
            starting construction. This can also be text for a construction
            identifier to be looked up in the window construction library.
        _shd_material: An Shade Material or an Blind Material that serves as the
            shading layer for this construction. This can also be a Glass Material,
            which will indicate that the WindowConstruction has a dynamically-
            controlled glass pane like an electrochromic window assembly. This
            can also be text for a material identifier to be looked up in the
            window material library.
        _shd_location_: Text to indicate where in the window assembly the shade material
            is located. (Default: "Interior"). Choose from the following 3 options:
            * Interior
            * Between
            * Exterior
            Note that the WindowConstruction must have at least one gas gap to use
            the "Between" option. Also note that, for a WindowConstruction with more
            than one gas gap, the "Between" option defalts to using the inner gap
            as this is the only option that EnergyPlus supports.
        _control_type_: An integer or text to indicate how the shading device is controlled,
            which determines when the shading is “on” or “off.” (Default: "AlwaysOn").
             Choose from the options below (units for the values of the corresponding
             setpoint are noted in parentheses next to each option):
             0 = AlwaysOn
             1 = OnIfHighSolarOnWindow (W/m2)
             2 = OnIfHighHorizontalSolar (W/m2)
             3 = OnIfHighOutdoorAirTemperature (C)
             4 = OnIfHighZoneAirTemperature (C)
             5 = OnIfHighZoneCooling (W)
             6 = OnNightIfLowOutdoorTempAndOffDay (C)
             7 = OnNightIfLowInsideTempAndOffDay (C)
             8 = OnNightIfHeatingAndOffDay (W)
        setpoint_: A number that corresponds to the specified control_type. This can
            be a value in (W/m2), (C) or (W) depending upon the control type.
        schedule_: An optional ScheduleRuleset or ScheduleFixedInterval to be applied
            on top of the control type. If None, the control type will govern all
            behavior of the construction.
    
    Returns:
        constr: A shaded window construction that can be assigned to Honeybee
            Apertures or ConstructionSets.
"""

ghenv.Component.Name = 'HB Window Construction Shade'
ghenv.Component.NickName = 'WindowConstrShd'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = "1 :: Constructions"
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:  # import the core honeybee dependencies
    from honeybee.typing import clean_and_id_ep_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.construction.windowshade import WindowConstructionShade
    from honeybee_energy.lib.constructions import window_construction_by_identifier
    from honeybee_energy.lib.materials import window_material_by_identifier
    from honeybee_energy.lib.schedules import schedule_by_identifier
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


# dictionary to convert to acceptable control types
CONTROL_TYPES = {
    '0': 'AlwaysOn',
    '1': 'OnIfHighSolarOnWindow',
    '2': 'OnIfHighHorizontalSolar',
    '3': 'OnIfHighOutdoorAirTemperature',
    '4': 'OnIfHighZoneAirTemperature',
    '5': 'OnIfHighZoneCooling',
    '6': 'OnNightIfLowOutdoorTempAndOffDay',
    '7': 'OnNightIfLowInsideTempAndOffDay',
    '8': 'OnNightIfHeatingAndOffDay',
    'AlwaysOn': 'AlwaysOn',
    'OnIfHighSolarOnWindow': 'OnIfHighSolarOnWindow',
    'OnIfHighHorizontalSolar': 'OnIfHighHorizontalSolar',
    'OnIfHighOutdoorAirTemperature': 'OnIfHighOutdoorAirTemperature',
    'OnIfHighZoneAirTemperature': 'OnIfHighZoneAirTemperature',
    'OnIfHighZoneCooling': 'OnIfHighZoneCooling',
    'OnNightIfLowOutdoorTempAndOffDay': 'OnNightIfLowOutdoorTempAndOffDay',
    'OnNightIfLowInsideTempAndOffDay': 'OnNightIfLowInsideTempAndOffDay',
    'OnNightIfHeatingAndOffDay': 'OnNightIfHeatingAndOffDay'
    }


if all_required_inputs(ghenv.Component):
    # set default values
    constr_id = clean_and_id_ep_string(_name)
    _shd_location_ = 'Interior' if _shd_location_ is None else _shd_location_.title()
    _control_type_ = 'AlwaysOn' if _control_type_ is None \
        else CONTROL_TYPES[_control_type_]

    # get objects from the library if they are strings
    if isinstance(_win_constr, str):
        win_con = window_construction_by_identifier(_win_constr)
        # duplicate and rename to avoid having the same construction name in one model
        _win_constr = win_con.duplicate()
        _win_constr.identifier = '{}_Unshaded'.format(constr_id)
    if isinstance(_shd_material, str):
        _shd_material = window_material_by_identifier(_shd_material)
    if isinstance(schedule_, str):
        schedule_ = schedule_by_identifier(schedule_)

    # create the construction object
    constr = WindowConstructionShade(
        constr_id, _win_constr, _shd_material, _shd_location_, _control_type_,
        setpoint_, schedule_)
    constr.display_name = _name
