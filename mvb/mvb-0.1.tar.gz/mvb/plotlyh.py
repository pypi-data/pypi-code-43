def top_n_pie_chart(df,val_col,n=50,title=None):
    """
    Inserts an inline plot of a Pie chart for the top N results from
    a dataframe, rolling the remaining results into an "other" slice.
    
    @input df: pandas dataframe contaiing a value column, index will be name of each slice
    @input val_col: string name of column to get values from
    @input n: int optional, default 50, number of items to show in pie (plus other category)
    @input title: string optional, title given to pie chart
    """
    df = df.sort_values(val_col,ascending=False)
    top_n_df = df.iloc[:n][val_col]
    if df.shape[0] > n:
        other_df = df.iloc[n:][val_col]
        top_n_df = top_n_df.append(pd.Series([other_df.sum()], index=[f"{other_df.shape[0]} Others"]))
    
    iplot(
        go.Figure(
            data=[
                go.Pie(labels=top_n_df.index, 
                       values=top_n_df.values,
                       sort=False)
            ],
            layout=dict(
                title=title
            )
        )
    )
