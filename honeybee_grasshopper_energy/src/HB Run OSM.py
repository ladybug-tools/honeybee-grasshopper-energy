# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

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
        _cpu_count_: An integer to set the number of CPUs used in the execution of each
            connected OSM file. If unspecified, it will automatically default
            to one less than the number of CPUs currently available on the
            machine (or 1 if only one processor is available).
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
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = '5'

import os
import json

try:
    from honeybee_energy.run import run_osw, run_idf
    from honeybee_energy.result.err import Err
    from honeybee_energy.result.osw import OSW
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning, \
        recommended_processor_count, run_function_in_parallel
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
    sch_directory1 = os.path.join(os.path.dirname(osw_directory), 'schedules')
    sch_directory2 = os.path.join(osw_directory, 'schedules')
    if os.path.isdir(sch_directory1):
        osw_dict['file_paths'] = [sch_directory1]
    elif os.path.isdir(sch_directory2):
        osw_dict['file_paths'] = [sch_directory2]
    osw = os.path.join(osw_directory, 'workflow.osw')
    with open(osw, 'w') as fp:
        json.dump(osw_dict, fp, indent=4)

    # get an IDF from the OSM using the OpenStudio CLI
    osm_i, idf_i = run_osw(osw, silent=silent)
    if idf_i is None:
        log_osw = OSW(os.path.join(osw_directory, 'out.osw'))
        errors = []
        print(log_osw.stdout)
        for error, tb in zip(log_osw.errors, log_osw.error_tracebacks):
            print(tb)
            errors.append(error)
        raise Exception('Failed to run OpenStudio CLI:\n{}'.format('\n'.join(errors)))

    # process the additional strings
    if add_str_ != [] and add_str_[0] is not None and idf is not None:
        a_str = '/n'.join(add_str_)
        with open(idf_i, "a") as idf_file:
            idf_file.write(a_str)
    osm[i] = osm_i
    idf[i] = idf_i

    # run the IDF through EnergyPlus
    if run_:
        sql_i, zsz_i, rdd_i, html_i, err_i = run_idf(idf_i, _epw_file, silent=silent)

        # report any errors on this component
        if err_i is not None:
            err_obj = Err(err_i)
            err_objs[i] = err_obj
            for warn in err_obj.severe_errors:
                give_warning(ghenv.Component, warn)
            for error in err_obj.fatal_errors:
                print err_obj.file_contents  # print before raising the error
                raise Exception(error)

        # append everything to the global lists
        sql[i] = sql_i
        zsz[i] = zsz_i
        rdd[i] = rdd_i
        html[i] = html_i
        err[i] = err_i


if all_required_inputs(ghenv.Component) and _translate:
    # global lists of outputs to be filled
    iter_count = len(_osm)
    osm = [None] * iter_count
    idf = [None] * iter_count
    sql = [None] * iter_count
    zsz = [None] * iter_count
    rdd = [None] * iter_count
    html = [None] * iter_count
    err = [None] * iter_count
    err_objs = [None] * iter_count

    # run the OSW files through OpenStudio CLI
    silent = True if run_ == 2 else False
    if _cpu_count_ is not None:
        workers = _cpu_count_
    else:
        workers = recommended_processor_count() if iter_count != 1 else 1
    run_function_in_parallel(run_osm_and_report_errors, iter_count, workers)

    # print out error report if it's only one file
    # otherwise it's too much data to be read-able
    if len(err_objs) == 1 and err_objs[0] is not None:
        print(err_objs[0].file_contents)
