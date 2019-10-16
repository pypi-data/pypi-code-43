import rasterio
import numpy as np
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, date
from rasterio.mask import mask
import fiona
import imageio
import os
import matplotlib
import matplotlib.pyplot as plt
import shutil
import geopandas as gpd
from rasterio.warp import calculate_default_transform, reproject, Resampling
import xarray as xr
import json

### draft for adampy python package

class getEndpoints:
    def __init__(self, username, password):
        self.username = user
        self.password = password

    ###this function should return the list of available endpoints
    def get_data(self):
        endpoints_list = endpoints( self.username, self.password )
        return endpoints_list

class getCollections:
    def __init__(self,endpoint):
        self.endpoint = endpoint

    ##this function shouldl return a list of all available colletions given endpoint. It can use the class getCapabilites
    def get_data(self):
        url = 'https://{}/wcs?service=WCS&Request=GetCapabilities'.format(self.endpoint)
        result = requests.get(url)

        xml_data = result.text

        tree = ET.fromstring(xml_data)

        collection_list = []

        for i in tree.iter('{http://www.opengis.net/wcs/2.0}CoverageId'):
            collection_list.append(i.text)

        return sorted(collection_list)

class getCatalogue:
    def __init__(self, endpoint, time_t, collection, min_long, max_lat, max_long, min_lat):
        self.endpoint = endpoint
        self.collection = collection
        self.min_lat = min_lat
        self.max_lat = max_lat
        self.min_long = min_long
        self.max_long = max_long
        self.time_t = time_t

    ##this function shouldl return a list of all available colletions given endpoint. It can use the class getCapabilites
    def get_data(self):
        url = 'https://{}/pycsw/pycsw/csw.py?mode=opensearch&service=CSW&version=2.0.2&request=GetRecords&elementsetname=brief&typenames=csw:Record&resulttype=results&time={}&q={}&maxrecords=100&outputFormat=application/json&bbox={},{},{},{}'.format(self.endpoint, self.time_t, self.collection, self.min_long, self.max_lat, self.max_long, self.min_lat)

        result = requests.get(url)

        return json.loads(result.text)

