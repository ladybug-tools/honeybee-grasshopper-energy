# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Modify a native Grasshopper Gene Pool component into a format that makes it easy
to input daily schedules into the other schedule components.
_
This essentially turns the Gene Pool into a list of 24 sliders representing an hourly
timeseries over a day. Each slider runs from the _low_bound_ to _high_bound_.
-

    Args:
        _gene_pool: The output of a native Grasshopper Gene Pool component.
        _template_: An integer for the template for which the values of the gene
            pool will be set. Default: 0. Choose one of the templates:
            -
            0 - maximum values from 9:00 to 17:00
            1 - minimum values from 9:00 to 17:00
            2 - maximum values from 7:00 to 22:00
            3 - minimum values from 7:00 to 22:00
            4 - maximum values from 0:00 to 24:00
            5 - minimum values from 0:00 to 24:00
        _low_bound_: A number for the lower boundary of the schedule values.
            Defaut: 0.
        _up_bound_: A number for the upper boundary of the schedule range.
            Default: 1.
        _decimals_: An integer greater than or equal to 0 for the number of
            decimal places to use in each slider. Default: 1.
        _run: Set to "True" to run the component and modify the connected gene pool.
            Note that you on't be able to edit a connected gene pool while this
            input is set to "True".
    
    Returns:
        report: Reports, errors, warnings, etc.
"""

ghenv.Component.Name = "HB Gene Pool to Day Schedule"
ghenv.Component.NickName = 'GenePoolToDaySch'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '2 :: Schedules'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


# template schedules
templates = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    [1] * 24,
    [0] * 24
]


if all_required_inputs(ghenv.Component) and _run:
    # set the default values
    _template_ = 0 if _template_ is None else _template_
    _low_bound_ = 0.0 if _low_bound_ is None else _low_bound_
    _up_bound_ = 1.0 if _up_bound_ is None else _up_bound_
    _decimals_ =  1 if _decimals_ is None else _decimals_

    # get the template values
    template = templates[_template_]

    # get the gene pool 
    gp = ghenv.Component.Params.Input[0].Sources[0]

    # modify the gene pool
    gp.Count = 24.0
    gp.Decimals = _decimals_
    gp.Name = "HB Day Schedule"
    gp.NickName = "DaySchedule"
    gp.Maximum = _up_bound_
    gp.Minimum = _low_bound_

    # set gene pool values
    for i in range(gp.Count):
        gp[i] = gp.Minimum + (template[i] * gp.Maximum)

    # register the change on the component
    gp.ExpireSolution(True)
else:
    print('Connect _gene_pool and a button to _run.')
