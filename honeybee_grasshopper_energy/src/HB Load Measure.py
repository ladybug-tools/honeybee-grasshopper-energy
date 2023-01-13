# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Load OpenStudio measures into Grasshopper and assign the measure's input arguments.
The resulting measure object can be plugged into the "measures_" input of the
"HB Model To OSM" component in order to be included in the export to OpenStudio.
-
Read more about OpenStudio measures and creating your own here:
http://nrel.github.io/OpenStudio-user-documentation/reference/measure_writing_guide/
-
You can also download several measures created by others from here:
https://bcl.nrel.gov/nrel/types/measure
-


    Args:
        _measure_path: Path to the folder in which the measure exists. This folder
            must contain a measure.rb and a measure.xml file. Note that connecting
            an input here will transform the component, essentially removing this
            input and changing all of the other component inputs to be input
            arguments for the measure.
    
    Returns:
        measure: A measure measure object can be plugged into the "measures_" input
            of the "HB Model To OSM" component in order to be included in the
            export to OpenStudio.
"""

ghenv.Component.Name = 'HB Load Measure'
ghenv.Component.NickName = 'LoadMeasure'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:
    from honeybee_energy.measure import Measure
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

import Grasshopper.Kernel as gh


def add_component_input_from_arg(argument):
    """Add an input parameter to this component using a MeasureArgument object.

    Args:
        argument: A honeybee-energy MeasureArgument object that will be used
            to create a new input parameter for the component.
    """
    # create the input parameter object
    param = gh.Parameters.Param_ScriptVariable()

    # assign the required properties to the input
    arg_id = '_{}'.format(argument.identifier) if argument.required else \
        '{}_'.format(argument.identifier)
    param.NickName = arg_id
    param.Name = arg_id if argument.display_name is None else argument.display_name
    param.AllowTreeAccess = False  # Measures don't support lists
    param.Access = gh.GH_ParamAccess.item  # Measures don't support lists
    param.Optional = True  # always needed so that default can come from measure file

    # assign the optional properties to the input if they exist
    if argument.type_text == 'Choice':
        descr = [argument.description] if argument.description else []
        if None not in argument.valid_choices:
            descr.append('Choose from the following options:')
            descr = descr + list(argument.valid_choices)
        param.Description = '\n '.join(descr)
    elif argument.description:
        param.Description = argument.description
    if argument.default_value is not None:
        param.AddVolatileData(gh.Data.GH_Path(0), 0, argument.default_value)
    elif argument.type_text == 'Choice' and argument.valid_choices == (None,):
        param.AddVolatileData(gh.Data.GH_Path(0), 0, 'None')

    # add the parameter to the compoent
    index = ghenv.Component.Params.Input.Count
    ghenv.Component.Params.RegisterInputParam(param, index)
    ghenv.Component.Params.OnParametersChanged()

def transform_name_and_description(measure):
    """Transform this component's name and description to match a measure.

    Args:
        measure: A honeybee-energy Measure object that will be used to assign
            this component's name and description.
    """
    # assign the measure metadata
    ghenv.Component.NickName = measure.identifier
    ghenv.Component.Name = measure.display_name if measure.display_name \
        else measure.identifier
    if measure.description:
        ghenv.Component.Description = measure.description


def transform_component(measure):
    """Transform this component to have a name and arguments that match a measure.

    Args:
        measure: A honeybee-energy Measure object that will be used to assign
            this component's name, description, and input arguments.
    """
    # assign the measure metadata
    transform_name_and_description(measure)
    # assign the input arguments
    for arg in measure.arguments:
        add_component_input_from_arg(arg)


def check_arguments_and_set_defaults(measure):
    """Check to be sure the names of component inputs align with measure arguments.

    This method will also assign any default values from the measure if there is
    no value input to the component.

    Args:
        measure: A honeybee-energy Measure object that will be used check this
            component's input arguments.
    """
    for i in range(1, ghenv.Component.Params.Input.Count):
        # get the param and the measure argument object
        param = ghenv.Component.Params.Input[i]
        arg = measure_init.arguments[i - 1]

        # check that the param matches the measure argument
        assert arg.identifier in param.NickName, \
            "This component's inputs do not match that of the input measure.\n" \
            "Grab a fresh 'HB Load Measure' component and reload the measure."

        # add any default values
        if not param.VolatileDataCount or param.VolatileData[0][0] is None:
            if arg.default_value is not None:
                param.AddVolatileData(gh.Data.GH_Path(0), 0, arg.default_value)
            elif arg.type_text == 'Choice' and arg.valid_choices == (None,):
                param.AddVolatileData(gh.Data.GH_Path(0), 0, 'None')


def update_measure_arguments(measure):
    """Update the arguments of a measure object based on this component's inputs.

    Args:
        measure: A honeybee-energy Measure object to have its arguments updated
            with the inputs to this component.
    """
    for i in range(1, ghenv.Component.Params.Input.Count):
        try:
            value = ghenv.Component.Params.Input[i].VolatileData[0][0]
            if value is not None:
                val = str(value)  # cast to string to avoid weird Grasshopper types
                argument = measure.arguments[i - 1]
                if argument.valid_choices == (None,) and val == 'None':
                    pass  # choice argument with no valid choices
                else:
                    argument.value = val if val != 'False' else False
        except Exception:  # there is no input for this value; just ignore it
            pass


def is_measure_input():
    """Check if a measure path is input to this component.

    This is needed because we don't know if there are default values for all
    required inputs until we load the measure.
    """
    if _measure_path is None:
        msg = 'Input parameter _measure_path failed to collect data!'
        print(msg)
        give_warning(ghenv.Component, msg)
        return False
    return True


if is_measure_input():
    # load the measure
    measure_init = Measure(_measure_path)

    # transform the component or check the inputs and set defaults
    if ghenv.Component.Params.Input.Count == 1:  # first time loading the measure
        transform_component(measure_init)
    else:  # the component has already been transformed
        transform_name_and_description(measure_init)
        check_arguments_and_set_defaults(measure_init)

    # if the measure has all inputs that it needs, output the measure
    if all_required_inputs(ghenv.Component):
        update_measure_arguments(measure_init)
        measure = measure_init
