"""
plot functions related to plotting images
"""
import matplotlib as _mpl
import matplotlib.pyplot as _plt
import numpy as _np
import warnings as _warnings
import os as _os

def from_list(imgs_list, n_plot_columns = 3, cmap = 'virdis', title_list = None):
    """
    Plot the images contained in the list of images passed
    
    Arguments: 
    ----------
        imgs_list: list where each element is an array-like image
        n_plot_columns: int. Number of plot columns per row of plots to display
            - If len(imgs_list)<n_plot_columns, the n_plot_columns will be updated to be equal to the len(imgs_list)
        cmap: matplotlib colormap
        title_list: list of strings to use as the title for each plot
        
    Returns:
    --------
        None. the plots will be displayed
    """
    
    if len(imgs_list)<n_plot_columns:
        n_plot_columns = len(imgs_list)
    
    if n_plot_columns == 1:
        fig, ax = _plt.subplots(1, n_plot_columns)
        ax_list = [ax]
    else:
        fig, ax_list = _plt.subplots(1, n_plot_columns)
        
    p = 0
    for i in range(len(imgs_list)):
        
        img = imgs_list[i]
        
        if type(title_list)==type(list()):
            ax_list[p].set_title(title_list[i])
        
        ax_list[p].imshow(img, cmap = cmap)
        ax_list[p].grid(which='both', visible=False)
        
        ax_list[p].set_axis_off()
        
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
            
            # generate new plot if this isn't the last header
            if i != len(imgs_list)-1:
                
                fig, ax_list = _plt.subplots(1, n_plot_columns)
                
                for ax in ax_list:
                    ax.grid(which='both',visible=False)
                    ax.set_axis_off()
            p=0
      
    # ensure last plot is formated and shown
    if p!=n_plot_columns:
        try:
            fig.tight_layout(rect=(0,0,int(n_plot_columns/1.2),1))
        except:
            try:
                 fig.tight_layout()
            except Exception as e: 
                print('Exception: '+ str(e))

        _plt.show()
        

def from_files(path_imgs_dir, filenames = 'auto', 
                n_plot_columns = 3,
                cmap = 'viridis',
                ):
    """
    Plot the images contained in the path_imgs_dir.
    
    Arguments: 
    ----------
        path_imgs_dir: path to directory where images are stored
        filenames: list of filenames for images of interest, or 'auto'.
            - If 'auto' all the image files within the directory will be plotted
        n_plot_columns: int. Number of plot columns per row of plots to display
        cmap: matplotlib colormap
        
    Returns:
    --------
        None. the plots will be displayed
    """
    
    if type(filenames)==type(list()):
        path_imgs = [_os.path.join(path_imgs_dir, filename) for filename in filenames]
    elif filenames == 'auto':
        path_imgs = [_os.path.join(path_imgs_dir, filename) for filename in _os.listdir(path_imgs_dir) if 'png' in filename or 'tiff' in filename or 'bmp' in filename or 'dcm' in filename or 'jpg' in filename or 'jpeg' in filename]
        
    imgs_list = []
    for p in range(len(path_imgs)):
        
        path_img = path_imgs[p]
        
        if 'dcm' in path_img:
            import pydicom
            img = pydicom.dcmread(path_img).pixel_array
        else:
            img = _plt.imread(path_img)
        
        imgs_list.append(img)
        
        p+=1
        
        if p%n_plot_columns==0 or p>len(path_imgs):
            
            from_list(imgs_list, n_plot_columns, cmap)
            
            imgs_list = []
        
    