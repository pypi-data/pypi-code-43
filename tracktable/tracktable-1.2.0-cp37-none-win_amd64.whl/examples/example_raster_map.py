from mpl_toolkits.basemap import Basemap
import osr, gdal
import pyproj
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from numpy import linspace
from numpy import meshgrid
import numpy as np

#################################################################################
def gdal_example(projWin = [-115.0, 40.0, -98.9, 30.86]):
    ds1 = gdal.Open('C:\\Users\\pbaxley\\Downloads\\HYP_LR_SR_OB_DR\\HYP_LR_SR_OB_DR.tif')
    #ds1 = gdal.Open('warp.tif')
    #ds2 = gdal.Warp('warp.tif',ds1, format='GTiff', srcSRS="epsg:4326", dstSRS="epsg:54032")
    ds2 = gdal.Warp('warp.tif',ds1, format='GTiff', srcSRS="epsg:4326", dstSRS="epsg:3857")
    #ds = gdal.Translate('output.tif', ds1, projWinSRS ="epsg:4326",  projWin = [-125.0, 46.0, -88.9, 25.86])
    ds = gdal.Translate('output.tif', ds2, outputSRS = 'epsg:3857', projWinSRS ="epsg:4326", projWin = projWin) #[-projwin ulx uly lrx lry]
    #ds = gdal.Translate('output.tif', ds1, outputSRS = 'epsg:54032', projWinSRS ="epsg:54032", projWin = [-8918927.75477855, 9901249.20364993, -7835923.94606816, 4309064.74473588]) #-130.487, 40.155  -79.036, 28.463
    
    data = ds.ReadAsArray()
    count = ds.RasterCount
    gt = ds.GetGeoTransform()
    proj = ds.GetProjection()
    cm1 = ds.GetRasterBand(1).GetRasterColorTable()
    cm2 = ds.GetRasterBand(2).GetRasterColorTable()
    cm3 = ds.GetRasterBand(3).GetRasterColorTable()
    
    xres = gt[1]
    yres = gt[5]

    # get the edge coordinates and add half the resolution 
    # to go to center coordinates
    xmin = gt[0] + xres * 0.5
    xmax = gt[0] + (xres * ds.RasterXSize) - xres * 0.5
    ymin = gt[3] + (yres * ds.RasterYSize) + yres * 0.5
    ymax = gt[3] - yres * 0.5

    #llproj = (xmin, ymin)
    #urproj = (xmax, ymax)
    x_center=(xmax+xmin)/2
    y_center=(ymax+ymin)/2
    
    ds = None

    inProj = pyproj.Proj(init='epsg:3857')
    #inProj = pyproj.Proj(init='epsg:4087')
    outProj = pyproj.Proj(init='epsg:4326')
    #x_center,y_center = pyproj.transform(inProj,outProj,x_center,y_center)
    #print(x_center,y_center)

    llproj = pyproj.transform(inProj,outProj,xmin,ymin)
    urproj = pyproj.transform(inProj,outProj,xmax, ymax)

    #################################################################################

    # Create the figure and basemap object
    fig = plt.figure(figsize=(8, 6))
    #m = Basemap(projection='aeqd', resolution='i', lon_0=-108.0, lat_0=35.0,
    #m = Basemap(epsg=3786, resolution='i',
    m = Basemap(epsg=3857, resolution='i',
    #            width=xmax-xmin,
    #            height=ymax-ymin)
                #llcrnrx=-88.9037,
                #llcrnry=25.873572,
                #urcrnrx=-125.062806,
                #urcrnry=45.9755498)
      #            llcrnrx=llproj[0],
    #            llcrnry=llproj[1],
    #            urcrnrx=urproj[0],
    #            urcrnry=urproj[1])
   # m = Basemap(epsg=4326, lon_0=x_center, lat_0=y_center, resolution='i',
                        llcrnrlon=llproj[0]-3,
                        llcrnrlat=llproj[1]-3,
                        urcrnrlon=urproj[0]+3,
                        urcrnrlat=urproj[1]+3)
  #                     llcrnrlon=llproj[0],
  #                      llcrnrlat=llproj[1],
  #                      urcrnrlon=urproj[0],
  #                      urcrnrlat=urproj[1])
  
    data[0] = np.flipud(data[0])

    #x = linspace(0, m.urcrnrx, data[0].shape[1])
    #y = linspace(0, m.urcrnry, data[0].shape[0])
    #x = linspace(xmin, xmax, data[0].shape[1])
    #y = linspace(ymin, ymax, data[0].shape[0])

    newxmin, newymax = m(projWin[0], projWin[1])
    newxmax, newymin = m(projWin[2], projWin[3])

    x = linspace(newxmin, newxmax, data[0].shape[1])
    y = linspace(newymin, newymax, data[0].shape[0])

    xx, yy = meshgrid(x, y)

    
    #extent = [xmin, xmax, ymin, ymax]
    extent = (newxmin, newxmax, newymin, newymax)
    
    # plot the data
    #image = mpimg.imread("output.tif")
    #m.imshow(image, origin='upper', extent = extent)
    m.bluemarble()
    #m.imshow(data[0], origin='lower', extent = extent, cmap=plt.cm.jet)
    #m.imshow(data[1], origin='upper', extent = extent)
    #m.imshow(data[2], origin='upper', extent = extent, cmap=cm3, alpha=.3)

    #m.pcolormesh(xx,yy,data[0],latlon=True,)
    m.pcolormesh(xx,yy,data[0],cmap=cm1)

    #m.pcolor(xx,yy,data[0,:,:])
    # annotate
    m.drawrivers(linewidth=.1,color='b')
    #m.drawstates()
    #m.drawcounties()
    #m.drawcountries()
    m.drawcoastlines(linewidth=.5)
    
    plt.savefig('southwest_na.png',dpi=600,transparent=True)

gdal_example()

