import pandas as pd

def DFinfo(data):
    """
    Более информативная версия .info().
    Использует более рационально место в jupiter, в дополнение к информации info выводит:
    количество нулей, уникальные значения, типы, наиболее частые значения (само значение и частота),
    среднее использование памяти.
    
    """
    columns = ['non-null', 'null', 'unique', 'type', 'top', 'freq', 'mean_memory_usage']
    index = []
    result = []
    for col in data.columns:
        # calculate memory
        serias_type = data[col].dtype
        selected_dtype = data.select_dtypes(include=[serias_type])
        mean_usage_b = selected_dtype.memory_usage(deep=True).mean()
        # returns size in human readable format
        def sizeof_fmt(num):
            # returns size in human readable format
            for x in ["bytes", "KB", "MB", "GB", "TB"]:
                if num < 1024.0:
                    return "{num:3.1f} {x}".format(num=num, x=x)
                num /= 1024.0
            return "{num:3.1f} {pb}".format(num=num, pb="PB")
        
        mean_memory = sizeof_fmt(mean_usage_b)
        
        objcounts = data[col].value_counts() # count unique
        index.append(col)                  # add columns
        result.append(
            [len(data[data[col].notna()]), # non-null
            len(data[data[col].isna()]),   # null
            len(data[col].unique()),       # unique
            serias_type,               # type
            objcounts.index[0],            # top
            objcounts.iloc[0],
            mean_memory])            # freq

    result = pd.DataFrame(result, index=index, columns=columns)
    return result