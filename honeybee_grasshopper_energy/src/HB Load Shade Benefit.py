# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Visualize the desirability of shade in terms of its impact on the annual heating
and cooling loads of Honeybee Rooms.
_
The calculation runs by performing a simple fast energy simulation of the
connected Honeybee Rooms without any shade other than context. The resulting
heating/cooling loads are extracted at each timestep of the simulation along with
the direct (beam) solar gain through each of the Room's windows. Solar vectors
are generated for each step of the simulation and projected from the Room's
Aperture geometries through the shades assigned to those Apertures.
_
Solar vectors for timesteps when the Room is cooling mode contribute positively
to shade desirability (shade help) while solar vectors for hours when the
Room is heating mode contribute negatively (shade harm). This contribution
is weighted by how much cooling or heating energy the Room requires at the
timestep along with the direct solar gain through each Aperture at the timestep.
_
The component outputs a colored mesh of the shades assigned to the Room Apertures
illustrating the net effect of shading each part of the geometry. A higher
saturation of blue indicates that shading the cell is desirable. A higher
saturation of red indicates that shading the cell is harmful (blocking more sun
when the Room is in heating mode than cooling mode). Desaturated cells indicate
that shading the cell will have relatively little effect on the heating or
cooling loads of the Room.
_
The units for shade desirability are kWh of Room cooling load avoided per unit
area of shade if the test cell of the shade is helpful (blue). If the test cell
is harmful (red), the units are kWh of Room heating load increased per unit
area of shade. So, if a given square meter of input _shade_geo has a shad
desirability of 10 kWh/m2, this means that a shade in this location provides
roughly 10 kWh of avoided cooling load to the parent Room over the year.
_
The method used by this component is based off of the Shaderade method developed
by Jon Sargent, Jeffrey Niemasz and Christoph Reinhart. More information can be
found in the following publication document:
Sargent, Jon; Niemasz, Jeffrey; Reinhart, Christoph. SHADERADE: Combining
Rhinoceros and EnergyPlus for the Design of Static Exterior Shading Devices.
Building Simulation, 2011, Sydney, Australia.
http://www.ibpsa.org/proceedings/bs2011/p_1209.pdf
-

    Args:
        _rooms: A list of Honeybee Rooms for which cooling/heating shade benefit/harm will
            be evaluated. At least some of these Rooms should have Apertures
            with Shades assigned to them in order for this component to produce
            meaningful results. Note that all Shades generated with the "HB Louver
            Shades" component or the "HB Extruded Border" component are
            automatically assigned to a parent Aperture. For more complex
            Shade geometries, the "HB Add Shade" component can be used to
            assign the Shade to a parent Aperture.
        context_: Honeybee Shades representing context geometry that can block sun
            to the _rooms, therefore discounting any benefit or harm that could
            come to the Room's Shades.
        _epw_file: Path to an .epw file on your system as a text string. This will be
            used in the energy simulation to determine heating/cooling loads
            and to generate solar vectors for the shade benefit calculation.
        _north_: A number between -360 and 360 for the counterclockwise difference
            between the North and the positive Y-axis in degrees.
            90 is West and 270 is East. (Default: 0).
        _grid_size: A positive number in Rhino model units for the size of grid cells at
            which the Shade geometries of the input _rooms will be subdivided
            for shade benefit analysis. The smaller the grid size, the higher
            the resolution of the analysis and the longer the calculation will
            take. So it is recommended that one start with a large value here
            and decrease the value as needed. However, the grid size should
            usually be smaller than the dimensions of the smallest piece of
            Shade geometry in order to yield meaningful results.
        _timestep_: An integer for the number of timesteps per hour at which the energy
            simulation will run and sun vectors will be generated for the analysis.
            Higher values will result in the generation of more vectors, which
            will make the resulting shade meshes smoother and produce a better
            representation of real benefit/harm. However, the calculation will take
            longer as there are more intersection operations to perform. The
            default is 1 timestep per hour, which is the coarsest resolution
            avalable and the fastest calculation.
        lag_time_: A number for the amount of time in hours between when solar gain
            eneters the room and the gain results in an increased cooling load.
            Typically, it takes an hour or so for solar gains falling on the
            room floors to heat up the floor surface and then convect to the
            room air where the gain can be absorbed by a cooling system. This
            means that the cooling value associated with each sun vector should
            be a step or two after the time of the sun vector. Lag time can
            be longer than an hour if the room has a particularly high thermal
            mass or it may be shorter if the room has less mass or uses a radiant
            cooling system integrated into the floor where the sun is absorbed.
            Note that the value input here can be a decimal value to indicate
            that the lag time is a fraction of an hour. (Default: 1.0 hour).
        legend_par_: Optional legend parameters from the "LB Legend Parameters"
            that will be used to customize the display of the results.
        _cpu_count_: An integer to set the number of CPUs used in the execution of the
            intersection calculation. If unspecified, it will automatically default
            to one less than the number of CPUs currently available on the
            machine or 1 if only one processor is available.
        _run: Set to "True" to run the component and perform shade benefit analysis.

    Returns:
        report: ...
        vectors: The sun vectors that were used to evaluate the shade (note that
            these will increase as the _timestep_ increases).
        points: Points across the room Aperture geometry from which sun vectors
            are projected. Note that only Apertures with assigned Shades are
            evaluated in order to avoid unnessarily increasing the calculation
            time by evaluating windows for which there is not shade.
        mesh: A colored mesh of the Shades assigned to the room's apertures showing
            where shading is helpful (blue), harmful (red), or does not make
            much of a difference (white or desaturated colors). Note that
            the colors can change depending upon the input legend_par_.
        legend: Legend showing the numeric values of kWh per unit shade area of
            decreased/increased cooling/heating load that correspond to the
            colors in the shade mesh.
        title: A text object for the study title.
        shade_help: The cumulative kWh of avoided cooling load per square area unit
            obtained by shading the given cell. If a given square meter of
            shade geometry has a helpfulness of 10 kWh/m2, this means that
            a shade in this location decreases the cooling load of the Room
            by roughly 10 kWh over the year.
        shade_harm: The cumulative kWh of increased heating load per square area unit
            obtained by shading the given cell. If a given square meter of
            shade geometry has a harmfulness of -10 kWh/m2, this means that
            a shade in this location increases the heating load of the Room
            by roughly 10 kWh over the year.
        shade_net: The sum of the helpfulness and harmfulness for each cell. This will be
            negative if shading the cell has a net harmful effect and positive
            if the shade has a net helpful effect.
