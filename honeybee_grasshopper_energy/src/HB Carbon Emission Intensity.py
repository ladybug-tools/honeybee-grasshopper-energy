# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Get information about carbon emission intensity (CEI) from an EnergyPlus SQL file.
_
The location and year (or input emissions of electricity intensity) will be used
to compute carbon intensity for both electricity and district heating/cooling.
Fixed numbers will be used to convert the following on-site fuel sources:
_
* Natural Gas --  277.358 kg/MWh
* Propane -- 323.897 kg/MWh
* Fuel Oil -- 294.962 kg/MWh
-

    Args:
        _sql: The file path of the SQL result file that has been generated from
            an energy simulation. This can also be a list of EnergyPlus files
            in which case EUI will be computed across all files. Lastly, it can
            be a directory or list of directories containing results, in which
            case, EUI will be calculated form all files ending in .sql.
        _loc_kgMWh: A ladybug Location object in the USA, which will be used to determine the
            subregion of the electrical grid. Alternatively, it can be A number
            for the electric grid carbon emissions in kg CO2/MWh. The following
            rules of thumb may be used as a guide:
            _
            * 800 kg/MWh - an inefficient coal or oil-dominated grid (West Virgina in 2020)
            * 400 kg/MWh - the average US (energy mixed) grid around 2020
            * 200-400 kg/MWh - for grids in transition to renewables
            * 100-200 kg/MWh - for grids with majority renewable/nuclear composition
            * 0-100 kg/MWh - for grids with renewables and storage
        _year_: An integer for the future year for which carbon emissions will
            be estimated. Values must be an even number and be between 2020
            and 2050. (Default: 2030).

    Returns:
        cei: A number for the total annual carbon emission intensity (CEI). This is
            the sum of all operational carbon emissions divided by the gross
            floor area (including both conditioned and unconditioned spaces).
            Units are kg CO2/m2.
        cei_end_use: The carbon emission intensity broken down by each end use. These
            values coorespond to the end_uses output below. Values are in kg CO2/m2 .
        end_uses: A list of text for each of the end uses in the simulation (Heating,
            Cooling, etc.). Thes outputs coorespond to the eui_end_use
            output above.
        gross_floor: The total gross floor area of the energy model. This can be used
            to compute the total energy use from the intensity values above or
            it can be used to help with other result post-processing. The value
            will be in m2 if ip_ is False or None and ft2 if True.
"""

ghenv.Component.Name = 'HB Carbon Emission Intensity'
ghenv.Component.NickName = 'CEI'
ghenv.Component.Message = '1.6.1'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '6 :: Result'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

import os
import subprocess
import json

try:
    from ladybug.location import Location
except ImportError as e:
    raise ImportError('\nFailed to import location:\n\t{}'.format(e))

try:
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.result.emissions import future_electricity_emissions, \
        emissions_from_sql
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


# Use the SQLiteResult class to parse the result files directly on Windows.
def get_results_windows(sql_files, elec_emiss):
    results = emissions_from_sql(sql_files, elec_emiss)
    return results['carbon_intensity'], results['total_floor_area'], \
        results['end_uses'], results['sources']


# The SQLite3 module doesn't work in IronPython on Mac, so we must make a call
# to the Honeybee CLI (which runs on CPython) to get the results.
def get_results_mac(sql_files, elec_emiss):
    from collections import OrderedDict
    cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'result',
            'carbon-emission-intensity']
    cmds.extend(sql_files)
    cmds.extend(['--electricity-emissions', str(elec_emiss)])
    process = subprocess.Popen(cmds, stdout=subprocess.PIPE)
    stdout = process.communicate()
    results = json.loads(stdout[0], object_pairs_hook=OrderedDict)
    return results['carbon_intensity'], results['total_floor_area'], \
        results['end_uses'], results['sources']


if all_required_inputs(ghenv.Component):
    # ensure that _sql is a list rather than a single string
    if isinstance(_sql, basestring):
        _sql = [_sql]

    # process the location and year or the electricity intensity
    if isinstance(_loc_kgMWh, Location):
        yr = 2030 if _year_ is None else int(_year_)
        elec_emiss = future_electricity_emissions(_loc_kgMWh, yr)
        if elec_emiss is None:
            msg = 'Location must be inside the USA in order to be used for carbon ' \
                'emissions estimation.\nPlug in a number for carbon intensity in ' \
                'kg CO2/MWH for locations outside the USA.'
            print(msg)
            raise ValueError(msg)
    else:
        try:
            elec_emiss = float(_loc_kgMWh)
        except TypeError:
            msg = 'Expected location object or number for _loccation. ' \
                'Got {}.'.format(type(_loc_kgMWh))
            raise ValueError(msg)

    # get the results
    get_results = get_results_windows if os.name == 'nt' else get_results_mac
    cei, gross_floor, end_use_pairs, sources = get_results(_sql, elec_emiss)

    # create separate lists for end use values and labels
    cei_end_use = end_use_pairs.values()
    end_uses = [use.replace('_', ' ').title() for use in end_use_pairs.keys()]

    # give a warning if the sources include district heating or cooling
    if 'district_heat' in sources:
        msg = 'District heating was found in the results and so carbon emissions ' \
            'cannot be accurately estimated.\nTry using a different HVAC or SHW system.'
        print(msg)
        give_warning(ghenv.Component, msg)
    if 'district_cool' in sources:
        msg = 'District cooling was found in the results and so carbon emissions ' \
            'cannot be accurately estimated.\nTry using a different HVAC system.'
        print(msg)
        give_warning(ghenv.Component, msg)
