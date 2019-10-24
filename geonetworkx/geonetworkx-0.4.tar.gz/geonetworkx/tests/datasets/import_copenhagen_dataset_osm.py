import geonetworkx as gnx
import osmnx as ox
from shapely.wkt import loads

study_area_wkt = "Polygon ((12.5747751995698902 55.67132899603028307, 12.57548328201693799 55.66792134925386648," \
                 " 12.57951050093452139 55.666947735889174, 12.58490962959326076 55.67053240327735608," \
                 " 12.59194619891079547 55.67424983612435341, 12.60000063674596227 55.67840982050076093," \
                 " 12.60181509801652133 55.68071108845366268, 12.6022576495459262 55.68199448788893591," \
                 " 12.59920404399303351 55.68217150850070141, 12.59513256992251051 55.68274682548892685," \
                 " 12.59291981227548618 55.6826140600301045, 12.58309516832269992 55.67637408346549677," \
                 " 12.5747751995698902 55.67132899603028307))"

study_area = loads(study_area_wkt)

streets_net = ox.graph_from_polygon(study_area)
streets_net = gnx.read_geograph_with_coordinates_attributes(streets_net)
streets_net.name = "streets_net"

ferry_net = ox.graph_from_polygon(study_area, infrastructure='relation["route"="ferry"]', clean_periphery=False,
                                  simplify=False, custom_filter="")

ferry_net = gnx.read_geograph_with_coordinates_attributes(ferry_net)
ferry_net.name = "ferry_net"

merged_graph = gnx.spatial_graph_merge(streets_net, ferry_net)
merged_graph.name = "ferry_and_streets"

gnx.write_geofile(merged_graph, r"D:\projets\GeoNetworkX\GeoNetworkX\geonetworkx\tests\datasets\trash", driver="GeoJSON")
gnx.write_geofile(ferry_net, r"D:\projets\GeoNetworkX\GeoNetworkX\geonetworkx\tests\datasets\trash", driver="GeoJSON")
gnx.write_geofile(streets_net, r"D:\projets\GeoNetworkX\GeoNetworkX\geonetworkx\tests\datasets\trash", driver="GeoJSON")

gdf = ox.footprints_from_polygon(study_area)
gdf["geometry"] = gdf["geometry"].centroid
gdf.drop(columns =["nodes"], inplace=True)

gdf.to_file("copenhagen_buildings.geojson", driver="GeoJSON")
import os
os.getcwd()