class getImage:
    def __init__(self, endpoint, collection, time_t, min_lat = -90, max_lat = 90, min_long = -180, max_long = 180, token = 'None', geometry = 'None', masking = False, fname = 'image.tif', mgrs_tile = 'None', scale = 1, xarray_out = False, netcdf_out = False):
        self.endpoint = endpoint
        self.collection = collection
        #self.geometry = geometry
        self.min_lat = min_lat
        self.max_lat = max_lat
        self.min_long = min_long
        self.max_long = max_long
        self.time_t = time_t
        self.token = token
        self.geometry = geometry
        self.masking = masking
        self.fname = fname
        self.mgrs_tile = mgrs_tile
        self.scale = scale
        self.xarray_out = xarray_out
        self.netcdf_out = netcdf_out
        #self.output_format = output_format

    def get_data(self):

        if self.masking == True:
            df = gpd.read_file(self.geometry)
            geom = df['geometry'][0]
            if self.mgrs_tile != 'None':
                url = "https://{}/wcs?service=WCS&Request=GetCoverage&version=2.0.0&subset=unix({})&format=image/tiff&filter=false&CoverageId={}&subset=Lat({},{})&subset=Long({},{})&token={}&scale={}&mgrs_tile={}".format(self.endpoint,self.time_t,self.collection, geom.bounds[1]-1, geom.bounds[3]+1, geom.bounds[0]-1, geom.bounds[2]+1, self.token, self.scale,self.mgrs_tile)
            else:
                url = "https://{}/wcs?service=WCS&Request=GetCoverage&version=2.0.0&subset=unix({})&format=image/tiff&filter=false&CoverageId={}&subset=Lat({},{})&subset=Long({},{})&token={}&scale={}".format(self.endpoint,self.time_t,self.collection, geom.bounds[1], geom.bounds[3], geom.bounds[0], geom.bounds[2], self.token, self.scale)

        else:
            if self.mgrs_tile != 'None':
                url = "https://{}/wcs?service=WCS&Request=GetCoverage&version=2.0.0&subset=unix({})&format=image/tiff&filter=false&CoverageId={}&subset=Lat({},{})&subset=Long({},{})&token={}&scale={}&mgrs_tile={}".format(self.endpoint,self.time_t,self.collection, self.min_lat, self.max_lat, self.min_long, self.max_long, self.token, self.scale, self.mgrs_tile)
            else:
                url = "https://{}/wcs?service=WCS&Request=GetCoverage&version=2.0.0&subset=unix({})&format=image/tiff&filter=false&CoverageId={}&subset=Lat({},{})&subset=Long({},{})&token={}&scale={}".format(self.endpoint,self.time_t,self.collection, self.min_lat, self.max_lat, self.min_long, self.max_long, self.token, self.scale)

        # if self.mgrs_tile != 'None':
        #     url = "https://{}/wcs?service=WCS&Request=GetCoverage&version=2.0.0&subset=unix({})&format=image/tiff&CoverageId={}&subset=Lat({},{})&subset=Long({},{})&token={}&mgrs_tile={}&filter=false".format(self.endpoint,self.time_t,self.collection, self.min_lat, self.max_lat, self.min_long, self.max_long, self.token, self.mgrs_tile)
        # else:
        #     url = "https://{}/wcs?service=WCS&Request=GetCoverage&version=2.0.0&subset=unix({})&format=image/tiff&CoverageId={}&token={}&mgrs_tile={}&filter=false".format(self.endpoint,self.time_t,self.collection, self.token, self.mgrs_tile)

        #print(url)
        result = requests.get(url)
        with open(self.fname, 'wb') as f:
            f.write(result.content)
            f.close()


        #if image is sentinel2 tiled transform to EPSG:4326


        src = rasterio.open(self.fname)
        out_image = src.read(1)
        out_image = out_image.astype(np.float32)
        out_image[out_image == src.nodata] = 'nan'
        out_meta = src.meta.copy()
        out_meta.update({"bbox": src.bounds})

        if 'EU_CAMS' in self.collection:
            out_meta.update({"offset": src.offsets[0],
                            "scale": src.scales[0]})

        if self.masking == True:
            with fiona.open(self.geometry, "r") as shapefile:
                features = [feature["geometry"] for feature in shapefile]
            out_image, out_transform = mask(src, features, crop=True)
            out_image = out_image.astype(np.float32)
            out_image[out_image == src.nodata] = 'nan'
            out_image = out_image[0,:,:]
            out_meta = src.meta.copy()

            if 'EU_CAMS' in self.collection:
                out_meta.update({"driver": "GTiff",
                                "height": out_image.shape[0],
                                "width": out_image.shape[1],
                                "transform": out_transform,
                                "offset": src.offsets[0],
                                "scale": src.scales[0]})
            else:
                out_meta.update({"driver": "GTiff",
                                "height": out_image.shape[0],
                                "width": out_image.shape[1],
                                "transform": out_transform})

            new_dataset = rasterio.open(self.fname, 'w', **out_meta)

            new_dataset.write(out_image, 1)
            new_dataset.close()

        if self.netcdf_out == True:
            da = xr.open_rasterio(self.fname)
            da.to_netcdf('{}.nc'.format(self.fname[:-4]))

        if self.xarray_out == True:
            da = xr.open_rasterio(self.fname)

            return da, out_meta

        return out_image, out_meta


