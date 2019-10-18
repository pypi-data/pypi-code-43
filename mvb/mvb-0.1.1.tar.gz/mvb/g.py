import re

def camel_case_split(camel_case_str):
    return re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', camel_case_str)).split()

def list_to_sql_clause(l):
    s = ",".join(list(map(lambda s: f"'{s}'",l)))
    return f"({s})"

def take_middle_n(l,n):
    """
    Take middle n elements from list l
    
    @input l: list of elements
    @input n: int number of elements to select
    
    @returns: list of elements
    """
    s = math.ceil((len(l)-n)/2)
    e = math.ceil((len(l)+n)/2)
    return l[s:e]

def merge_lists(ll):
    """
    Merge a list of lists into one flat list
    [[a,b],[c,d],[e,f]] => [a,b,c,d,e,f]
    
    @input ll: list of lists
    
    @returns: list
    """
    return [i for l in ll for i in l] 
    
def dict_to_file_name(d):
    """
    Creates a file name by concatenating dict into string for file name
    key1=value1.key2=value2
    
    @input d: dict of key value pairs
    
    @returns: string representing dict for file naming
    """
    return ".".join(list(map(lambda i: f"{i[0]}={i[1]}",d.items())))


def str_to_dict(s,kv_delim='=',item_delim='&'):
    """
    Takes a string and returns a dict representing the key value pairs in the string
    
    @input s: string to extract values from
    @input kv_delim: delimiter between keys and values, default '=' 
    @input item_delim: delimiter between items (key value pairs), default '&'
        
    @returns: dict representing key value pairs from string
    """
    d = {a[0]:a[1] for a in list(map(lambda s: s.split(kv_delim),s.split(item_delim))) if len(a) > 1}
    return d

