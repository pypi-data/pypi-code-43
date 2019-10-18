# change_point_detection function's assertions
# assert that the df_column is a list, the length is greater than 4
assert(isinstance(df_column,list) and len(df_column)>4 )
# assert all values in df_column are integers or floats and not nan nor infinities
assert(np.sum([not (np.isreal(x) and np.isfinite(x)) for x in df_column])==0)
# assert the length_of_interval is greater than 0 and is an integer
assert(isinstance(length_of_interval,int) and length_of_interval>=4 and length_of_interval%2==0)
# assert the specified_confidence_level is between 0 and 1
assert(specified_confidence_level<1 and specified_confidence_level>0)
# assert niterations is greater than or equal to 10 and is an integer
assert(isinstance(niterations,int) and niterations>=10)
# assert acc is boolean
assert(isinstance(acc,bool))
# assert rank is boolean
assert(isinstance(rank,bool))


# change_points function's assertions
# assert that the column is a list, the length is greater than 4
assert(isinstance(column,list) and len(column)>4 )
# assert all values in column are integers or floats and not nan nor infinities
assert(np.sum([not (np.isreal(x) and np.isfinite(x)) for x in column])==0)
# assert the specified_confidence_level is between 0 and 1
assert(specified_confidence_level<1 and specified_confidence_level>0)
# assert niterations is greater than or equal to 10 and is an integer
assert(isinstance(niterations,int) and niterations>=10)
# assert acc is boolean
assert(isinstance(acc,bool))
# assert rank is boolean
assert(isinstance(rank,bool))


# bit_depth_change function's assertions
# assert that the df_column is a list, the length is greater than 4
assert(isinstance(df_column,list) and len(df_column)>4 )
# assert all values in df_column are integers or floats and not nan nor infinities
assert(np.sum([not (np.isreal(x) and np.isfinite(x)) for x in df_column])==0)
# assert that the change_point_indices is a list, the length is greater than or equal to 2
assert(isinstance(change_point_indices,list) and len(change_point_indices)>=2 )
# assert the p_threshhold is between 0 and 1
assert(p_threshhold<1 and p_threshhold>0)
# assert the avg_threshhold is greater than or equal to 0
assert(avg_threshhold>=0)


# direction_smoother function's assertions
# assert that the direction_column is a list
assert(isinstance(direction_column,list) )
# assert all values in direction_column are -1, 0, or 1
assert(np.sum([not (x in [-1,0,1]) for x in direction_column])==0)
# assert secs is greater than or equal to 10 and is an integer
assert(isinstance(secs,int) and secs>=0)


# change_point_loop function's assertions
# assert that the direction_column is a list
assert(isinstance(direction_column,list) )
# assert all values in direction_column are -1, 0, or 1
assert(np.sum([not (x in [-1,0,1]) for x in direction_column])==0)
# assert that the df_column is a list, the length is greater than 4
assert(isinstance(df_column,list) and len(df_column)>4 )
# assert all values in df_column are integers or floats and not nan nor infinities
assert(np.sum([not (np.isreal(x) and np.isfinite(x)) for x in df_column])==0)
# assert the scl is between 0 and 1
assert(scl<1 and scl>0)
# assert niter is greater than or equal to 10 and is an integer
assert(isinstance(niter,int) and niter>=10)
# assert acc is boolean
assert(isinstance(acc,bool))
# assert rank is boolean
assert(isinstance(rank,bool))
# assert the p_thresh is between 0 and 1
assert(p_thresh<1 and p_thresh>0)
# assert the avg_thresh is greater than or equal to 0
assert(avg_thresh>=0)


# final_direction function's assertions
# assert that the direction_column is a list
assert(isinstance(direction_column,list) )
# assert all values in direction_column are -1, 0, or 1
assert(np.sum([not (x in [-1,0,1]) for x in direction_column])==0)
# assert that the df_column is a list, the length is greater than 4
assert(isinstance(df_column,list) and len(df_column)>4 )
# assert all values in df_column are integers or floats and not nan nor infinities
assert(np.sum([not (np.isreal(x) and np.isfinite(x)) for x in df_column])==0)
# assert the p_threshhold is between 0 and 1
assert(p_threshhold<1 and p_threshhold>0)
# assert the avg_threshhold is greater than or equal to 0
assert(avg_threshhold>=0)