class getImageSentinel2:
    def __init__(self, endpoint, collection, time_t, min_lat = -90, max_lat = 90, min_long = -180, max_long = 180, token = 'None', geometry = 'None', masking = False, fname = 'image.tif', mgrs_tile = 'None', scale = 1, xarray_out = False, netcdf_out = False):
        self.endpoint = endpoint
        self.collection = collection
        #self.geometry = geometry
        self.min_lat = min_lat
        self.max_lat = max_lat
        self.min_long = min_long
        self.max_long = max_long
        self.time_t = time_t
        self.token = token
        self.geometry = geometry
        self.masking = masking
        self.fname = fname
        self.mgrs_tile = mgrs_tile
        self.scale = scale
        self.xarray_out = xarray_out
        self.netcdf_out = netcdf_out
        #self.output_format = output_format

    def get_data(self):

        if self.masking == True:
            df = gpd.read_file(self.geometry)
            geom = df['geometry'][0]
            if self.mgrs_tile != 'None':
                url = "https://{}/wcs?service=WCS&Request=GetCoverage&version=2.0.0&subset=unix({})&format=image/tiff&filter=false&CoverageId={}&subset=Lat({},{})&subset=Long({},{})&token={}&scale={}&mgrs_tile={}".format(self.endpoint,self.time_t,self.collection, geom.bounds[1]-1, geom.bounds[3]+1, geom.bounds[0]-1, geom.bounds[2]+1, self.token, self.scale,self.mgrs_tile)
            else:
                url = "https://{}/wcs?service=WCS&Request=GetCoverage&version=2.0.0&subset=unix({})&format=image/tiff&filter=false&CoverageId={}&subset=Lat({},{})&subset=Long({},{})&token={}&scale={}".format(self.endpoint,self.time_t,self.collection, geom.bounds[1], geom.bounds[3], geom.bounds[0], geom.bounds[2], self.token, self.scale)

        else:
            if self.mgrs_tile != 'None':
                url = "https://{}/wcs?service=WCS&Request=GetCoverage&version=2.0.0&subset=unix({})&format=image/tiff&filter=false&CoverageId={}&subset=Lat({},{})&subset=Long({},{})&token={}&scale={}&mgrs_tile={}".format(self.endpoint,self.time_t,self.collection, self.min_lat, self.max_lat, self.min_long, self.max_long, self.token, self.scale, self.mgrs_tile)
            else:
                url = "https://{}/wcs?service=WCS&Request=GetCoverage&version=2.0.0&subset=unix({})&format=image/tiff&filter=false&CoverageId={}&subset=Lat({},{})&subset=Long({},{})&token={}&scale={}".format(self.endpoint,self.time_t,self.collection, self.min_lat, self.max_lat, self.min_long, self.max_long, self.token, self.scale)

        # if self.mgrs_tile != 'None':
        #     url = "https://{}/wcs?service=WCS&Request=GetCoverage&version=2.0.0&subset=unix({})&format=image/tiff&CoverageId={}&subset=Lat({},{})&subset=Long({},{})&token={}&mgrs_tile={}&filter=false".format(self.endpoint,self.time_t,self.collection, self.min_lat, self.max_lat, self.min_long, self.max_long, self.token, self.mgrs_tile)
        # else:
        #     url = "https://{}/wcs?service=WCS&Request=GetCoverage&version=2.0.0&subset=unix({})&format=image/tiff&CoverageId={}&token={}&mgrs_tile={}&filter=false".format(self.endpoint,self.time_t,self.collection, self.token, self.mgrs_tile)

        #print(url)
        result = requests.get(url)
        with open(self.fname, 'wb') as f:
            f.write(result.content)
            f.close()


        #if image is sentinel2 tiled transform to EPSG:4326
        dst_crs = 'EPSG:4326'

        with rasterio.open(self.fname) as src:
            transform, width, height = calculate_default_transform(
                src.crs, dst_crs, src.width, src.height, *src.bounds)
            kwargs = src.meta.copy()
            kwargs.update({
                'crs': dst_crs,
                'transform': transform,
                'width': width,
                'height': height,
                'dtype': 'float32',
                'bbox': src.bounds
            })
            new_fname = '4326_{}'.format(self.fname)
            with rasterio.open(new_fname, 'w', **kwargs) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=dst_crs,
                        resampling=Resampling.nearest)

        src = rasterio.open(new_fname)
        out_image = src.read(1)
        out_image = out_image.astype(np.float32)
        out_image[out_image == src.nodata] = 'nan'
        out_meta = src.meta.copy()
        #out_meta.update({"offset": src.offsets[0],
        #                "scale": src.scales[0]})

        if self.masking == True:
            with fiona.open(self.geometry, "r") as shapefile:
                features = [feature["geometry"] for feature in shapefile]
            out_image, out_transform = mask(src, features, crop=True)
            out_image = out_image.astype(np.float32)
            out_image[out_image == src.nodata] = 'nan'
            out_image = out_image[0,:,:]
            out_meta = src.meta.copy()
            out_meta.update({"driver": "GTiff",
                            "height": out_image.shape[0],
                            "width": out_image.shape[1],
                            "transform": out_transform,
                            "bbox": src.bounds})

        with rasterio.open(self.fname, 'w', **out_meta) as dst:
            dst.write_band(1, out_image)

        if self.netcdf_out == True:
            da = xr.open_rasterio(self.fname)
            da.to_netcdf('{}.nc'.format(self.fname[:-4]))

        if self.xarray_out == True:
            da = xr.open_rasterio(self.fname)

            return da, out_meta

        return out_image, out_meta

