import pandas as pd
import os
import warnings
import multiprocessing

class ParallelDataFrame():
    '''
    Run pandas apply function with multiprocessing, suitable for CPU 
    intensive operation; the execution time advantage is showing with
    large dataframe/series.
    '''

    def __init__(self, df, num_ps=None):
        '''
        param:
            df: DataFrame
            num_ps: int; optional
        '''

        cpu_counts = multiprocessing.cpu_count()
        cores = cpu_counts - 1 if cpu_counts > 1 else cpu_counts

        if num_ps:
            self.pool = multiprocessing.Pool(processes=cores)
        else:
            self.pool = multiprocessing.Pool(processes=num_ps)

        self._df = df
        
        if os.name == 'nt':
            warnings.warn("requiring multiprocessing-safe main module protection: " +
                          "if __name__ == '__main__':")        


    def apply(self, func, *args, chunksize=10000):
        '''
        param:
            func: function
            chunksize: int; default to 10000

        return: DataFrame or Series
        '''

        async_results = [self.pool.apply_async(func,
                         (self._df.iloc[i: i + chunksize], *args))
                         for i in range(0, len(self._df), chunksize)]

        df_results = [_r.get() for _r in async_results]

        return pd.concat(df_results)


    def group_apply(self, func, groupkey, *args):
        '''
        param:
            groupkey: str; list of str
            func: function

        return: DataFrame or Series
        '''

        grp_obj = self._df.groupby(groupkey)

        async_results = [self.pool.apply_async(func, (grp_obj.get_group(grp),
                         groupkey, grp, *args))
                         for grp in grp_obj.groups]

        df_results = [_r.get() for _r in async_results]

        return pd.concat(df_results)


    def close(self):

        self.pool.close()


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc, tb):
        self.close()