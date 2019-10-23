from kyc.connection import Connection

def get_group(group_id):
    path = "report/group/%s" % (group_id)        
    r = Connection.request('get', path)
    
    return r.json();