class getImageSentinel5p:
    def __init__(self, endpoint, collection, time_t, min_lat = -90, max_lat = 90, min_long = -180, max_long = 180, token = 'None', geometry = 'None', masking = False, fname = 'image.tif', mgrs_tile = 'None', scale = 1, xarray_out = False, netcdf_out = False):
        self.endpoint = endpoint
        self.collection = collection
        #self.geometry = geometry
        self.min_lat = min_lat
        self.max_lat = max_lat
        self.min_long = min_long
        self.max_long = max_long
        self.time_t = time_t
        self.token = token
        self.geometry = geometry
        self.masking = masking
        self.fname = fname
        self.mgrs_tile = mgrs_tile
        self.scale = scale
        self.xarray_out = xarray_out
        self.netcdf_out = netcdf_out
        #self.output_format = output_format

    def get_data(self):

        if self.masking == True:
            df = gpd.read_file(self.geometry)
            geom = df['geometry'][0]
            if self.mgrs_tile != 'None':
                url = "https://{}/wcs?service=WCS&Request=GetCoverage&version=2.0.0&subset=unix({})&format=image/tiff&filter=false&CoverageId={}&subset=Lat({},{})&subset=Long({},{})&token={}&scale={}&mgrs_tile={}".format(self.endpoint,self.time_t,self.collection, geom.bounds[1]-1, geom.bounds[3]+1, geom.bounds[0]-1, geom.bounds[2]+1, self.token, self.scale,self.mgrs_tile)
            else:
                url = "https://{}/wcs?service=WCS&Request=GetCoverage&version=2.0.0&subset=unix({})&format=image/tiff&filter=false&CoverageId={}&subset=Lat({},{})&subset=Long({},{})&token={}&scale={}&nodata=9969209968386869046778552952102584320".format(self.endpoint,self.time_t,self.collection, geom.bounds[1], geom.bounds[3], geom.bounds[0], geom.bounds[2], self.token, self.scale)

        else:
            if self.mgrs_tile != 'None':
                url = "https://{}/wcs?service=WCS&Request=GetCoverage&version=2.0.0&subset=unix({})&format=image/tiff&filter=false&CoverageId={}&subset=Lat({},{})&subset=Long({},{})&token={}&scale={}&mgrs_tile={}".format(self.endpoint,self.time_t,self.collection, self.min_lat, self.max_lat, self.min_long, self.max_long, self.token, self.scale, self.mgrs_tile)
            else:
                url = "https://{}/wcs?service=WCS&Request=GetCoverage&version=2.0.0&subset=unix({})&format=image/tiff&filter=false&CoverageId={}&subset=Lat({},{})&subset=Long({},{})&token={}&scale={}&nodata=9969209968386869046778552952102584320".format(self.endpoint,self.time_t,self.collection, self.min_lat, self.max_lat, self.min_long, self.max_long, self.token, self.scale)

        # if self.mgrs_tile != 'None':
        #     url = "https://{}/wcs?service=WCS&Request=GetCoverage&version=2.0.0&subset=unix({})&format=image/tiff&CoverageId={}&subset=Lat({},{})&subset=Long({},{})&token={}&mgrs_tile={}&filter=false".format(self.endpoint,self.time_t,self.collection, self.min_lat, self.max_lat, self.min_long, self.max_long, self.token, self.mgrs_tile)
        # else:
        #     url = "https://{}/wcs?service=WCS&Request=GetCoverage&version=2.0.0&subset=unix({})&format=image/tiff&CoverageId={}&token={}&mgrs_tile={}&filter=false".format(self.endpoint,self.time_t,self.collection, self.token, self.mgrs_tile)

        #print(url)
        result = requests.get(url)
        with open(self.fname, 'wb') as f:
            f.write(result.content)
            f.close()


        #if image is sentinel2 tiled transform to EPSG:4326


        src = rasterio.open(self.fname)
        out_image = src.read(1)
        out_image = out_image.astype(np.float32)
        out_image[out_image == src.nodata] = 'nan'
        out_image[out_image > 1000] = 0
        out_image[out_image < 0] = 0
        out_image[out_image == 0] = 'nan'
        out_meta = src.meta.copy()
        out_meta.update({"bbox": src.bounds})


        if self.masking == True:
            with fiona.open(self.geometry, "r") as shapefile:
                features = [feature["geometry"] for feature in shapefile]
            out_image, out_transform = mask(src, features, crop=True)
            out_image = out_image.astype(np.float32)
            out_image[out_image == src.nodata] = 'nan'
            out_image[out_image > 1000] = 0
            out_image[out_image < 0] = 0
            out_image[out_image == 0] = 'nan'
            out_image = out_image[0,:,:]
            out_meta = src.meta.copy()
            out_meta.update({"driver": "GTiff",
                            "height": out_image.shape[0],
                            "width": out_image.shape[1],
                            "transform": out_transform})

            new_dataset = rasterio.open(self.fname, 'w', **out_meta)

            new_dataset.write(out_image, 1)
            new_dataset.close()

        if self.netcdf_out == True:
            da = xr.open_rasterio(self.fname)
            da.to_netcdf('{}.nc'.format(self.fname[:-4]))

        if self.xarray_out == True:
            da = xr.open_rasterio(self.fname)

            return da, out_meta

        return out_image, out_meta


