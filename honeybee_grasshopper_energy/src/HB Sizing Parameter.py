# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create parameters with criteria for sizing the heating and cooling system.
-

    Args:
        ddy_file_: An optional path to a .ddy file on your system, which contains
            information about the design days used to size the hvac system. If None,
            honeybee will look for a .ddy file next to the .epw and extract all
            99.6% and 0.4% design days.
        filter_ddays_: Boolean to note whether the design days in the ddy_file_
            should be filtered to only include 99.6% and 0.4% design days. If None
            or False, all design days in the ddy_file_ will be incorporated into
            the sizing parameters. This can also be the integer 2 to filter for
            99.0% and 1.0% design days.
        _heating_fac_: A number that will get multiplied by the peak heating load
            for each zone in the model in order to size the heating system for
            the model. Must be greater than 0. (Default: 1.25).
        _cooling_fac_: A number that will get multiplied by the peak cooling load
            for each zone in the model in order to size the cooling system for
            the model. Must be greater than 0. (Default: 1.15).
        eff_standard_: Text to specify the efficiency standard, which will automatically
            set the efficiencies of all HVAC equipment when provided. Note that
            providing a standard here will cause the OpenStudio translation
            process to perform an additional sizing calculation with EnergyPlus,
            which is needed since the default efficiencies of equipment vary
            dependingon their size. THIS WILL SIGNIFICANTLY INCREASE
            TRANSLATION TIME TO OPENSTUDIO. However, it is often
            worthwhile when the goal is to match the HVAC specification with a
             particular standard. The "HB Building Vintages" component has a full
            list of supported HVAC efficiency standards. You can also choose
            from the following.
                * DOE_Ref_Pre_1980
                * DOE_Ref_1980_2004
                * ASHRAE_2004
                * ASHRAE_2007
                * ASHRAE_2010
                * ASHRAE_2013
                * ASHRAE_2016
                * ASHRAE_2019
        climate_zone: Text indicating the ASHRAE climate zone to be used with the
            efficiency_standard. When unspecified, the climate zone will be
            inferred from the design days. This input can be a single
            integer (in which case it is interpreted as A) or it can include the
            A, B, or C qualifier (eg. 3C). Typically, the "LB Import STAT"
            component can yield the climate zone for a particular location.
        building_type: Text for the building type to be used in the efficiency_standard.
            If the type is not recognized or is None, it will be assumed that the
            building is a generic NonResidential. The following have meaning
            for the standard.
                * NonResidential
                * Residential
                * MidriseApartment
                * HighriseApartment
                * LargeOffice
                * MediumOffice
                * SmallOffice
                * Retail
                * StripMall
                * PrimarySchool
                * SecondarySchool
                * SmallHotel
                * LargeHotel
                * Hospital
                * Outpatient
                * Warehouse
                * SuperMarket
                * FullServiceRestaurant
                * QuickServiceRestaurant
                * Laboratory
                * Courthouse

    Returns:
        sizing: Parameters with criteria for sizing the heating and cooling system.
            These can be connected to the "HB Simulation Parameter" component in
            order to specify settings for the EnergyPlus simulation.
"""

ghenv.Component.Name = 'HB Sizing Parameter'
ghenv.Component.NickName = 'SizingPar'
ghenv.Component.Message = '1.6.1'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from honeybee_energy.simulation.sizing import SizingParameter
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

# dictionary to get correct efficiency standards
EFF_STANDARDS = {
    'DOE_Ref_Pre_1980': 'DOE_Ref_Pre_1980',
    'DOE_Ref_1980_2004': 'DOE_Ref_1980_2004',
    'ASHRAE_2004': 'ASHRAE_2004',
    'ASHRAE_2007': 'ASHRAE_2007',
    'ASHRAE_2010': 'ASHRAE_2010',
    'ASHRAE_2013': 'ASHRAE_2013',
    'ASHRAE_2016': 'ASHRAE_2016',
    'ASHRAE_2019': 'ASHRAE_2019',
    'pre_1980': 'DOE_Ref_Pre_1980',
    '1980_2004': 'DOE_Ref_1980_2004',
    '2004': 'ASHRAE_2004',
    '2007': 'ASHRAE_2007',
    '2010': 'ASHRAE_2010',
    '2013': 'ASHRAE_2013',
    '2016': 'ASHRAE_2016',
    '2019': 'ASHRAE_2019'
}

# set default sizing factors
heating_fac = 1.25 if _heating_fac_ is None else _heating_fac_
cooling_fac = 1.15 if _cooling_fac_ is None else _cooling_fac_

# create the object
sizing = SizingParameter(None, heating_fac, cooling_fac)

# apply design days from ddy
if ddy_file_ is not None:
    if filter_ddays_ == 1:
        sizing.add_from_ddy_996_004(ddy_file_)
    elif filter_ddays_ == 2:
        sizing.add_from_ddy_990_010(ddy_file_)
    else:
        sizing.add_from_ddy(ddy_file_)

# set the efficiency standard if provided
if eff_standard_ is not None:
    sizing.efficiency_standard = EFF_STANDARDS[eff_standard_]
if climate_zone_ is not None:
    sizing.climate_zone = climate_zone_
if bldg_type_ is not None:
    sizing.building_type = bldg_type_
