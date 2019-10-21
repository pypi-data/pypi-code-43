# test_2()
	# test_1()
	# mgr=Manager(host='94.247.135.91',username='docker',password='docker',port='8086')
	# with mgr.session_context():
	# 	a: MainRequest=mgr.session.query(MainRequest).first()
	# 	# print(to_shape(a.cadastre_value))
	# 	print(a.cadastre_value)
	# 	mgr.session.add(SridTest(geom=gmtr.SpatialGeom(to_shape(a.cadastre_value)).convert_crs(4326,3857).geom_obj))
	#
	#
	# return
	# mgr=Manager(host='94.247.135.91',username='docker',password='docker',port='8086')

	# s2_info.priority=136
	# print(s2_info)

	# mgr.s2_info: Sentinel2_Info=s2_info
	# print(mgr.s2_info.priority)
	# mgr.s2_info.priority=136
	# print(mgr.s2_info.priority)
	# print(mgr.s2_info)
	# s2_info=mgr.session.query(Sentinel2_Info).filter(Sentinel2_Info.priority==36).first()