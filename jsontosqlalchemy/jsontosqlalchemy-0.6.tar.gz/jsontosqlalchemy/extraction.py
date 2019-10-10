#%%
# n_cell
# Imports
import numpy as np
from ast import literal_eval
#%%
class extraction:
    def pivot_extraction_keys(self, list):
        a = np.array(list)
        n = np.unique(a[:,1])
        return np.array( [ [i,a[a[:,1]==i,0],a[a[:,1]==i,2],a[a[:,1]==i,3],a[a[:,1]==i,4]] for i in n] )

    def extrac_parent(self, parent):
        z = parent.replace(',,',',')
        z = '[' + z + ']'
        z = z.replace('[,','[')
        z = z.replace(',]',']')
        z = literal_eval(z)
        leng = len(z)
        if leng == 1:
            return ''
        else:
            while not isinstance(z[leng-2],str):
                leng = leng-1 
            return z[leng-2]

    def extraction_keys(self, v, lista_claves=[], prefix='', table = '',parent = '',count=None,noid=False):
        if isinstance(v, dict):
            for k, v2 in v.items():
                p2 = '{}["{}"]'.format(prefix, k)
                parent2 = '{},"{}",'.format(parent, k)
                if isinstance(v2, dict):
                    # count = None
                    noid = False
                    lista_claves.append((prefix + '["' + str(k) + '"]',k,self.extrac_parent(parent + '"' + str(k) + '",'),str(count),noid))
                elif isinstance(v2, list) and len(v2)>0:
                    # print('v2[0]:', str(v2[0]))
                    # print('v2', str(v2))
                    noid = False
                    if isinstance(v2[0], (dict,list)):
                        # print('v2[0]:', str(v2[0]))
                        # print('v2[0] is list or dict')
                        pass
                        # lista_claves.append((prefix + "['" + str(k) + "']",k))
                    elif isinstance(v2[0], (str, int, float)):
                        # print('v2[0] is numer or str')
                        # print('v2:', str(v2))
                        v2 = self.convert_todict(v2)
                        # print(str(v2))
                        noid = True
                self.extraction_keys(v2, lista_claves, p2,table=k,parent=parent2,count=count,noid=noid) 
        elif isinstance(v, list):
            for i, v2 in enumerate(v):
                # print(parent,table,prefix)
                # print('--------------')
                p2 = "{}[{}]".format(prefix, i)
                parent2 = "{},{},".format(parent, i)
                if isinstance(v2, (dict,list)):                
                    count = i
                    lista_claves.append((prefix + "[" + str(i) + "]",table,self.extrac_parent(parent + ','),None,noid))
                self.extraction_keys(v2, lista_claves, p2,parent=parent2,count=count, noid=noid)
        else:        
            # if isinstance(v, list):
                # lista_claves.append(prefix)
            # print('{} = {}'.format(prefix, repr(v)))
            pass
        return lista_claves

    def iterate_over_json(self, skeleton, json_row):
        df = {}
        # json_row = json_row['json_name']
        for i,arr in enumerate(skeleton):
            # print(type(arr[4][0]))
            tmp = []
            # print(arr[0])
            if (arr[4][0] == 'True') or (arr[4][0] == True):
            # if arr[4][0]:
                # print(str(arr[4][0]))
                # print(str(arr[1]))
                # {'id': eval(tmp_eval)}
                for j, arr2 in enumerate(arr[1]):
                    # print('arr2SI:',str(arr2))
                    tmp_eval = 'json_row' + str(arr2)
                    tmp.append((self.only_columns({'id_': eval(tmp_eval)}),arr[2][j],arr[3][j]))
            else:
                for j, arr2 in enumerate(arr[1]):
                    # print('arr2No:',str(arr2))
                # print('arr2:',arr2)
                # print('arr:',arr)
                # print('arr[3][J]',arr[3][j])
                    tmp_eval = 'json_row' + str(arr2)
                    tmp.append((self.only_columns(eval(tmp_eval)),arr[2][j],arr[3][j]))
                # tmp.append(only_columns(eval(tmp_eval)))
            df[arr[0]] = tmp
            # print('---------')
        return df

    def only_columns(self, dict_to_column):
        dict_keys = {}
        for key, value in dict_to_column.items():
            if isinstance(value,list):
                if len(value) != 0:
                    if not isinstance(value[0],(list,dict)):
                        # dict_keys[key] = value
                        pass
            elif not isinstance(value,dict):
                dict_keys[key] = value
        return dict_keys

    def extraction(self, json_row):
        return self.iterate_over_json(self.pivot_extraction_keys(self.extraction_keys(json_row, lista_claves = [])),json_row)

    def convert_todict(self,lista):
        list_to_dict = []
        for i in lista:
            list_to_dict.append({'id':i})
        return list_to_dict
#%%
# test
if False:
    import json
    with open('example/candidate_example.json', 'r', encoding='utf-8') as data_file:   
        cand_test = json.load(data_file)    
    df_cand = extraction().extraction({'candidate':cand_test})
#%%
# n_cell
# Description
# b = copy.deepcopy(cand_test)
# c = extraction_keys(copy.deepcopy(cand_test))
#%%
# jobs
if False:
    import json
    with open('example/job_example.json', 'r', encoding='utf-8') as data_file:    
        job_test = json.load(data_file)
    df_job = extraction().extraction(job_test)

#%%
# n_cell
# Description
# ext = extraction()

#%%
# ext.extraction(job_test)

#%%