class getTimeSeries:
    def __init__(self, endpoint, collection, time_t, lat, long, token = 'None', mgrs_tile = 'None'):
        self.endpoint = endpoint
        self.collection = collection
        self.time_t = time_t
        self.lat = lat
        self.long = long
        self.token = token
        self.mgrs_tile = mgrs_tile

    def get_data(self):
        url = 'https://{}/wcs?service=WCS&Request=GetCoverage&version=2.0.0&subset=unix({})&format=application/xml&CoverageId={}&subset=Lat({})&subset=Long({})&filter=false&token={}&mgrs_tile={}'.format(self.endpoint, self.time_t, self.collection, self.lat, self.long, self.token, self.mgrs_tile)
        result = requests.get(url)
        xml_data = result.text

        try:
            tree = ET.fromstring(xml_data)
        except:
            print('No data was available for ', time_t)
            #print(url)
            print(result,'\n\n')
            return [],[]

        for t in tree.iter('{http://www.opengis.net/gml/3.2}lowerCorner'):
            # split string into list of coordinates
            time_delta = t.text.split()
            time_delta = time_delta[2]

        for t in tree.iter('{http://www.opengis.net/gml/3.2}tupleList'):
            # split string into list temps
            data = t.text
            #print(dates)
        #split
        data = data.split()
        #split again
        data = data[0].split(',')

        data = np.array(data).astype(float)


        for t in tree.iter('{http://www.opengis.net/gml/3.3/rgrid}coefficients'):
            # extract dates
            dates = t.text

        #print(data_mean)
        times = []
        dates = dates.split()

        for i in range(0,len(dates)):
            dates[i] = int(dates[i]) + int(time_delta)

        for i in range(0,len(dates)):
            times.append(datetime.fromtimestamp(int(dates[i])).strftime('%Y-%m-%dT%H:%M'))

        return data, times

