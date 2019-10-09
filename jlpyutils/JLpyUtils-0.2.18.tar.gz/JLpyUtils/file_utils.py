"""
save and load helper functions to streamline saving common file types including 'hdf', 'csv', 'json', 'dill'
"""

def save(obj, filename, format_, path_dir) :
    """
    Save an arbitrary object with the specified filename and format_ in the path_dir
    
    Arguments:
    ----------
        obj:
        filename:
        format_:
            - valid formats: 'h5', 'csv', 'json', 'dill', 'h5_csv', 'hdf'
        path_dir:
    """
    try:

        import os, sys

        if os.path.isdir(path_dir)==False:
            os.makedirs(path_dir)

        if format_ == 'h5':

            import h5py

            path_save_file = os.path.join(path_dir, filename+'.h5' )

            file = h5py.File(path_save_file, 'w')
            file.create_dataset(filename, data=obj)
            file.close()

        elif format_ == 'csv':

            import numpy as np

            path_save_file = os.path.join(path_dir,filename+'.csv')

            if type(obj)==np.ndarray:
                np.savetxt(path_save_file, obj, delimiter=',')
            else:

                import dask
                if type(obj)==dask.dataframe.core.DataFrame:
                    path_save_file = path_save_file.replace('.csv','_batch*.csv')

                obj.to_csv(path_save_file, index=False)

        elif format_ == 'json':

            import json
            path_save_file = os.path.join(path_dir, filename+'.json')
            file = open(path_save_file, 'w')
            json.dump(obj, file)
            file.close()

        elif format_ == 'dill':
            import dill
            path_save_file = os.path.join(path_dir, filename+'.dill')
            file = open(path_save_file, 'wb')
            dill.dump(obj, file)
            file.close()

        elif format_ =='h5_csv': #try saving as h5, otherwise save as csv
            try:
                import h5py

                path_save_file = os.path.join(path_dir, filename+'.h5' )

                file = h5py.File(path_save_file, 'w')
                file.create_dataset(filename, data=obj)
                file.close()
            except:
                file.close()
                os.remove(path_save_file)

                import numpy as np

                path_save_file = os.path.join(path_dir,filename+'.csv')

                if type(obj)==np.ndarray:
                    np.savetxt(path_save_file, obj, delimiter=',')
                else:
                    obj.to_csv(path_save_file, index=False)

        elif format_=='hdf':
            import dask

            try:
                path_save_file = os.path.join(path_dir, filename+'.hdf' )
                obj.to_hdf(path_save_file, '/data')

            except Exception as e:
                import os

                print(e)
                print('\n...saving as csv')
                if os.path.isfile(path_save_file):
                    os.remove(path_save_file)

                obj.to_csv(path_save_file.replace('.hdf','_*.csv'), index=False)
    except Exception as e:
        print('Error for:',filename, format_, path_dir)
        raise e
    
        

def load(filename, format_, path_dir, headers='infer'):
    
    """
    Load an arbitrary object with the specified filename and format_ in the path_dir
    Arguments:
    ----------
        filename: the name of the file of interest (without the extension)
        format_: the format of the file ('h5','csv','json','dill','h5_csv','hdf')
        path_dir: the directory where the file is stored
        headers: the headers that will be assigned to the file for 'csv' or 'h5_csv' formats.
            - If 'infer' the headers will be infered from the file
            - If None, the file will be loaded without headers
            - If a list is passed, the headers will be assigned to the values in the list
    Returns:
    --------
        obj: the object loaded from the file. if 'h5_csv' or 'csv', a pandas DataFrame will be returned
    """
    try:
        import os, sys

        if format_ == 'h5': 

            import h5py

            path_save_file = os.path.join(path_dir, filename+'.h5')
            file = h5py.File(path_save_file, 'r')
            obj = file[filename][:]
            file.close()

            if type(headers) == type(list()):
               obj = pd.DataFrame(obj, columns = headers)


        elif format_ == 'csv':

            import pandas as pd

            #check if file is saved in chunks
            chunk_files = [file for file in os.listdir(path_dir) if filename+'_batch' in file and '.csv' in file]
            if len(chunk_files)>0:#load as dask df
                import dask
                path_save_file_list = [os.path.join(path_dir, filename) for filename in chunk_files]
                obj = dask.dataframe.read_csv(path_save_file_list, sample=512000)
            else:
                path_save_file = os.path.join(path_dir, filename+'.csv')
                if type(headers) == type(list()):
                    obj = pd.read_csv(path_save_file, low_memory = False, header = None, names = headers)
                else:
                    obj = pd.read_csv(path_save_file, low_memory = False, header = headers)

        elif format_ == 'dask_csv':
            import dask

            path_save_file = os.path.join(path_dir, filename+'.csv')
            obj = dask.dataframe.read_csv(path_save_file, low_memory = False, header = headers)


        elif format_ == 'json':
            import json
            path_save_file = os.path.join(path_dir, filename+'.json')
            file = open(path_save_file, 'r')
            obj = json.load(file)
            file.close()

        elif format_ == 'dill':
            import dill
            path_save_file = os.path.join(path_dir, filename+'.dill')
            file = open(path_save_file, 'rb')
            obj = dill.load(file)
            file.close()

        elif format_ =='h5_csv': #try loading as h5, otherwise save as csv
            try:
                import h5py
                import pandas as pd

                path_save_file = os.path.join(path_dir, filename+'.h5')
                file = h5py.File(path_save_file, 'r')
                print([key for key in file.keys()])
                obj = file[filename][:]
                file.close()

                if type(headers) == type(list()):
                    obj = pd.DataFrame(obj, columns = headers)

            except:
                import pandas as pd

                path_save_file = os.path.join(path_dir, filename+'.csv')
                if type(headers) == type(list()):
                    obj = pd.read_csv(path_save_file, low_memory = False, header = None, names = headers)
                else:
                    obj = pd.read_csv(path_save_file, low_memory = False, header = headers)

        elif format_=='hdf':
            import dask

            path_save_file = os.path.join(path_dir, filename+'.hdf' )

            try:
                obj = dask.dataframe.read_hdf(path_save_file, '/data')
            except:
                import pandas as pd

                obj = pd.read_hdf(path_save_file,'/data')

                npartitions = max([1,int(obj.shape[0]/53685)])

                obj = dask.dataframe.from_pandas(obj, npartitions)
            
    except Exception as e:
        print('Error for:',filename, format_, path_dir)
        raise e
        

    return obj