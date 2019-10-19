import os                                                                       
from multiprocessing import Pool                                                

process_list = range(100)
	
def run_process(process_counter):                                                             
    print ("Starting RUN # " + str(process_counter))
    #os.system('python3 -c "import firethorn_utils.tap_validator as validator;validator.main()" -ft=http://tap.roe.ac.uk/firethorn -r=60 -u=chae1aixuh5exae5Udoh -p=EiB0shoegahfeWahx1ai -g=oowe1eedaeFei1tohtai -m=sync')                                       
    os.system('python3 -c "import firethorn_utils.tap_validator as validator;validator.main()" -ft=http://localhost:8081/firethorn -r=56 -u=Ohci9phe2Dahw3thoht8 -p=iejegahth1phohg5Phoo -g=goo8Doo0loo4chie8Xah -m=sync')                                       
    print ("Ended RUN # " + str(process_counter))


pool = Pool(processes=30)                                                        
pool.map(run_process, process_list)   
