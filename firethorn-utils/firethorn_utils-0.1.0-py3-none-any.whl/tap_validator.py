'''
Created on Jul 17, 2018

@author: stelios
'''

try:
    
    import urllib.request
    import firethorn
    import json    
    import os
    from firethorn.models.resource import Resource
    from firethorn.models.adql.adql_resource import AdqlResource 
    import sys
    import uuid
    import time
    from argparse import ArgumentParser
    from .util import Utility
    import concurrent.futures
    import urllib.parse
    import random
    import firethorn.tap.voQuery as voQuery
except Exception as e:
    print (e)
    #logging.exception(e)



class ValidatorResults(object):
    '''
    Validator Results Class, stores information from a validation run
    '''

    def __init__(self, processed, candidates, exceptions, total_time = 0):
        '''
        Constructor
        '''
        self.processed = processed
        self.candidates = candidates
        self.exceptions = exceptions
        self.total_time = 0

        return


    @property
    def processed(self):
        return self.__processed
        
        
    @processed.setter
    def processed(self, processed):
        self.__processed = processed


    @property
    def candidates(self):
        return self.__candidates


    @candidates.setter
    def candidates(self, candidates):
        self.__candidates = candidates


    @property
    def exceptions(self):
        return self.__exceptions


    @exceptions.setter
    def exceptions(self, exceptions):
        self.__exceptions = exceptions


    @property
    def total_time(self):
        return self.__total_time


    @total_time.setter
    def total_time(self, total_time):
        self.__total_time = total_time





class TAPValidator(object):
    '''
    Validator class, used to validate an AdqlResource via TAP queries
    '''


    def __init__(self, firethorn_object , verbose):
        '''
        Constructor
        '''
        self.firethorn_object = firethorn_object
        self.verbose = True
        return
     

    def format_name(self, name):
        keywords=[
            "first",
            "diagnostics",
            "match",
            "region",
            "zone",
            "timestamp",
            "coord2",
            "coord1",
            "size",
            "min",
            "max",
            "match",
            "zone",
            "time",
            "distance",
            "value",
            "sql",
            "first",
            "date",
            "area",
            "key",
            "count",
            "when"
            ]
        if (name.lower() in keywords):
            return '"' + name + '"'
        else:
            return name


    def validate (self, resource_url, resource_tap_url, mode="async"):
        '''
        Validate an Adql Resource, Check all tables by querying and checking result row count
        '''

        start_time = time.time()
        print ("--- Starting validation on Resource: " + resource_url + "---")

        acc = self.firethorn_object.identity()

        resource = Resource(
            adql_resource = AdqlResource(
                account = acc,
                url = resource_url,
                )
            )
    
        #
        # Iterate the catalog/schema/tables tree querying each and
        # building a list of candidates where the result rowcount
        # is less than expected. 
    
        processed = dict()
        candidates = dict()
        exceptions =  dict()
    
        for schema in resource.get_schemas():
            for table in schema.get_tables():
                start_time_table = time.time()
                fullname = self.format_name(schema.name()) + "." + self.format_name(table.name())
                if (self.verbose):
                    print(
                        "Testing [{}]".format(
                            fullname
                            )
                        )
                try:

                    query_str = "SELECT TOP 5 * FROM {}.{}".format(
                        self.format_name(schema.name()),
                        self.format_name(table.name())
                        )



                    sync_base_url = resource_tap_url + "/sync?QUERY=" + query_str 
                    sync_params = "&REQUEST=doQuery&LANG=ADQL&FORMAT=VOTABLE"

                    voqry = voQuery.VOQuery(endpointURL=resource_tap_url, query=query_str, mode=mode)
                    voqry.run()

                    #query_obj = resource.query(
                    #    query_str
                    #    )


                    #py_table = query_obj.results().as_astropy()
                    #py_table.pprint()
                    rowcount = voqry.rowcount()
                    processed[fullname] = rowcount

                    print ("Rowcount:" + str(rowcount))
                    if (rowcount < 10 and rowcount>=0):
                        candidates[fullname] = rowcount
                        if (self.verbose=='True'):
                            print(
                                "Candidate [{}] [{}]".format(
                                    fullname,
                                    rowcount
                                    )
                                )
                    if (rowcount<0):
                        if (voqry.get_error()!=None):
                            raise Exception(voqry.get_error())
                        else:
                            raise Exception("Unknown Exception")
                        raise Exception(voqry.get_error())

                except Exception as e:
                    #logging.exception(e)
                    message = sys.exc_info()[0]
                    print (message)
                    exceptions[fullname] = str(e)
                    if (self.verbose=='True'):
                        print(
                           "Exception [{}] [{}]".format(
                                fullname,
                                message
                                )
                            )
                    print (exceptions)

                total_time_table = time.time() - start_time_table
                print ("Table query completed after %s seconds" % (total_time_table))

        total_time = time.time() - start_time 
        print("--- Validation completed after  %s seconds ---" % (total_time))
       
        return  ValidatorResults(candidates=candidates, processed=processed, exceptions=exceptions, total_time=total_time)



def main():

    '''
    Validator Arguments
    '''
    parser = ArgumentParser()
    parser.add_argument("-ft", "--firethorn_url", dest="firethorn_url",
                    help="Firethorn Instance URL", metavar="FIRETHORN")
    parser.add_argument("-r", "--resource_id", dest="resource_id",
                    help="Resource ID", metavar="RESOURCE")
    parser.add_argument("-u", "--username", dest="username",
                    help="Firethorn username", metavar="USERNAME")
    parser.add_argument("-p", "--pass", dest="password",
                    help="Firethorn password", metavar="PASSWORD")
    parser.add_argument("-g", "--group", dest="group",
                    help="Firethorn group", metavar="GROUP")
    parser.add_argument("-v", "--verbose", dest="verbose", 
                    help="Print status messages to stdout")
    parser.add_argument("-from", "--from", dest="from_email",
                    help="Email from which to send Validation email", metavar="FROM")
    parser.add_argument("-to", "--to", dest="to_email",
                    help="Email to which to send Validation email", metavar="TO")
    parser.add_argument("-m", "--mode", dest="mode",
                    help="TAP query mode (sync|async)", metavar="MODE")

    args = parser.parse_args()    


    ft = firethorn.Firethorn(endpoint=args.firethorn_url)
    ft.login(args.username, args.password, args.group)

    validator_obj = TAPValidator(ft, args.verbose)
    validator_results = validator_obj.validate(args.firethorn_url + "/adql/resource/"  + args.resource_id, args.firethorn_url + "/tap/"  + args.resource_id, mode=args.mode)
    

    print ("Processed: ")
    print (validator_results.processed)
    print ("------------")
 
    print ("Candidates: ")
    print (validator_results.candidates)
    print ("------------")


    print ("Exceptions: ")
    print (validator_results.exceptions)
    print ("------------")

    '''
    Send exceptions by email
    '''
    print(validator_results.exceptions)
    if ((len(validator_results.exceptions)>0) and (args.from_email!=None) and (args.to_email!=None)):
        print ("Sending email with exceptions to: " + args.to_email)
        Utility.sendMail(args.from_email, args.to_email, "Validation Results - Database Exeptions", json.dumps(validator_results.exceptions))

if __name__ == "__main__":
    main()



