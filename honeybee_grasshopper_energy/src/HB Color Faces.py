# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Visualize face and sub-face level energy simulation results as colored geometry.

-
    Args:
        _data: A list of HourlyContinuousCollections of the same data type, which
            will be used to color Faces with simulation results. Data collections
            can be of any class (eg. MonthlyCollection, DailyCollection) but they
            should all have headers with metadata dictionaries with 'Surface'
            keys. These keys will be used to match the data in the collections
            to the input faces.
        _hb_objs: An array of honeybee Rooms, Faces, Apertures or Doors to be
            colored with simulation results in the Rhino scene. This can
            also be an entire Model to be colored.
        normalize_: Boolean to note whether results should be normalized by the
            face/sub-face area if the data type of the data_colections supports it.
            If False, values will be generated using sum total of the data collection
            values. Note that this input has no effect if the data type of the
            data_collections is not normalizable since data collection values will
            always be averaged for this case. Default: True.
        sim_step_: An optional integer (greater than or equal to 0) to select
            a specific step of the data collections for which result values will be
            generated. If None, the geometry will be colored with the total of
            resutls in the data_collections if the data type is cumulative or with
            the average of results if the data type is not cumulative. Default: None.
        period_: A Ladybug analysis period to be applied to all of the input _data.
        legend_par_: An optional LegendParameter object to change the display
            of the ColorRooms.
    
    Returns:
        report: ...
        mesh: A colored mesh of the face/sub-face geometry colored using the input
            _data. Multiple meshes will be output for several data collections
            are input.
        wire_frame: A list of polylines representing the outline of the faces.
        legend: Geometry representing the legend for the colored favess.
        title: A text object for the global title.
        faces: A list of honeybee Face, Aperture and Door objects that have been
            matched to the input _data. This can be plugged into the "HB Visualize
            Quick" component to get face breps that are colored.
        colors: A list of color objects that align with the output faces. These
            can be connected to a native Grasshopper "Custom Preview" component
            in order to color room volumes with results.
        values: A list of numbers for each of the faces, which are used to generate
            the colors.
"""

ghenv.Component.Name = "HB Color Faces"
ghenv.Component.NickName = 'ColorFaces'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '6 :: Result'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:
    from honeybee.model import Model
    from honeybee.room import Room
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.result.colorobj import ColorFace
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_point3d
    from ladybug_rhino.fromgeometry import from_face3ds_to_colored_mesh, \
        from_face3d_to_wireframe
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.fromobjects import legend_objects
    from ladybug_rhino.color import color_to_color
    from ladybug_rhino.grasshopper import all_required_inputs
    from ladybug_rhino.config import units_abbreviation
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # extract any faces from input Rooms or Models
    faces = []
    for hb_obj in _hb_objs:
        if isinstance(hb_obj, Model):
            for room in hb_obj.rooms:
                faces.extend(room.faces)
        elif isinstance(hb_obj, Room):
            faces.extend(hb_obj.faces)
        else:
            faces.append(hb_obj)

    # apply analysis period to the data if connected
    if period_ is not None:
        _data = [coll.filter_by_analysis_period(period_) for coll in _data]

    # set default norm_by_floor value
    normalize_ = True if normalize_ is None else normalize_

    # create the ColorFace visualization object and output geometry
    color_obj = ColorFace(_data, faces, legend_par_, sim_step_, normalize_,
                          units_abbreviation())
    graphic = color_obj.graphic_container
    mesh = [from_face3ds_to_colored_mesh([fc], col) for fc, col in
            zip(color_obj.matched_flat_geometry, graphic.value_colors)]
    wire_frame = []
    for face in color_obj.matched_flat_faces:
        wire_frame.append(from_face3d_to_wireframe(face.geometry))
    legend = legend_objects(graphic.legend)
    title = text_objects(color_obj.title_text, graphic.lower_title_location,
                         graphic.legend_parameters.text_height,
                         graphic.legend_parameters.font)
    faces = color_obj.matched_flat_faces
    colors = [color_to_color(col, 125) for col in graphic.value_colors]
    values = graphic.values
