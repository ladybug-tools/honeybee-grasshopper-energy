# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Translate a fully-simualte-able OpenStudio model (.osm) to an IDF and run the it
through EnergyPlus.

-
    Args:
        _osm: Path to an OpenStudio Model (OSM) file as a text string. This can
            also be a list of OSM files.
        _epw_file: Path to an .epw file as a text string.
        add_str_: THIS OPTION IS JUST FOR ADVANCED USERS OF ENERGYPLUS.
            You can input additional text strings here that you would like
            written into the IDF.  The strings input here should be complete
            EnergyPlus objects that are correctly formatted. This input can be used to
            write objects into the IDF that are not currently supported by Honeybee.
        parallel_: Set to "True" to run execute simulations of multiple IDF files
            in parallel, which can greatly increase the speed of calculation but
            may not be desired when other processes are running. If False, all
            EnergyPlus simulations will be be run on a single core. Default: False.
        _translate: Set to "True" to translate the OSM files to IDFs using the
            OpenStudio command line interface (CLI).
        run_: Set to "True" to run the resulting IDF through EnergyPlus.
            _
            This input can also be the integer "2", which will run the whole
            translation and simulation silently (without any batch windows).

    Returns:
        report: Check here to see a report of the EnergyPlus run.
        idf: The file path of the IDF file that has been generated on this computer.
        sql: The file path of the SQL result file that has been generated on your
            machine. This will be None unless run_ is set to True.
        zsz: Path to a .csv file containing detailed zone load information recorded
            over the course of the design days. This will be None unless run_ is
            set to True.
        rdd: The file path of the Result Data Dictionary (.rdd) file that is
            generated after running the file through EnergyPlus.  This file
            contains all possible outputs that can be requested from the EnergyPlus
            model.  Use the Read Result Dictionary component to see what outputs
            can be requested.
        html: The HTML file path of the Summary Reports. Note that this will be None
            unless the input _sim_par_ denotes that an HTML report is requested and
            run_ is set to True.
"""

ghenv.Component.Name = 'HB Run OSM'
ghenv.Component.NickName = 'RunOSM'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = '5'

import json
import os
import System.Threading.Tasks as tasks

try:
    from honeybee_energy.run import run_osw, run_idf
    from honeybee_energy.result.err import Err
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

def run_osm_and_report_errors(i):
    """Run an OSW through OpenStudio CLI."""
    # create a blank osw for the translation
    osw_dict = {
        'seed_file': _osm[i],
        'weather_file': _epw_file
        }
    osw_directory = os.path.dirname(_osm[i])
    osw = os.path.join(osw_directory, 'workflow.osw')
    with open(osw, 'w') as fp:
        json.dump(osw_dict, fp, indent=4)

    osm_i, idf_i = run_osw(osw, silent=silent)
    # process the additional strings
    if add_str_ != [] and add_str_[0] is not None and idf is not None:
        add_str = '/n'.join(add_str_)
        with open(idf, "a") as idf_file:
            idf_file.write(add_str)
    osm.append(osm_i)
    idf.append(idf_i)

    # run the IDF through EnergyPlus
    if run_:
        sql_i, zsz_i, rdd_i, html_i, err_i = run_idf(idf_i, _epw_file, silent=silent)

        # report any errors on this component
        if err_i is not None:
            err_obj = Err(err_i)
            err_objs.append(err_obj)
            for warn in err_obj.severe_errors:
                give_warning(ghenv.Component, warn)
            for error in err_obj.fatal_errors:
                print err_obj.file_contents  # print before raising the error
                raise Exception(error)

        # append everything to the global lists
        sql.append(sql_i)
        zsz.append(zsz_i)
        rdd.append(rdd_i)
        html.append(html_i)
        err.append(err_i)


if all_required_inputs(ghenv.Component) and _translate:
    # global lists of outputs to be filled
    osm, idf, sql, zsz, rdd, html, err, err_objs = [], [], [], [], [], [], [], []

    # run the OSW files through OpenStudio CLI
    silent = True if run_ == 2 else False
    if parallel_:
        tasks.Parallel.ForEach(range(len(_osm)), run_osm_and_report_errors)
    else:
        for i in range(len(_osm)):
            run_osm_and_report_errors(i)

    # print out error report if it's only one file
    # otherwise it's too much data to be read-able
    if len(err_objs) == 1:
        print(err_objs[0].file_contents)
