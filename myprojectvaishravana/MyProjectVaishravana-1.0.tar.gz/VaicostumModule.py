def recursiveprint(movieslist):
    for movies in movieslist:
        if isinstance(movies,list):
            recursiveprint(movies)    
        else:
            print(movies)        
 