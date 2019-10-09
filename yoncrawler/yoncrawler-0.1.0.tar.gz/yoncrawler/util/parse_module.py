from yoncrawler.util.logger import getMyLogger

def clean(text):
    return text.replace('\r', '').replace('\n', '').replace('\t', '').strip()

def table_parser(table, prepocessing=lambda x:x, clean_text=True):
    mylogger = getMyLogger()
    table = prepocessing(table)
    tablelist = table.find_all('tr')
    col_names = [col.text for col in tablelist[0].find_all('th')]
    col_names.append('href')
    rows = tablelist[1:]

    def row_parse(row):
        try:
            if clean_text:
                values = [clean(tr.text)
                    for tr in row.find_all('td')]
            else:
                values = [tr.text for tr in row.find_all('td')] 
            values.append(row.find('a')['href']) 
            row_dict = dict() 
            
            for key, val in zip(col_names, values):
                row_dict[key] = val
            
            return row_dict
        except Exception as e:
            mylogger.warning(e)
            return None

    data = list(map(row_parse, rows))

    return data
