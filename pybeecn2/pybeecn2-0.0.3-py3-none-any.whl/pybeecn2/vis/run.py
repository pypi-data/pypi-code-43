
import os
import shutil
import logging.config
import pandas as pd
import folium
import numpy as np
import branca.colormap as cm
import shapely.geometry as sg
import geopandas as gpd
import matplotlib.pyplot as plt
logger = logging.getLogger(__name__)


def setup_analysis_directory(directory):
    directory = os.path.abspath(directory)
    dirs = dict(
        plots=os.path.join(directory, 'plot_files'),
        data=os.path.join(directory, 'data_files'),
        geo=os.path.join(directory, 'geo_files'),
        report=os.path.join(directory, 'final_report')
    )

    # Creating New Analysis Directory (if required)
    if not os.path.exists(directory):
        logger.info("Creating New Analysis Directory: {}".format(directory))
        os.makedirs(directory)

    # Creating Sub directories
    for name, d in dirs.items():
        if not os.path.exists(d):
            logger.info("Creating Analysis {} Directory: {}".format(name, d))
            os.makedirs(d)

    return dirs
#
#
# def make_gpd_data_dict(url_dict):
#     data_dict = {}
#     for key in url_dict:
#         data_dict[key] = gpd.read_file(url_dict[key])
#
#     return data_dict
#
#
# def plot_boundary_points_png(point_gpd: gpd.geodataframe, boundary_gpd: gpd.geodataframe, plot_dir, show=False,
#                              figwidth=10, figheight=10, point_color='blue', boundary_color='green'):
#
#     f, ax = plt.subplots(figsize=(figwidth, figheight))
#     boundary_gpd.plot(ax=ax, color=boundary_color)
#     point_gpd.plot(ax=ax, color=point_color)
#     plt.xlabel('Latitude')
#     plt.ylabel('Longitude')
#     plt.title('BEECN Locations in Portland, OR')
#     if show:
#         plt.show()
#     f.savefig(os.path.join(plot_dir, 'beecn_locations.png'))
#     return
#
#
# def plot_population_map_html(gpd_data_dict: dict, url_dict: dict, dirs, pop_list: list,
#                              population_column='Total_Pop_5_n_over',
#                              fill_color='YlGn', fill_opacity=0.6, line_opacity=0.2):
#
#     # format the points in the data frame
#     gpd_data_dict['points']['geometry'] = gpd_data_dict['points']['geometry'].map(lambda x: str(x).lstrip('POINT (').rstrip(')'))
#     lat = []
#     lon = []
#
#     for row in gpd_data_dict['points']['geometry']:
#         try:
#             lon.append(row.split(' ')[0])
#             lat.append(row.split(' ')[1])
#         except:
#             lon.append(np.NaN)
#             lat.append(np.NaN)
#
#     gpd_data_dict['points']['latitude'] = lat
#     gpd_data_dict['points']['longitude'] = lon
#
#     latitude = np.array(gpd_data_dict['points']['latitude'])
#     latitude = latitude.astype(float)
#     longitude = np.array(gpd_data_dict['points']['longitude'])
#     longitude = longitude.astype(float)
#
#     # make the map object
#     m = folium.Map(location=[latitude.mean(), longitude.mean()], zoom_start=11.5)
#     population = folium.Choropleth(
#                                    geo_data=gpd_data_dict['boundaries'],
#                                    data=gpd_data_dict['boundaries'],
#                                    columns=['OBJECTID', population_column],
#                                    key_on='feature.properties.OBJECTID',
#                                    fill_color=fill_color,
#                                    fill_opacity=fill_opacity,
#                                    line_opacity=line_opacity,
#                                    legend_name='{} Population Size by Tract'.format(population_column),
#                                    highlight=True,
#                                    name='{} Population'.format(population_column),
#                                    show=True
#     ).add_to(m)
#
#     folium.GeoJson(
#         url_dict['boundaries'],
#         tooltip=folium.features.GeoJsonTooltip(fields=pop_list,
#                                                localize=True,
#                                                sticky=True),
#         smooth_factor=0.01
#     ).add_to(population.geojson)
#
#     beecn_site = gpd_data_dict['points']['SITE_NAME']
#     address = gpd_data_dict['points']['LOCATION']
#
#     location = zip(latitude, longitude)
#
#     points_fg = folium.FeatureGroup(name='BEECN Locations')
#     ring_fg = folium.FeatureGroup(name='1600m Radius')
#     count = 0
#
#     fname = os.path.join(dirs['plots'], 'total_population_bar.png')
#     for i in location:
#         tooltip = '<b>Name</b>: {} <br> ' \
#                   '<b>Address</b>: {} <br>'\
#                   .format(beecn_site[count], address[count])
#     # '<img src="{}" alt="Smiley face" height="100" width="100">'fname) can use to pull in images...
#
#         folium.Marker(i, icon=folium.Icon(icon='medkit', prefix='fa'),
#                       tooltip=tooltip).add_to(points_fg)
#         folium.Circle(i,
#                       weight=1.5,
#                       radius=1600).add_to(ring_fg)
#         count += 1
#
#     points_fg.add_to(m)
#     ring_fg.add_to(m)
#     m.add_child(folium.LayerControl())
#
#     map_path = os.path.join(dirs['plots'], '{}_population_map.html'.format(population_column))
#     m.save(map_path)
#
#     return m
#
# # Make data functions
# # ----------------------------------------------------------------------------------------------------------------------
# # todo: add tract summary functions
# # todo: find intersections of beecn circles and tract boundaries
#
# def geo_json_to_df(geo_url: str):
#     data = gpd.read_file(geo_url)
#     return data
#
#
# def get_id_and_pop(data: pd.DataFrame):
#     pop_list = ['OBJECTID', 'TRACT', 'Total_Pop_5_n_over', 'Spanish', 'Russian', 'Other_Slavic', 'Other_Indic',
#                 'Other_Indo_European', 'Chinese', 'Japanese', 'Korean', 'Mon_Khmer_Cambodian', 'Laotian', 'Vietnamese',
#                 'Other_Asian', 'Tagalog', 'Other_Pacific_Island', 'Arabic', 'African']
#     data = pd.DataFrame(data, columns=pop_list)
#     return data
#
#
# def make_totals_df(data: pd.DataFrame):
#
#     pop_dict = {}
#     for col in data:
#         if not col == 'OBJECTID' and not col == 'TRACT':
#             pop_dict[col] = data[col].sum()
#     df = pd.DataFrame.from_dict(pop_dict, orient='index', columns=['population'])
#     # total_total = df.loc[df.index == 'Total_Pop_5_n_over'].iloc[0]
#     # pops_total = df.loc[df.index != 'Total_Pop_5_n_over'].iloc[0:len(df)]
#     # pops_sum = pops_total.population.sum()
#     # df.loc['other_over_5'] = total_total - pops_sum
#     df.index.names = ['demographic']
#     return df
#
#
# def make_tract_pops_df(df):
#     print(df)
#
#
# def make_population_bar(data: pd.DataFrame, ax=None):
#     data.plot.barh(ax=ax)
#
#
# def get_single_population(data_gpd, column):
#     single_pop_df = pd.DataFrame(data_gpd[[column, 'OBJECTID', 'NAME']])
#     # single_pop_df.loc['Total'] = single_pop_df['Total_Pop_5_n_over'].sum()
#     # Could make another percentage column here if necessary
#     return single_pop_df


