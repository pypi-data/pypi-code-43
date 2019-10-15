"""
Helper functions related to common plotting operations via matplotlib
"""

import matplotlib as _mpl
import matplotlib.pyplot as _plt
import numpy as _np
import warnings as _warnings
import os as _os

from . import _plot_imgs as imgs

_mpl.rcParams['grid.color'] =  'lightgray'
_mpl.rcParams['grid.linestyle'] = '-'
_mpl.rcParams['grid.linewidth'] = 1
_mpl.rcParams['axes.grid.which'] = 'both'
_mpl.rcParams['axes.grid']=True 
_mpl.rcParams['xtick.minor.visible']=True
_mpl.rcParams['ytick.minor.visible']=True
_mpl.rcParams['xtick.top']=True
_mpl.rcParams['ytick.right']=True
_mpl.rcParams['xtick.direction']='inout'
_mpl.rcParams['ytick.direction']='inout'
_mpl.rcParams['font.size'] = 14
_mpl.rcParams['figure.facecolor'] = 'w'

def make_independant_legend(legend_lines,legened_labels,legend_title):
    """
    Generate a plot legend without any plot
    """
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    
    _plt.legend(legend_lines,legened_labels,title=legend_title)
    _plt.grid(which='both')
    _plt.axis('off')
    _plt.show()

def fetch_color_map_for_primary_color(primary_color, 
                                      n_colors, 
                                      color_space_range = None):
    """
    Default color_space_range = {'R': (0.1,0.7),
                                 'G': (0.4,0.6),
                                 'B': (0,0.3)}
    
    Arguments:
    ----------
        primary_color: str. 'R', 'G', or 'B'
        n_colors: number of color levels to define
        color_space_range: float tuple or list with upper and lower values between 0 and 1 defining the relative range of colors for the primary color selected
    """
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    if color_space_range == None: # Apply default setting
        color_space_range = {'R': (0.1,0.7),
                             'G': (0.4,0.6),
                             'B': (0,0.3)}
        color_space_range = color_space_range[primary_color]

    if primary_color == 'R':
        color_map = _plt.cm.hot(_np.linspace(color_space_range[0],color_space_range[1],n_colors))    
    elif primary_color == 'G':
        color_map = _plt.cm.nipy_spectral(_np.linspace(color_space_range[0],color_space_range[1],n_colors))    
    elif primary_color == 'B':
        color_map = _plt.cm.jet(_np.linspace(color_space_range[0],color_space_range[1],n_colors))    
    return color_map

def corr_matrix(df_corr, cbar_label = 'Correlation Coeff.', vmin = None, vmax = None):
    """
    Plot a correlation matrix chart
    
    Arguments:
    ----------
        df_corr: correlation matrix dataframe
        cbar_label: label for the color bar
        vmin: min value for color bar
        vmax: max value for color bar
    """
    
    fig, ax = _plt.subplots(1,1)
    cax = ax.matshow(df_corr, vmin = vmin, vmax = vmax)
    cbar = fig.colorbar(cax)
    cbar.set_label(cbar_label, labelpad=15, ha='center', va='center', rotation=90)
    ax.grid(which='both',visible=False)
    ax.set_xticklabels([0]+list(df_corr.columns), rotation='vertical')
    ax.set_yticklabels([0]+list(df_corr.columns))
    _plt.show()

