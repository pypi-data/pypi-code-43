#%%
# n_cell
# Description
from collections.abc import Mapping
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine
import copy
#%%
# n_cell
# Description
class inserction:
    def __init__(self, db_engine, master_dict, logger=None):
        self.db_engine = db_engine
        self.logger = logger
        self.master_dict = master_dict

    def filter_none(self, d):
        if isinstance(d, Mapping):
            return {k: self.filter_none(v) for k, v in d.items() if v is not None}
        else:
            return d

    def prepare_inserction(self, extraction_table):
        dict_clases = {}
        tmp_clases = []
        intersection = set(self.master_dict.keys()).intersection(extraction_table.keys())
        for i,j in self.master_dict.items():
            if i not in intersection:
                continue
            tmp_clases = []
            for l,k in enumerate(extraction_table[i]):
                if j[1] != '':
                    str_parent = j[1]
                    if (k[2] == 'None') or (k[2] is None):
                        str_parent+='0'               
                    else:
                        str_parent+=k[2]
                    dict_clases[i+str(l)] = self.update_class(j[0],k[0],j[2],dict_clases[str_parent])
                else:
                    dict_clases[i+str(l)] = self.update_class(j[0],k[0])
        return dict_clases

    def inserction(self, extraction_table):
        dict_clases = self.prepare_inserction(extraction_table) 
        try:
            cnxn = create_engine(self.db_engine, echo=False)
            conn = cnxn.connect()
            Session = sessionmaker(bind=cnxn,autoflush=True)
            session = Session()
        except Exception as e:
            print('Exception session')
            if self.logger:
                self.logger.error('Exception session')
        finally:
            session.close()
        try:
            for key, value in dict_clases.items():
                session.merge(value)
                session.flush()  
        except Exception as e:
            try:
                print(str(extraction_table))
                print('key: ' + key + 'dict of tables: '  + str(extraction_table[key]))            
                self.logger.error('key: ' + key + 'dict of tables: '  + str(extraction_table[key]))
            except Exception as f:
                print('not found key in ' + key)
                self.logger.error('not found key in ' + key)            
            print('Exception merge/flush in inserction: ' + str(e) + ', dict_clases: ' + str(dict_clases))
            self.logger.error('Exception merge/flush in inserction: ' + str(e) + ', dict_clases: ' + str(dict_clases))
            session.rollback()
        try:
            session.commit()
            return True
        except Exception as e:
            print('Exception commit in inserction: ' + str(e) + ', dict_clases: ' + str(dict_clases))
            self.logger.error('Exception commit in inserction: ' + str(e) + ', dict_clases: ' + str(dict_clases))
            session.rollback()
        finally:
            session.close()

    def update_class(self, clas, dict_row,relation=None, clas_parent=None):
        new_dict = dict(**self.filter_none(dict_row))
        new_clas = copy.deepcopy(clas)
        for key, value in new_dict.items():
            setattr(new_clas, key, value)
        if clas_parent != None:
            key = relation
            setattr(new_clas, key, clas_parent)
        return new_clas