def get_map_data(url: str):
    points_data = gpd.read_file(url)
    return points_data


def make_locations(points: gpd.geoseries.GeoSeries):
    latitudes = []
    longitudes = []
    for pnt in points:
        tmp = str(pnt).lstrip('POINT (').rstrip(')')
        long, lat = tmp.split(' ')
        latitudes.append(float(lat))
        longitudes.append(float(long))
    points = []
    for lat, long in zip(latitudes, longitudes):
        points.append((lat, long))
    return points


def get_map_center(points: list):
    lats = [pnt[0] for pnt in points]
    longs = [pnt[1] for pnt in points]
    lat_ave = np.array(lats).mean()
    long_ave = np.array(longs).mean()
    return lat_ave, long_ave


def create_map(latitude: float, longitude: float):
    m = folium.Map(location=[latitude, longitude], zoom_start=11.5)
    return m


def make_choropleth(boundary_data, demographic):
    if 'Total' in demographic:
        show = True
    else:
        show = False
    population = folium.Choropleth(
                   geo_data=boundary_data,
                   data=boundary_data,
                   columns=['OBJECTID', demographic],
                   key_on='feature.properties.OBJECTID',
                   fill_color='YlGn',
                   fill_opacity=0.6,
                   line_opacity=0.2,
                   legend_name='{} Population Size by Tract'.format(demographic),
                   highlight=True,
                   name='{} Population'.format(demographic),
                   show=show)
    return population