def corr_pareto(df_corr, label, max_bars = 30, rect = (0, 0, 1, 1), ylim = None, return_df = False):
    
    '''
    Plot a pareto bar-chart for 1 label of interest within a correlation dataframe
    
    Arguments:
    ---------
        df_corr: pandas DataFrame correlation matrix
        label: column/header for which you want to plot the bar-chart pareto for
        max_bars: max number of bars to plot. If n_bars > max_bars, then the top and bottom half of the sorted bars will be plotted
        rect: tight_layout rectangular coordinates (see matplotlib docs for more details)
        ylim: limits on y axis
        return_df: boolean. Wether or not to return the correlation pareto dataframe
        
    Returns:
    --------
        df_corr_pareto: Pandas DataFrame of the correlation pareto (sorted)
    '''

    import matplotlib as mpl
    import matplotlib.pyplot as plt

    #Fetch pareto for selected label
    df_label_pareto = df_corr[label]
    df_label_pareto_sorted = df_corr[label].sort_values(ascending=False)
    df_label_pareto_sorted = df_label_pareto_sorted.drop(label)

    fig, ax = _plt.subplots(1,1)
    if len(df_label_pareto_sorted.index)>max_bars:
        bottom = df_label_pareto_sorted.iloc[:int(max_bars/2)]
        top = df_label_pareto_sorted.iloc[-int(max_bars/2):]
        
        ax.bar(bottom.index, bottom, label = 'top '+str(int(max_bars/2)))
        ax.bar(top.index, top, label = 'bottom '+str(int(max_bars/2)))

        ax.set_xticklabels(list(bottom.index)+list(top.index), rotation=90)
        ax.legend()
    else:
        ax.bar(df_label_pareto_sorted.index, df_label_pareto_sorted)
        ax.set_xticklabels(df_label_pareto_sorted.index, rotation = 'vertical')
    
    ylabel = label+" Correlation Factor"
    
    #make sure the y axis label isn't too long, otherwise added next lines to the label
    if len(ylabel)>20:
        ylabel = '\n'.join(ylabel.split(' '))
    
    ax.set_ylabel(ylabel)
    ax.set_title(label+" Correlation Factor Pareto\n")
    ax.grid(which='both', visible=False)
    ax.set_ylim(ylim)
    
    try:
        fig.tight_layout(rect = rect )
    except:
        None
    _plt.show()
    
    if return_df:
        df_corr_pareto = df_label_pareto_sorted.reset_index()
        df_corr_pareto.columns = ['feature','Corr Coeff']
    else:
        df_corr_pareto = None
    return df_corr_pareto
    
def covariance_matrix(df_cov, 
                      cbar_label = 'Covariance Coeff.', vmin = None, vmax = None):
    """
    Plot the covariance matrix for the pandas df covariance matrix passed
    
    Arguments:
    ----------
        df_cov: the pandas df covariance matrix (call df.cov on your original df)
        cbar_label: the color bar axis label
        vmin, vmax: min and max values for the color bar. If None, autoscaling will be applied
    """
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    
    fig, ax = _plt.subplots(1,1)
    cax = ax.matshow(df_cov, vmin = vmin, vmax = vmax)
    cbar = fig.colorbar(cax)
    cbar.set_label(cbar_label, labelpad=15, ha='center', va='center', rotation=90)
    ax.grid(which='both',visible=False)
    ax.set_xticklabels([0]+list(df_cov.columns), rotation='vertical')
    ax.set_yticklabels([0]+list(df_cov.columns))
    _plt.show()

def by_color_group_and_line_group(df,
                                   color_group,
                                   line_group,
                                   x_label,
                                   y_label,
                                   x_scale):
    """
    Make a plot with lines defined by a line_group column, where each line is colored according to the color_group column
    
    Arguments:
    ----------
        df: dataframe of interest
        color_group: column name defininig the color group/axis
        line_group: column name defining a line for a given color group
        x_label: the x-axis label
        y_label: the y-axis label
        x_scale: scale for x-axis ('linear','log')
    """
    
    df = df.sort_values(x_label).reset_index(drop=True)
    Color_ID = str(df['Color'].unique()[0])
    
    df_color_group = df.groupby(by=color_group)
    
    legend_labels = list(df[color_group].unique())
    colors = fetch_color_map_for_primary_color(Color_ID, len(legend_labels))
    legend_lines = [_mpllines.Line2D([0], [0], color=c, lw=1) for c in colors]
    
    c = 0
    for color_group_ID, df_by_color_group in df_color_group:
        df_line_group = df_by_color_group.groupby(line_group)
        for line_group_ID, df_by_line_group in df_line_group:
            _plt.plot(df_by_line_group[x_label],df_by_line_group[y_label],color = colors[c], linestyle='-')
        c+=1
    if x_scale == 'log':
        _plt.xscale('log')
    _plt.xlabel(x_label)
    _plt.ylabel(y_label)
    _plt.show()
    make_independant_legend(legend_lines, legend_labels,color_group)
    
    
