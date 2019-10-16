# dat_src,dlayer=DataSet.from_array(digitized,ndvi_ds).polygonize('Memory','',
#                                                                 field_name=field_name)
# poly_collection=cleanup_polygons(dlayer,field_name,area_threshold=110,thresh_len=8)
# if 0 in poly_collection: poly_collection.pop(0)
# dat_src=dlayer=None
# #print(list(poly_collection.keys()))
# features=list()
# for cat_id,geoms in poly_collection.items():
# 	simple_logger.debug('cat_id: %s',cat_id)
# 	feat=geojson.Feature(id=cat_id,geometry=shg.MultiPolygon(geoms),
# 	                     properties=dict(DN=float(mean_vals[cat_id])))
# 	features.append(feat)
# feat_col=geojson.FeatureCollection(features,cad_num=spk.cad_land.name)
# geojson.dump(feat_col,open('arkan5_simplified_12.geojson','w'))



# print(get_group_cloudiness())
	# cad_info: Cadastres_Info=db_opers.SessionHelper(db_opers.Cadastres_Info).get_with_id(1380560,as_saved=True)
	# band_paths=list()
	# band_paths.append(
	# 	r'/home/lgblkb/PycharmProjects/Egistic/Downloaded_images/sentinel2/unzipped_scenes/S2B_MSIL2A_20180518T062629_N0206_R077_T42UUB_20180518T101322.SAFE/GRANULE/L2A_T42UUB_A006252_20180518T063426/IMG_DATA/R10m/T42UUB_20180518T062629_B04_10m.jp2')
	# band_paths.append(
	# 	r'/home/lgblkb/PycharmProjects/Egistic/Downloaded_images/sentinel2/unzipped_scenes/S2B_MSIL2A_20180518T062629_N0206_R077_T42UUB_20180518T101322.SAFE/GRANULE/L2A_T42UUB_A006252_20180518T063426/IMG_DATA/R10m/T42UUB_20180518T062629_B03_10m.jp2')
	# band_paths.append(
	# 	r'/home/lgblkb/PycharmProjects/Egistic/Downloaded_images/sentinel2/unzipped_scenes/S2B_MSIL2A_20180518T062629_N0206_R077_T42UUB_20180518T101322.SAFE/GRANULE/L2A_T42UUB_A006252_20180518T063426/IMG_DATA/R10m/T42UUB_20180518T062629_B02_10m.jp2')
	# no_data_value=0
	# p1=gsup.results_folder.create('test1').get_filepath('ndvi',ext='.tiff',include_datetime=True)
	# p2=gsup.results_folder.create('test1').get_filepath('ndvi_merged',ext='.tiff',include_datetime=True)
	# rgb_to_geotiff(p1,cutline_json=geojson.Feature(geometry=db_opers.to_shape(cad_info.geom)),*band_paths,no_data_value=no_data_value)
	# gsup.run_shell(gsup.gdal_merge_py,'-o',p2,'-n',str(no_data_value),'-a_nodata','nan',p1,with_popen=True)

	# np.random.seed(1)

	# val_ranges=[-1,0,0.033,0.066,0.1,0.133,0.166,0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.6,0.7,0.8,0.9,1]
	# simple_logger.debug('len(val_ranges): %s',len(val_ranges))

	# zero_catch_window=1e-9
	# val_ranges=[-1.01,-zero_catch_window,zero_catch_window,*np.linspace(zero_catch_window,1,12)]
	# mean_vals,digitized=categorize(ndvi_ds.array,val_ranges)
	# digitized*=digitized!=2
	# mean_vals.pop(2)
	# print(mean_vals)
	# print(len(mean_vals))
	# #digitized=remove_lonely_cats(digitized)
	# field_name='Category'
	# #DataSet.from_array(digitized,ndvi_ds).polygonize('geojson','arkan5_original_12.geojson',field_name=field_name)
	# contour_dsrc,contour_layer=ndvi_ds.generate_contours(val_ranges,'Memory','')
	# feats=process_vector_layer(contour_layer,100)
	# contour_dsrc=contour_layer=None
	# save_json_features(feats,'reduced_13',cad_num=cad_num)