def make_feature_points(points: list, point_names: list, addresses: list, layer_name=None):
    fg = folium.FeatureGroup(name=layer_name)
    for pnt, nm, add in zip(points, point_names, addresses):
        tooltip = '<b>Name</b>: {} <br>' \
                  '<b>Address</b>: {} <br>'.format(nm, add)
        folium.Marker(pnt, tooltip=tooltip).add_to(fg)
    return fg


def make_point_rings(points: list, layer_name='Ring', radius=1600):
    fg = folium.FeatureGroup(name=str(radius) + ' ' + layer_name)
    for pnt in points:
        folium.Circle(pnt, weight=1.5, radius=radius).add_to(fg)
    return fg


# def get_boundary(fg: folium.map.FeatureGroup):
#     json = fg.to_json()


def main(args):
    """
    :param args:
    :return:
    """
    demographics = ['Total_Pop_5_n_over', 'Spanish', 'Russian', 'Other_Slavic', 'Other_Indic',
                    'Other_Indo_European', 'Chinese', 'Japanese', 'Korean', 'Mon_Khmer_Cambodian',
                    'Laotian', 'Vietnamese', 'Other_Asian', 'Tagalog', 'Other_Pacific_Island',
                    'Arabic', 'African']

    # Setup plot directory
    # -----------------------------------------------------------------------------------------------------------------
    directory = os.path.join(args.directory, 'beecn')

    # Setup the directory
    # -----------------------------------------------------------------------------------------------------------------
    dirs = setup_analysis_directory(directory)

    if len(os.listdir(dirs["plots"])) != 0:
        logger.warning("Plots Directory: {} is not empty...removing old plots".format(os.path.join(dirs['plots'])))
        shutil.rmtree(dirs["plots"])
        os.makedirs(dirs["plots"])

    if len(os.listdir(dirs["data"])) != 0:
        logger.warning("Data Directory: {} is not empty...removing old files".format(os.path.join(dirs['data'])))
        shutil.rmtree(dirs["data"])
        os.makedirs(dirs["data"])

    # Get the data
    # -----------------------------------------------------------------------------------------------------------------
    logger.info('Getting the boundary data from {}'.format(args.boundaries))
    boundary_data = get_map_data(args.boundaries)
    logger.info('Points data...{}'.format(boundary_data))

    logger.info('Getting the point data from {}'.format(args.points))
    points_data = get_map_data(args.points)
    logger.info('Points data...{}'.format(points_data))

    # Start building the map
    # -----------------------------------------------------------------------------------------------------------------
    beecn_points = make_locations(points_data.geometry)
    lat, long = get_map_center(points=beecn_points)
    m = create_map(latitude=lat, longitude=long)
    for dem in enumerate(demographics):
        logger.info('Making map layer for {}'.format(demographics[dem[0]]))
        population = make_choropleth(boundary_data, demographics[dem[0]]).add_to(m)
        if dem[0] == 0:
            field = demographics
        else:
            field = [demographics[0], demographics[dem[0]]]
        folium.GeoJson(boundary_data,
                       tooltip=folium.features.GeoJsonTooltip(fields=field,
                                                              localize=True,
                                                              sticky=True),
                       smooth_factor=0.0
                       ).add_to(population.geojson)
        for key in population._children.keys():
            if 'color_map' in key:
                del(population._children[key])
    been_fg = make_feature_points(beecn_points, points_data.SITE_NAME, points_data.LOCATION,
                                  layer_name='BEECN Sites').add_to(m)
    radius_fg = make_point_rings(beecn_points).add_to(m)

    m.add_child(folium.LayerControl())

    fname = os.path.join(dirs['plots'], 'population_map_center_{}_{}.html'.format(lat, long))
    m.save(fname)
