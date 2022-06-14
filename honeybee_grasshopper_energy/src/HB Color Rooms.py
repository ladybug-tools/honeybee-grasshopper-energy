# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Visualize Room-level energy simulation results as colored Room geometry.

-
    Args:
        _data: A list of data collections of the same data type, which will be
            used to color Rooms. Data collections can be of any class
            (eg. MonthlyCollection, DailyCollection) but they should originate
            from an energy simulation sql (with header metadata that has 'Zone'
            or, in some cases, 'System' keys). These keys will be used to
            match the data in the collections to the input rooms.
        _rooms_model: An array of honeybee Rooms or honeybee Models, which will
            be matched to the data_collections. The length of these Rooms does
            not have to match the data_collections and this object will only
            create visualizations for rooms that are found to be matching.
        norm_by_flr_: Boolean to note whether results should be normalized
            by the floor area of the Room if the data type of the data_colections
            supports it. If False, values will be generated using sum total of
            the data collection values. Note that this input has no effect if
            the data type of the data_collections is not cumulative since data
            collection values will always be averaged for this case. Default: True.
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
        mesh: A colored mesh of the Room floor geometry colored using the input
            _data. Multiple meshes will be output for several data collections
            are input.
        wire_frame: A list of polylines representing the outline of the
            room volumes.
        legend: Geometry representing the legend for the colored rooms.
        title: A text object for the global title.
        rooms: A list of honeybee Room objects that have been successfully matched
            to the input _data. This can be plugged into the "HB Visualize
            Quick" component to get full room volumes that are colored.
        colors: A list of color objects that align with the output rooms. These
            can be connected to a native Grasshopper "Custom Preview" component
            in order to color room volumes with results.
        values: A list of numbers for each of the rooms, which are used to
            generate the colors.
"""

ghenv.Component.Name = "HB Color Rooms"
ghenv.Component.NickName = 'ColorRooms'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '6 :: Result'
ghenv.Component.AdditionalHelpFromDocStrings = '2'


try:
    from honeybee.model import Model
    from honeybee.room import Room
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.result.colorobj import ColorRoom
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_point3d
    from ladybug_rhino.fromgeometry import from_face3ds_to_colored_mesh, \
        from_polyface3d_to_wireframe
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.fromobjects import legend_objects
    from ladybug_rhino.color import color_to_color
    from ladybug_rhino.grasshopper import all_required_inputs
    from ladybug_rhino.config import units_abbreviation
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def split_solar_enclosure_data(data_to_split, rooms):
    """Split solar enclosure data according to exterior aperture area."""
    # figure out the ratios of exterior aperture area in each room
    enclosures = Room.group_by_air_boundary_adjacency(rooms)
    encl_ratios = {}
    for encl in enclosures:
        if len(encl) != 1:
            ap_areas = [rm.exterior_aperture_area for rm in encl]
            total_a = sum(ap_areas)
            if total_a != 0:
                rat_dict = {rm.identifier: ap / total_a
                            for rm, ap in zip(encl, ap_areas)}
            else:
                rat_dict = {rm.identifier: 0 for rm in encl}
            encl_ratios[encl[0].identifier] = rat_dict
    encl_ratios = [x for _, x in sorted(zip(encl_ratios.keys(), encl_ratios.values()))]

    # create the list of split data collections
    split_data, enc_count = [], 0
    for dat in data_to_split:
        if 'Solar Enclosure' in dat.header.metadata['Zone']:
            rm_ratios = encl_ratios[enc_count]
            for rm_id, rm_rat in rm_ratios.items():
                new_data = dat.duplicate()
                new_data.header.metadata['Zone'] = rm_id.upper()
                new_data.values = [val * rm_rat for val in dat.values]
                split_data.append(new_data)
            enc_count += 1
        else:
            split_data.append(dat)
    return split_data


if all_required_inputs(ghenv.Component):
    # extract any rooms from input Models
    rooms = []
    for hb_obj in _rooms_model:
        if isinstance(hb_obj, Model):
            rooms.extend(hb_obj.rooms)
        else:
            rooms.append(hb_obj)

    # apply analysis period to the data if connected
    if period_ is not None:
        _data = [coll.filter_by_analysis_period(period_) for coll in _data]

    # set default norm_by_floor value
    norm_by_flr_ = True if norm_by_flr_ is None else norm_by_flr_

    # sense if the conneccted data is for a solar enclosure and split the data if so
    zone_solar = 'Zone Windows Total Transmitted Solar Radiation Energy'
    if isinstance(_rooms_model[0], Model) and 'type' in _data[0].header.metadata and \
            _data[0].header.metadata['type'] == zone_solar:
        _data = split_solar_enclosure_data(_data, rooms)

    # create the ColorRoom visualization object and output geometry
    color_obj = ColorRoom(_data, rooms, legend_par_, sim_step_, norm_by_flr_,
                          units_abbreviation())
    graphic = color_obj.graphic_container
    mesh = [from_face3ds_to_colored_mesh(flrs, col) for flrs, col in
            zip(color_obj.matched_floor_faces, graphic.value_colors)]
    wire_frame = []
    for room in rooms:
        wire_frame.extend(from_polyface3d_to_wireframe(room.geometry))
    legend = legend_objects(graphic.legend)
    title = text_objects(color_obj.title_text, graphic.lower_title_location,
                         graphic.legend_parameters.text_height,
                         graphic.legend_parameters.font)
    rooms = color_obj.matched_rooms
    colors = [color_to_color(col, 125) for col in graphic.value_colors]
    values = graphic.values