class getAnimation:
    def __init__(self, endpoint, collection, start_date, end_date, min_lat = -90, max_lat = 90, min_long = -180, max_long = 180, token = 'None', geometry = 'None', masking = False, frame_duration = 0.1, legend = False):
        self.endpoint = endpoint
        self.collection = collection
        #self.geometry = geometry
        self.min_lat = min_lat
        self.max_lat = max_lat
        self.min_long = min_long
        self.max_long = max_long
        self.start_date = start_date
        self.end_date = end_date
        self.token = token
        self.geometry = geometry
        self.masking = masking
        self.frame_duration = frame_duration
        self.legend = legend

        #self.output_format = output_format


    def get_data(self):

        def daterange(start_date, end_date):
            for n in range(int ((end_date - start_date).days)):
                yield start_date + timedelta(n)

        filenames = []
        for single_date in daterange(self.start_date, self.end_date):
            time_t = '{}T00:00:00,{}T23:59:59'.format(single_date,single_date)
            url = "https://{}/wcs?service=WCS&Request=GetCoverage&version=2.0.0&subset=unix({})&format=image/tiff&CoverageId={}&subset=Lat({},{})&subset=Long({},{})&token={}".format(self.endpoint,time_t,self.collection, self.min_lat, self.max_lat, self.min_long, self.max_long, self.token)
            #print(url)
            result = requests.get(url)
            if not os.path.exists('temp'):
                os.makedirs('temp')
            fname = 'temp/{}.tif'.format( time_t)


            with open(fname, 'wb') as f:
                f.write(result.content)
                f.close()

            src = rasterio.open(fname)
            out_image = src.read(1)
            out_meta = src.meta.copy()
            out_image = out_image.astype(float)
            out_image[out_image == src.nodata] = 'nan'

            if self.masking == True:
                with fiona.open(self.geometry, "r") as shapefile:
                    features = [feature["geometry"] for feature in shapefile]
                out_image, out_transform = mask(src, features, crop=True)
                out_image = out_image.astype(float)
                out_image[out_image == src.nodata] = 'nan'
                out_image = out_image[0,:,:]
                out_meta = src.meta.copy()
                out_meta.update({"driver": "GTiff",
                                "height": out_image.shape[0],
                                "width": out_image.shape[1],
                                "transform": out_transform})

            plt.subplots(figsize=(13,13))
            plt.imshow((out_image[:,:]))
            plt.title('{} | {}'.format(self.collection,time_t.split(',')[0]), size=20)
            plt.axis('off')
            if self.legend == True:
                plt.colorbar()

            plt.savefig('{}'.format(fname[:-4]))
            plt.close()
            filenames.append('{}.png'.format(fname[:-4]))

        if not os.path.exists('gifs'):
            os.makedirs('gifs')

        gif_fname = 'gifs/{}_{}.gif'.format(self.collection, time_t.split(',')[0])

        images = [imageio.imread(f) for f in filenames]
        imageio.mimsave(gif_fname, images, duration=self.frame_duration)
        # with imageio.get_writer(gif_fname, mode='I', duration = 5) as writer:
        #     for filename in filenames:
        #         image = imageio.imread(filename)
        #         writer.append_data(image)

        shutil.rmtree('temp')

        return gif_fname



