import re
import codecs
from datetime import datetime


def log_process(filename,column):
    """
    input: 
        column name : 'ip','Session', 'datetime','address','status','size', and 'protocol'
        file name
    output: 
        list of column value
    """
    fmt = '%Y-%m-%d %H:%M:%S'
    result = []
    p = re.compile('([^ ]*) ([^ ]*) ([^ ]*) %? \[([^]]*)\] "([^"]*)" ([^ ]*) ([^ ]*)')
    with codecs.open(filename,'r',encoding='utf-8', errors='ignore') as f:
        file = f.readlines()
    for line in file:
        line = line.replace('\n','')
        try:
            m = p.match(line)
            host, ignore, user, date , request, status, size = m.groups()
            datetime_this = datetime.strptime(date[:20], '%d/%b/%Y:%H:%M:%S').strftime(fmt)
            if "http://" in request:
                index_of_web = request.find("http://")
                address_this = request[index_of_web:].replace(' HTTP/1.1','')
                protocol_this = request[:index_of_web]            
            else:
                index_of_web = request.find("https://")
                address_this = request[index_of_web:].replace(' HTTP/1.1','')
                protocol_this = request[:index_of_web] 
            status_this = status
            size_this = size
            data = {'ip':host,'session':user,'datetime': datetime_this,'address': address_this,'status': status_this,'size' : size_this,'protocol' : protocol_this}
            result.append(data[column])
        except:
            pass
    return result
