"""
This work was authored by Gabriel McBride in support
of Portland Open Data Program and Portland Bureau of
Emergency Management BEECN Program. The effort was
conducted as a use case for the student's masters
project to study the interaction between Systems
Engineering and Data Science activities.
"""
import os
import shutil
import subprocess
import glob
import pybeecn.vis.mapping as mp
import shapely.geometry as sg
import geopandas as gpd
import folium

points_url = 'https://opendata.arcgis.com/datasets/6e6185533d5447deb8b7204c27e1858e_92.geojson'
boundary_url = 'https://opendata.arcgis.com/datasets/386fd0d07bca42d09f4fd46462bf8a7d_121.geojson'


def test_get_points_data():
    points_data = mp.get_map_data(points_url)
    assert len(points_data) > 0
    assert 'geometry' in [col for col in points_data.columns]
    assert isinstance(points_data['geometry'], gpd.geoseries.GeoSeries)
    assert isinstance(points_data['geometry'][0], sg.point.Point)


def test_get_boundary_data():
    boundary_data = mp.get_map_data(boundary_url)
    assert len(boundary_data) > 0
    assert 'geometry' in [col for col in boundary_data.columns]
    assert isinstance(boundary_data['geometry'], gpd.geoseries.GeoSeries)
    assert isinstance(boundary_data['geometry'][0], sg.polygon.Polygon)


def test_make_locations():
    points_gpd = gpd.read_file(points_url)
    points = points_gpd.geometry
    pnts = mp.make_locations(points)
    assert [isinstance(l, float) for l in pnts[0]]
    assert [isinstance(l, float) for l in pnts[1]]


def test_get_map_center():
    points = [(45, -122), (46, -123), (47, -122), (48, -124)]
    # lat, long = mp.get_map_center(points)
    lat, long = mp.get_map_center(points)
    assert isinstance(points, list)
    assert isinstance(lat, float)
    assert isinstance(long, float)


def test_create_map():
    m = mp.create_map(latitude=45.51710899, longitude=-122.640867)
    assert isinstance(m, folium.folium.Map)


def test_add_pop_to_map():
    boundary_data = gpd.read_file(boundary_url)
    chloro = mp.make_choropleth(boundary_data, 'African')
    assert isinstance(chloro, folium.features.Choropleth)


def test_add_feature_points():
    m = folium.Map(location=[122, 45])
    points_gpd = gpd.read_file(points_url)
    points = mp.make_locations(points_gpd.geometry)
    addresses = points_gpd.LOCATION
    point_names = points_gpd.SITE_NAME
    fg = mp.make_feature_points(points, point_names, addresses).add_to(m)
    assert isinstance(m, folium.Map)
    assert isinstance(fg, folium.map.FeatureGroup)


# def test_get_boundary():
#     m = folium.Map(location=[45, -122])
#     boundary_data = gpd.read_file(boundary_url)
#     fg = mp.make_choropleth(boundary_data, demographic='African').add_to(m)
#     mp.get_boundary(fg)


def test_view_map():

    tmp_dir = os.path.join('/tmp', 'test_beecn_files')
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    else:
        os.makedirs(tmp_dir)
    plot_dir = os.path.join(tmp_dir, 'plots_dir')
    cmd = 'pybeecn vis map --directory {} '.format(tmp_dir)
    cmd += '--boundaries {} --points {}'.format(boundary_url, points_url)
    subprocess.check_output(cmd, shell=True)

    html_files = glob.glob(os.path.join(plot_dir, '*html*'))
    png_files = glob.glob(os.path.join(plot_dir, '*png*'))

    for f in html_files:
        assert os.path.getsize(f) > 0
    for f in png_files:
        assert os.path.getsize(f) > 0
    shutil.rmtree(tmp_dir)