class getAnimation_paral:
    def __init__(self, endpoint, collection, start_date, end_date, min_lat = -90, max_lat = 90, min_long = -180, max_long = 180, token = 'None', geometry = 'None', masking = False, frame_duration = 0.1, legend = False):
        self.endpoint = endpoint
        self.collection = collection
        #self.geometry = geometry
        self.min_lat = min_lat
        self.max_lat = max_lat
        self.min_long = min_long
        self.max_long = max_long
        self.start_date = start_date
        self.end_date = end_date
        self.token = token
        self.geometry = geometry
        self.masking = masking
        self.frame_duration = frame_duration
        self.legend = legend

    def get_data(self):

        def download_thread(q, progress, d, collection = self.collection, start_date = self.start_date, end_date=self.end_date, min_lat=self.min_lat, max_lat=self.max_lat, min_long=self.min_long, max_long=self.max_long, token=self.token, geometry=self.geometry, masking= self.masking, frame_duration = self.frame_duration, legend = self.legend):
            while not q.empty():
                if q.unfinished_tasks == q.qsize():
                    progress.value += 1
                key, dateString = q.get()
                download_data(dateString, self.collection, self.min_lat, self.max_lat, self.min_long, self.max_long, self.token, self.geometry, self.masking)
                #d[key] = [dates,data]
                q.task_done()
                progress.value += 1

        def retreiveData(collection = self.collection, start_date = self.start_date, end_date=self.end_date, min_lat=self.min_lat, max_lat=self.max_lat, min_long=self.min_long, max_long=self.max_long, token=self.token, geometry=self.geometry, masking= self.masking, frame_duration = self.frame_duration, legend = self.legend):
            try:
                os.mkdir('cache')
            except:
                pass


            # Retreive data
            print('Retreiving data, please wait ...')
            #access_token = connect_to_server()

            startDate = self.start_date
            lastDate = self.end_date
            dataDict = {}
            q = Queue(maxsize=0)

            while startDate < lastDate:
                dateString = '{},{}'.format(datetime.strftime(startDate,'%Y-%m-%dT%H:%M:%S'),
                                   datetime.strftime(startDate + relativedelta(days=1),'%Y-%m-%dT%H:%M:%S'))
                key = (startDate.year,startDate.month)
                q.put((key,dateString))
                startDate += relativedelta(days=1)

            # Putting query urls in a queue
            progress = IntProgress(min=0, max=q.qsize())
            #display(progress)

            # Retreive data for maximum 40 queries at a time
            for i in range(10):
                process = threading.Thread(target=download_thread, args=(q, progress, dataDict, self.collection, self.min_lat, self.max_lat, self.min_long, self.max_long, self.token, self.geometry, self.masking, self.frame_duration, self.legend))
                process.setDaemon(True)
                process.start()

            q.join()

        def download_data(time_t, collection, min_lat, max_lat, min_long, max_long, token, geometry, masking):
            times=[]
            data_mean = []
            filenames = []
            #We create the URL with the request. Note that the parameters inside the "format" function at the end of the
            #URL will fill the {} in order.
            url = 'https://wcs-eo4sdcr.adamplatform.eu/wcs?service=WCS&Request=GetCoverage&version=2.0.0&subset=unix({})&format=image/tiff&CoverageId={}&subset=Lat({},{})&subset=Long({},{})'.format(time_t, self.collection, self.min_lat, self.max_lat, self.min_long, self.max_long)
            #Once the url is build, we can send a request to the server
            fname = 'cache/{}.tif'.format(time_t)
            result = requests.get(url)
            with open(fname, 'wb') as f:
                f.write(result.content)
                f.close()

        def create_pngs():

            files = glob.glob("cache/*.tif")

            for fname in files:
                try:
                    src = rasterio.open(fname)
                    out_image = src.read(1)
                    out_meta = src.meta.copy()
                    out_image[out_image == src.nodata] = 'nan'

                    if self.masking == True:
                        with fiona.open(self.geometry, "r") as shapefile:
                            features = [feature["geometry"] for feature in shapefile]
                        out_image, out_transform = mask(src, features, crop=True)
                        out_image[out_image == src.nodata] = 'nan'
                        out_image = out_image[0,:,:]
                        out_meta = src.meta.copy()
                        out_meta.update({"driver": "GTiff",
                                        "height": out_image.shape[0],
                                        "width": out_image.shape[1],
                                        "transform": out_transform})

                    plt.subplots(figsize=(13,13))
                    plt.imshow((out_image))
                    plt.title('{}'.format(fname[:-4].split(',')[-1]), size=20)
                    plt.axis('off')
                    plt.savefig('{}'.format(fname[:-4]))
                    plt.close()
                    filename = '{}.png'.format(fname[:-4])
                except:
                    pass

            files_png = glob.glob("cache/*.png")


            return sorted(files_png)

        def create_gifs(filenames):
            if not os.path.exists('gifs'):
                    os.makedirs('gifs')

            gif_fname = 'gifs/test.gif'

            images = [imageio.imread(f) for f in filenames]
            imageio.mimsave(gif_fname, images, duration=0.5)
            shutil.rmtree('cache')

            return gif_fname

        retreiveData(self.collection, self.start_date, self.end_date, self.min_lat, self.max_lat, self.min_long, self.max_long, self.token, self.geometry, self.masking, self.frame_duration, self.legend)
        filenames = create_pngs()
        gif_fname = create_gifs(filenames)

        return gif_fname
