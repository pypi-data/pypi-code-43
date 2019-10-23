from kyc.connection import Connection

def get_company(id=0,ban=""):
    if id==0:
        path = "report/company/ban/%s" % (ban)
    else:
        path = "report/company/%s" % (id)
        
    r = Connection.request('get', path)
    
    return r.json();
