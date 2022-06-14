# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Run an IDF file through EnergyPlus.

-
    Args:
        _idf: Path to an IDF file as a text string. This can also be a list of
            IDF files.
        _epw_file: Path to an .epw file as a text string.
        add_str_: THIS OPTION IS JUST FOR ADVANCED USERS OF ENERGYPLUS.
            You can input additional text strings here that you would like
            written into the IDF.  The strings input here should be complete
            EnergyPlus objects that are correctly formatted. This input can be used to
            write objects into the IDF that are not currently supported by Honeybee.
        _cpu_count_: An integer to set the number of CPUs used in the execution of each
            connected IDF file. If unspecified, it will automatically default
            to one less than the number of CPUs currently available on the
            machine (or 1 if only one processor is available).
        _run: Set to "True" to run the IDF through EnergyPlus.
            _
            This input can also be the integer "2", which will run the whole
            simulation silently (without any batch windows).

    Returns:
        report: Check here to see a report of the EnergyPlus run.
        sql: The file path of the SQL result file that has been generated on your
            machine.
        zsz: Path to a .csv file containing detailed zone load information recorded
            over the course of the design days.
        rdd: The file path of the Result Data Dictionary (.rdd) file that is
            generated after running the file through EnergyPlus.  This file
            contains all possible outputs that can be requested from the EnergyPlus
            model.  Use the Read Result Dictionary component to see what outputs
            can be requested.
        html: The HTML file path of the Summary Reports. Note that this will be None
            unless the input _sim_par_ denotes that an HTML report is requested and
            _run is set to True.
"""

ghenv.Component.Name = 'HB Run IDF'
ghenv.Component.NickName = 'RunIDF'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = '5'

import os
import shutil

try:
    from ladybug.futil import preparedir
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee_energy.run import run_idf
    from honeybee_energy.result.err import Err
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning, \
        recommended_processor_count, run_function_in_parallel
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def run_idf_and_report_errors(i):
    """Run an IDF file through EnergyPlus and report errors/warnings on this component."""
    # process the additional strings
    idf_i = idfs[i]
    if add_str_ != [] and add_str_[0] is not None:
        a_str = '/n'.join(add_str_)
        with open(idf_i, "a") as idf_file:
            idf_file.write(a_str)
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


if all_required_inputs(ghenv.Component) and _run:
    # global lists of outputs to be filled
    iter_count = len(_idf)
    sql = [None] * iter_count
    zsz = [None] * iter_count
    rdd = [None] * iter_count
    html = [None] * iter_count
    err = [None] * iter_count
    err_objs = [None] * iter_count

    # copy the IDFs into a sub-directory if they are not already labeled as in.idf
    idfs = []
    for idf_file_path in _idf:
        idf_dir, idf_file_name = os.path.split(idf_file_path)
        if idf_file_name != 'in.idf':  # copy the IDF file into a sub-directory
            sub_dir = os.path.join(idf_dir, 'run')
            target = os.path.join(sub_dir, 'in.idf')
            preparedir(sub_dir)
            shutil.copy(idf_file_path, target)
            idfs.append(target)
        else:
            idfs.append(idf_file_path)

    # run the IDF files through E+
    silent = True if _run == 2 else False
    if _cpu_count_ is not None:
        workers = _cpu_count_
    else:
        workers = recommended_processor_count() if iter_count != 1 else 1
    run_function_in_parallel(run_idf_and_report_errors, iter_count, workers)

    # print out error report if it's only one
    # otherwise it's too much data to be read-able
    if len(err_objs) == 1:
        print(err_objs[0].file_contents)
