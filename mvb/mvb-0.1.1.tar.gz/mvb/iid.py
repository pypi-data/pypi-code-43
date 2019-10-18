import re
iid_re = re.compile(r"(\d*\$\d*)")
def extract_iids(s):
    """
    Extracts instance ids from string
    
    @input s: string potentially containing instance ids
    
    @returns: list of instance ids from string
    """
    return iid_re.findall(s)

def categorize_iid(iid):
    """
    Takes an instance id, and returns the category of executable it represents
    
    @input iid: string containing the instance id of a workday executable
    
    @returns: string representing type of the executable {Report, Job, Web Service, Task}
    """
    if '1422$' in str(iid):
        return 'Report'
    elif '4297$' in str(iid):
        return 'Report'
    elif '4608$1510' in str(iid):
        return 'Report'
    elif '4608$1060' in str(iid):
        return 'Report'
    elif '3101$25' in str(iid):
        return 'Job'
    elif '4608$' in str(iid):
        return 'Job'
    elif '2996$' in str(iid):
        return 'Web Service'
    elif '5557$' in str(iid):
        return 'Web Service'
    else:
        return 'Task'