def hist_or_bar(df, n_plot_columns = 3, 
                 categorical_headers = [None],
                 xscale = 'linear',
                 yscale = 'linear'):
    """
    Iterate through each column in a dataframe and plot the histogram or bar chart for the data.
    
    Arguments:
    ----------
        df: pandas dataframe
        n_plot_columns: number of plots to print on a single row of plots
        categorical_headers: string. The name of the categorical headers which will be plotted as bar charts. If [None], object type headers will be plotted as bar charts.
    """
    
    import datetime
    import sklearn.impute
    
    _warnings.filterwarnings('ignore')
    
    df = df.copy()
    
    dtypes = df.dtypes.reset_index()
    dtypes.columns = ['column','dtype']
    dtypes = dtypes.sort_values(['dtype','column'])
    
    if n_plot_columns == 1:
        fig, ax = _plt.subplots(1, n_plot_columns)
        ax_list = [ax]
    else:
        fig, ax_list = _plt.subplots(1, n_plot_columns)
    p=0
    for header in dtypes['column']:
        
        if 'dask' in str(type(df)):
            Series_ = df[header].compute()
        else:
            Series_ = df[header]
        
        type_ = Series_.dtype
        
        #plot as bar char if object and not date time
        if (type_ == 'O' and isinstance(Series_.iloc[0], datetime.time)==False) or header in categorical_headers:
            
            Series_ = Series_.fillna('NaN')
            
            df_counts = Series_.value_counts().reset_index()
            df_counts.columns = [header, 'counts']
            df_counts = df_counts.sort_values('counts').reset_index(drop=True)
            df_counts[header] = df_counts[header].astype(str)
            
            #only allow up to max_labels to be plotted, otherwise just plot the top and bottom most frequent labels
            max_labels = 10
            if df_counts.shape[0]>max_labels:
                
                bottom = df_counts.iloc[:int(max_labels/2), :]
                top = df_counts.iloc[-int(max_labels/2):, :]
                
                ax_list[p].bar(bottom[header], bottom['counts'], label = 'bottom counts')
                ax_list[p].bar(top[header], top['counts'], label = 'top counts')
                
                ax_list[p].set_xticklabels(list(bottom[header])+list(top[header]), rotation=90)
                ax_list[p].legend()
            else:
                ax_list[p].bar(df_counts[header],df_counts['counts'])
                
                ax_list[p].set_xticklabels(df_counts[header], rotation=90)
        
        #plot counts vs time if time pts
        elif isinstance(df.head()[header].iloc[0], datetime.time):
            
            Series_ = Series_.dropna()
            
            df_counts = Series_.value_counts().reset_index()
            df_counts.columns = [header, 'counts']
            df_counts = df_counts.sort_values(header)
            
            ax_list[p].plot(df_counts[header], df_counts['counts'])
            
            ax_list[p].set_xscale(xscale)
            
            
        else: #plot as histogram
            
            ax_list[p].hist(Series_, bins = _np.min((100, Series_.nunique())))
            
            ax_list[p].set_xscale(xscale)
            
        ax_list[p].grid(which='both',visible=False)
        
        if len(header)>20:
            xlabel = '\n'.join(header.split(' '))
        else:
            xlabel = header
            
        ax_list[p].set_xlabel(xlabel)
        ax_list[p].set_ylabel('counts')
        ax_list[p].set_yscale(yscale)
        ax_list[p].ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
        
        p+=1
        
        if p==n_plot_columns:
            
            p=0
            
            try:
                fig.tight_layout(rect=(0,0,int(n_plot_columns/1.2),1))
            except:
                try:
                     fig.tight_layout()
                except Exception as e: 
                    print('Exception: '+ str(e))
                
            _plt.show()
            
            #generate new plot if this isn't the last header
            if header != list(df.columns)[-1]:
                
                fig, ax_list = _plt.subplots(1, n_plot_columns)
                #fill in dummy plots
                for ax in ax_list:
                    ax.grid(which='both',visible=False)
            p=0
        

    #ensure last plot is formated and shown
    if p!=n_plot_columns:
        try:
            fig.tight_layout(rect=(0,0,int(n_plot_columns/1.2),1))
        except:
            try:
                 fig.tight_layout()
            except Exception as e: 
                print('Exception: '+ str(e))

        _plt.show()
    _warnings.filterwarnings('default')
        