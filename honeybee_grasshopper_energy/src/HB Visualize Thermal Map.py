# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Spatially visualize the detailed results of a thermal mapping analysis from a
comfort matrix.

-
    Args:
        _comf_mtx: A comfort Matrix object from the "HB Read Thermal Matrix" component.
        _mesh: Mesh objects that correspond with the sensor grids of the thermal map
            analysis. These will be , with a number of faces or vertices that match
            the number of input values and will be colored with results.
        sim_step_: An optional integer (greater than or equal to 0) to select a
            specific time step of the comfort results to be displayed. Note
            that this will override any connected period.
        period_: A Ladybug analysis period to be applied to select a slice of time
            across the comfort results to be displayed.
        legend_par_: An optional LegendParameter object to change the display
            of the results.

    Returns:
        report: ...
        mesh: The input mesh objects colored with results.
        legend: Geometry representing the legend for the results.
        title: A text object for the title.
        colors: The colors associated with each input value.
        values: A list of numbers for each face of the mesh, which are used to
            generate the colors.
"""

ghenv.Component.Name = 'HB Visualize Thermal Map'
ghenv.Component.NickName = 'VizThermalMap'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '7 :: Thermal Map'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:
    from ladybug_geometry.geometry3d.mesh import Mesh3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from ladybug.graphic import GraphicContainer
    from ladybug.legend import LegendParameters
    from ladybug.color import Colorset
    from ladybug.datatype.fraction import RelativeHumidity
    from ladybug.datatype.temperature import Temperature
    from ladybug.datatype.temperaturedelta import TemperatureDelta, RadiantTemperatureDelta
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_mesh3d
    from ladybug_rhino.fromgeometry import from_mesh3d
    from ladybug_rhino.fromobjects import legend_objects
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.color import color_to_color
    from ladybug_rhino.grasshopper import all_required_inputs, de_objectify_output
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def colors_from_data_type(data_type):
    """Get the list of colors that should be used by default for a given data type.

    Args:
        data_type: A data type object that will be used to determine default colors.
    """
    if isinstance(data_type, (Temperature, RadiantTemperatureDelta, RelativeHumidity)):
        return Colorset.original()
    else:  # it is some type of thermal condition or delta temperature
        return Colorset.thermal_comfort()


if all_required_inputs(ghenv.Component):
    # load the data and perform and time-slicing operations on it
    data_mtx = de_objectify_output(_comf_mtx)
    header = data_mtx[0][0].header
    if sim_step_ is not None:
        values = [data[sim_step_] for data_list in data_mtx for data in data_list]
        time_text = data_mtx[0][0].datetimes[sim_step_]
    elif period_ is not None:
        new_data = [[data.filter_by_analysis_period(period_) for data in data_list]
                     for data_list in data_mtx]
        values = [data.average for data_list in new_data for data in data_list]
        time_text = period_
    else:
        values = [data.average for data_list in data_mtx for data in data_list]
        time_text = header.analysis_period

    # generate Ladybug objects for the graphic
    lb_meshes = [to_mesh3d(mesh) for mesh in _mesh]
    lb_mesh = Mesh3D.join_meshes(lb_meshes)
    graphic = GraphicContainer(
        values, lb_mesh.min, lb_mesh.max, legend_par_,
        data_type=header.data_type, unit=header.unit
    )

    # set titles and set default colors and color ranges
    if graphic.legend_parameters.are_colors_default:
        graphic.legend_parameters.colors = colors_from_data_type(header.data_type)
    if isinstance(header.data_type, TemperatureDelta) and not \
            isinstance(header.data_type, RadiantTemperatureDelta) and \
            graphic.legend.is_min_default and graphic.legend.is_max_default:
        graphic.legend_parameters.min = -5
        graphic.legend_parameters.max = 5
    graphic.legend_parameters.title = header.unit
    global_title = '{}\n{}'.format(header.data_type.name, time_text)
    title = text_objects(global_title, graphic.lower_title_location,
                         graphic.legend_parameters.text_height * 1.5,
                         graphic.legend_parameters.font)

    # draw rhino objects
    lb_mesh.colors = graphic.value_colors
    mesh = from_mesh3d(lb_mesh)
    legend = legend_objects(graphic.legend)
    colors = [color_to_color(col) for col in lb_mesh.colors]
