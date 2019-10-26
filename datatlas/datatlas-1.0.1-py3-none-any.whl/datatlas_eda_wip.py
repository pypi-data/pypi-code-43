
"""
[TITLE]
Author: Mei Yong
Updated Date: Sat Sep 21 15:28:52 2019

"""



import pandas as pd
df = pd.read_csv(r"C:\Users\shaom\Desktop\Machine_Learning\projects\data\titanic.csv")


def get_dtype_profile(df):
    
    import re
    
    dtype_regex_dict = {}
    
    for column in df:
        
        col = df[column]
        
        # Data prep for regex
        col.dropna(inplace=True) # Drop nulls
        col = col.astype(str).str.lower() # Lowercase
        col = col.str.replace(' ','') # Remove whitespace
        col = col.apply(lambda x: re.sub(r'[^\w\s]', '', x)) # Remove punctuation
        
        numeric_count, string_count, mixed_count = 0, 0, 0
        
        for item in col:
            
            item_len = len(item)
            
            # Find the number of alphabets in the string
            alphabet_find = re.findall(r"[a-zA-Z]+", item)
            try:
                alphabet_len = len(alphabet_find[0])
            except:
                alphabet_len = 0
            
            # Find the number of numbers in the string
            number_find = re.findall(r"[0-9]+", item)
            try:
                number_len = len(number_find[0])
            except:
                number_len = 0
            
            # Note the number of strings that are fully alphabets, fully numbers, or mixed
            if item_len == number_len:
                numeric_count += 1
            elif item_len == alphabet_len:
                string_count += 1
            else:
                mixed_count += 1
        
        
        dtype_regex_result = {'numeric': round(numeric_count/len(col) *100, 2)
                            ,'non-numeric': round(string_count/len(col) *100, 2)
                            ,'mixed': round(mixed_count/len(col) *100, 2)   
                            }
            
        dtype_regex_dict[column] = dtype_regex_result
    
    dtype_final = {}
    for column in dtype_regex_dict:
        d = dtype_regex_dict[column]
        dtype_final[column] = max(d, key=d.get)
    
    return dtype_regex_dict, dtype_final





dtype_detail, dtype_final = get_dtype_profile(df)

some_dict = {}
for column in dtype_profile:
    #print(column)
    d = dtype_profile[column]
    some_dict[column] = max(d, key=d.get)
    
    
    
    

# IDs and other checks
    
import re
    
further_regex_dict = {}
    
for column in df:
    
    col = df[column]
    
    
    # Data prep for regex
    col = col.astype(str).str.lower() # Lowercase
    col = col.str.replace(' ','') # Remove whitespace
    col = col.apply(lambda x: re.sub(r'[^\w\s]', '', x)) # Remove punctuation
    
    # If there are less than or equal to 3 distinct values, check if it's a yes/no column
    if col.nunique() <= 3:
        
        distinct_values = list(col.unique())
        count_yesno = 0

        for value in distinct_values:
            if re.search(r"^[y](es)?$|^[n][o]?$|^[t](rue)?$|^[f](alse)?$|(nan)|^[0-1]{1}[0]?$", value):
                count_yesno += 1
                
        if col.nunique() == count_yesno:
            further_regex_dict[column] = "Likely_yesno"
    
    # If there are more distinct values, check if it's an ID        
    else:
        pass

    
    
    
    





### If column is a date column, convert it to datetime format
for column in sfPermitsClean:
    if 'date' in column:
        sfPermitsClean[column] = pd.to_datetime(sfPermitsClean[column], errors='coerce')
        
        ### Formatting datetime
import datetime
ex_date_1 = "01-03-2019"
ex_date_2 = datetime.datetime.strptime(ex_date_1, "%d-%m-%Y")

In [140]: datetime.datetime.strptime("11/12/98","%m/%d/%y")
Out[140]: datetime.datetime(1998, 11, 12, 0, 0)

In [141]: datetime.datetime.strptime("11/12/98","%d/%m/%y")
Out[141]: datetime.datetime(1998, 12, 11, 0, 0)

In [143]: date.year
Out[143]: 1998

In [144]: date.month
Out[144]: 11

In [145]: date.day
Out[145]: 12

        
        ### Count up the labels and group
        
        ### If more than 1 group, output 'Warning: Mixed types {'string':10%, 'numeric':90%}
        
        ### Note the most commonly occuring label
        
        ### If most values look like numerics BUT the auto-detected type is string, then warning should be numeric
        
        ### If most values look like strings BUT the auto-detected type is numeric, then warning should be string (this will likely never be triggered)
        
        
        
        
        
        
                
        ### ID check
        ### Check for sequential score
        ### Check for repeated value score - mask then group then average where zero is means more repeated values and one means less repeated values and closer to zero is more likely to be an ID
        ### Check for Benford's law - basically if the values start with the same number or set of numbers
            
        ### y/n check
        ### Convert to string (keep the NaNs)
        ### Check for common y/n values
            
        ### Date check
        ### Remove NaNs
        ### Convert to string
        ### Check regex and label
        ### Count up the labels
        ### If >60% date then date warning


        