"""

ghenv.Component.Name = 'HB Load Shade Benefit'
ghenv.Component.NickName = 'LoadShadeBenefit'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import os
import subprocess
import json
import math

try:
    from ladybug_geometry.geometry3d import Mesh3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from ladybug.futil import write_to_file_by_name, nukedir
    from ladybug.sunpath import Sunpath
    from ladybug.color import Colorset
    from ladybug.graphic import GraphicContainer
    from ladybug.epw import EPW
    from ladybug.sql import SQLiteResult
    from ladybug.datacollection import HourlyContinuousCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.config import folders
    from honeybee.boundarycondition import Outdoors
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.simulation.parameter import SimulationParameter
    from honeybee_energy.run import run_idf
    from honeybee_energy.result.err import Err
    from honeybee_energy.writer import energyplus_idf_version
    from honeybee_energy.config import folders as energy_folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from lbt_recipes.version import check_energyplus_version
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_vector2d, to_joined_gridded_mesh3d
    from ladybug_rhino.fromgeometry import from_face3d, from_mesh3d, \
        from_point3d, from_vector3d
    from ladybug_rhino.config import conversion_to_meters, units_system, \
        tolerance, angle_tolerance, units_abbreviation
    from ladybug_rhino.fromobjects import legend_objects
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.intersect import join_geometry_to_mesh, generate_intersection_rays, \
        intersect_rays_with_mesh_faces
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning, hide_output, \
        recommended_processor_count
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def serialize_data(data_dicts):
    """Reserialize a list of HourlyContinuousCollection dictionaries."""
    return [HourlyContinuousCollection.from_dict(data) for data in data_dicts]

# List of all the output strings that will be requested
cool_out = 'Zone Ideal Loads Supply Air Total Cooling Energy'
heat_out = 'Zone Ideal Loads Supply Air Total Heating Energy'
solar_out = 'Surface Window Transmitted Beam Solar Radiation Energy'
all_output = (cool_out, heat_out, solar_out)


if all_required_inputs(ghenv.Component) and _run:
    # check the presence of energyplus and check that the version is compatible
    check_energyplus_version()

    # set the defaults and process all of the inputs
    workers = _cpu_count_ if _cpu_count_ is not None else recommended_processor_count()
    timestep = _timestep_ if _timestep_ is not None else 1
    lag_time = 1 if lag_time_ is None else lag_time_
    lag_steps = int(timestep * lag_time)
    if _north_ is not None:  # process the north_
        try:
            _north_ = math.degrees(
                to_vector2d(_north_).angle_clockwise(Vector2D(0, 1)))
        except AttributeError:  # north angle instead of vector
            _north_ = float(north_)
    else:
        _north_ = 0

    # gather all assigned shades and remove them from the rooms
    rooms = [r.duplicate() for r in _rooms]  # duplicate to avoid editing input
    ap_count, shd_count = 0, 0
    shade_dict = {}
    for room in rooms:
        if room.properties.energy.is_conditioned and \
                room.properties.energy.setpoint is not None:
            r_dict = {}
            for face in room.faces:
                if isinstance(face.boundary_condition, Outdoors):
                    aps = face.apertures
                    if len(aps) != 0:
                        fap_ids, fap_geos, fshd_geos = [], [], []
                        for ap in aps:
                            fap_ids.append(ap.identifier.upper())
                            fap_geos.append(from_face3d(ap.geometry))
                            fshd_geos.extend(from_face3d(shd.geometry)
                                             for shd in ap.outdoor_shades)
                            ap.remove_shades()  # remove shades for the energy simulation
                        if len(fshd_geos) != 0:
                            r_dict[face.identifier] = {
                                'ap_ids': fap_ids,
                                'ap_geo': fap_geos,
                                'shd_geo': fshd_geos,
                                'normal': from_vector3d(face.normal)
                            }
                            ap_count += len(fap_geos)
                            shd_count += len(fshd_geos)
            if len(r_dict) != 0:
                shade_dict[room.identifier.upper()] = r_dict

    # make sure that there are shades to evaluate
    if shd_count == 0:
        msg = 'There were no shades to evaluate across all of the input _rooms.\n' \
            'Make sure that shades are assigned to the apertures of conditioned\n' \
            'rooms or use components like "HB Louver Shades" to generate shades\n' \
            'that are assigned to the apertures.'
        print(msg)
        raise ValueError(msg)
    else:
        msg = 'Evaluating {} shade geometries across {} apertures.'.format(
            shd_count, ap_count)
        print(msg)

    # create the Model from the _rooms and context_
    _model = Model('Load_Shade_Benefit', rooms, orphaned_shades=context_,
                   units=units_system(),
                   tolerance=tolerance, angle_tolerance=angle_tolerance)

    # process the simulation folder name and the directory
    directory = os.path.join(folders.default_simulation_folder, _model.identifier)
    sch_directory = os.path.join(directory, 'schedules')
    nukedir(directory)  # delete any existing files in the directory

    # create simulation parameters for the coarsest/fastest E+ sim possible
    _sim_par_ = SimulationParameter()
    _sim_par_.timestep = timestep
    _sim_par_.north_angle = _north_
    _sim_par_.shadow_calculation.solar_distribution = 'FullExterior'
    _sim_par_.output.reporting_frequency = 'Timestep'
    _sim_par_.output.include_html = False
    for out_p in all_output:
        _sim_par_.output.add_output(out_p)

    # assign design days from the EPW
    msg = None
    folder, epw_file_name = os.path.split(_epw_file)
    ddy_file = os.path.join(folder, epw_file_name.replace('.epw', '.ddy'))
    if os.path.isfile(ddy_file):
        try:
            _sim_par_.sizing_parameter.add_from_ddy_996_004(ddy_file)
        except AssertionError:
            msg = 'No design days were found in the .ddy file next to the _epw_file.'
    else:
         msg = 'No .ddy file was found next to the _epw_file.'
    if msg is not None:
        epw_obj = EPW(_epw_file)
        des_days = [epw_obj.approximate_design_day('WinterDesignDay'),
                    epw_obj.approximate_design_day('SummerDesignDay')]
        _sim_par_.sizing_parameter.design_days = des_days
        msg = msg + '\nDesign days were generated from the input _epw_file but this ' \
            '\nis not as accurate as design days from DDYs distributed with the EPW.'
        give_warning(ghenv.Component, msg)
        print(msg)

    # create the strings for simulation paramters and model
    ver_str = energyplus_idf_version() if energy_folders.energyplus_version \
        is not None else energyplus_idf_version(compatibe_ep_version)
    sim_par_str = _sim_par_.to_idf()
    model_str = _model.to.idf(
        _model, schedule_directory=sch_directory, patch_missing_adjacencies=True)
    idf_str = '\n\n'.join([ver_str, sim_par_str, model_str])

    # write the final string into an IDF
    idf = os.path.join(directory, 'in.idf')
    write_to_file_by_name(directory, 'in.idf', idf_str, True)

    # run the IDF through EnergyPlus
    silent = True if _run == 1 else False
    sql, zsz, rdd, html, err = run_idf(idf, _epw_file, silent=silent)
    if sql is None and err is not None:  # something went wrong; parse the errors
        err_obj = Err(err)
        print(err_obj.file_contents)
        for error in err_obj.fatal_errors:
            raise Exception(error)

    # parse the result sql and get the timestep data collections
    if os.name == 'nt':  # we are on windows; use IronPython like usual
        sql_obj = SQLiteResult(sql)
        cooling = sql_obj.data_collections_by_output_name(cool_out)
        heating = sql_obj.data_collections_by_output_name(heat_out)
        solar = sql_obj.data_collections_by_output_name(solar_out)
    else:  # we are on Mac; sqlite3 module doesn't work in Mac IronPython
        # Execute the honybee CLI to obtain the results via CPython
        cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'result',
                'data-by-outputs', sql]
        for outp in all_output:
            cmds.append('["{}"]'.format(outp))
        custom_env = os.environ.copy()
        custom_env['PYTHONHOME'] = ''
        process = subprocess.Popen(cmds, stdout=subprocess.PIPE, env=custom_env)
        stdout = process.communicate()
        data_coll_dicts = json.loads(stdout[0])
        cooling = serialize_data(data_coll_dicts[0])
        heating = serialize_data(data_coll_dicts[1])
        solar = serialize_data(data_coll_dicts[2])

    # convert the results to a dictionary for quick access
    cool_dict, heat_dict, solar_dict = {}, {}, {}
    for cool in cooling:
        cool_dict[cool.header.metadata['System'].split(' ')[0]] = cool
    for heat in heating:
        heat_dict[heat.header.metadata['System'].split(' ')[0]] = heat
    for sol in solar:
        solar_dict[sol.header.metadata['Surface']] = sol

    # initialize sunpath based on the EPW and get all of the vectors
    epw_obj = EPW(_epw_file)
    location = epw_obj.location
    sp = Sunpath.from_location(location, _north_)
    lb_vecs, relevant_i = [], []
    for i, dt in enumerate(solar[0].datetimes):
        sun = sp.calculate_sun_from_date_time(dt)
        if sun.is_during_day:
            lb_vecs.append(sun.sun_vector_reversed)
            relevant_i.append(i)
    vectors = [from_vector3d(lb_vec) for lb_vec in lb_vecs]

    # if there is context, remove any rays that are blocked by the context
    context_mesh = None
    if len(context_) != 0 and context_[0] is not None:
        context_mesh = join_geometry_to_mesh([from_face3d(c.geometry) for c in context_])

    # loop through the relevant rooms and compute shade benefit
    points, mesh = [], []
    shade_help, shade_harm, shade_net = [], [], []
    hide_output(ghenv.Component, 2)
    for room_id, room_data in shade_dict.items():
        cool_vals = cool_dict[room_id].values
        heat_vals = heat_dict[room_id].values
        # shif the values by the lag
        cool_vals = cool_vals[-lag_steps:] + cool_vals[:-lag_steps]
        heat_vals = heat_vals[-lag_steps:] + heat_vals[:-lag_steps] 
        for ap_data in room_data.values():
            solar_vals = solar_dict[ap_data['ap_ids'][0]]
            for ap_id in ap_data['ap_ids'][1:]:
                solar_vals += solar_dict[ap_id]

            # create the gridded mesh from the geometry
            analysis_mesh = to_joined_gridded_mesh3d(ap_data['shd_geo'], _grid_size)
            ap_mesh = from_mesh3d(analysis_mesh)
            study_mesh = to_joined_gridded_mesh3d(ap_data['ap_geo'], _grid_size / 1.75)
            ap_points = [from_point3d(pt) for pt in study_mesh.face_centroids]
            points.extend(ap_points)
            mesh.append(analysis_mesh)

            # create a series of rays that represent the sun projected through the shade
            int_rays = generate_intersection_rays(ap_points, vectors)
            normals = [ap_data['normal']] * len(int_rays)

            # intersect the sun rays with the shade mesh
            face_int = intersect_rays_with_mesh_faces(
                ap_mesh, int_rays, context_mesh, normals, cpu_count=workers)

            # loop through the face intersection result and evaluate the benefit
            pt_div = 1 / float(len(ap_points))
            for face_res, face_area in zip(face_int, analysis_mesh.face_areas):
                f_help, f_harm = 0, 0
                for t_ind in face_res:
                    ri = relevant_i[t_ind]
                    cl, ht, sl = cool_vals[ri], heat_vals[ri], solar_vals[ri]
                    if cl > 0:  # a step where shade helps
                        f_help += min(cl, sl)
                    elif ht > 0:
                        f_harm -= min(ht, sl)
                # Normalize by the area of the cell so there's is a consistent metric
                # between cells of different areas.
                shd_help = ((f_help / face_area)) * pt_div
                shd_harm = ((f_harm / face_area)) * pt_div
                shade_help.append(shd_help)
                shade_harm.append(shd_harm)
                shade_net.append(shd_help + shd_harm)

    # create the mesh and legend outputs
    mesh = Mesh3D.join_meshes(mesh)
    graphic = GraphicContainer(shade_net, mesh.min, mesh.max, legend_par_)
    graphic.legend_parameters.title = 'kWh/{}2'.format(units_abbreviation())
    if legend_par_ is None or legend_par_.are_colors_default:
        graphic.legend_parameters.colors = reversed(Colorset.shade_benefit_harm())
    if legend_par_ is None or legend_par_.min is None or legend_par_.max is None:
        bnd_val = max(max(shade_net), abs(min(shade_net)))
        if legend_par_ is None or legend_par_.min is None:
            graphic.legend_parameters.min = -bnd_val
        if legend_par_ is None or legend_par_.max is None:
            graphic.legend_parameters.max = bnd_val
    title = text_objects('Cooling/Heating Load Shade Benefit', graphic.lower_title_location,
                         graphic.legend_parameters.text_height * 1.5,
                         graphic.legend_parameters.font)

    # create all of the visual outputs
    mesh.colors = graphic.value_colors
    mesh = from_mesh3d(mesh)
    legend = legend_objects(graphic.legend)
