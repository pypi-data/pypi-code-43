"""
This sub-module contains functions/classes related to image analysis, most of which wrap SciKit image functions in some way.
"""

import numpy as _np
import matplotlib.pyplot as __plt__

try:
    import cv2 as __cv2__
except:
    import os as __os__
    __os__.system("apt-get install -y libsm6 libxext6 libxrender-dev")
    import cv2 as __cv2__

def base64_str_to_img(base64_str):
    """
    Convert base64 string to an image array. The function can handle raw string or bytes encoded sting.
    
    Arguments:
    ----------
        base64_str: bytes or raw string of image in base64 format
        
    Returns:
    --------
        img: standard image array
    """
    import base64
    import io
    import cv2
    import imageio
    
    if type(base64_str)==type(b''):
        base64_str = base64_str.decode()

    img = imageio.imread(io.BytesIO(base64.b64decode(base64_str)))
    
    return img

def resize(img, y_size, x_size):
    """
    resize and image using skimage.transform.resize(..., mode= 'reflect')
    """
    return skimage.transform.resize(img, (y_size,x_size),mode= 'reflect')

def denoise(img):
    """
    denoise an image using skimage.restoration.denoise_tv_chambolle()
    """
    import skimage.restoration
    return skimage.restoration.denoise_tv_chambolle(img)

def __build_crop_array__(img,yx_min,yx_max,padding, use_square = False):
    """
    Helper function to assemble the crop array for the __find_img_contours_and_cropping_array__() function
    """
    y_min_index = max(yx_min[0]-padding,0)
    x_min_index = max(yx_min[1]-padding,0)
    
    y_max_index = min(yx_max[0]+padding,img.shape[0])
    x_max_index = min(yx_max[1]+padding,img.shape[1])
    
    crop_array = [y_min_index, y_max_index, x_min_index, x_max_index]
    
    if use_square:
        mean_width = _np.mean((crop_array[1]-crop_array[0],crop_array[3]-crop_array[2]))
        x_offset = mean_width - (crop_array[1]-crop_array[0])
        y_offset = mean_width - (crop_array[3]-crop_array[2])
        
        crop_array[0] = crop_array[0]-int(x_offset/2)
        crop_array[1] = crop_array[1]+int(x_offset/2)
        crop_array[2] = crop_array[2]-int(y_offset/2)
        crop_array[3] = crop_array[3]+int(y_offset/2)
    
    return crop_array

def __find_img_contours_and_cropping_array__(img, contour_level = 0.1, padding = 50, use_square = False):
    """
    sub-function for auto_crop.use_counts() which runs the skimage.measure.find_countours operation & pulls out the cropping bounds for the analyzed image.
    
    Arguments:
    ----------
        img: The gray-scale image of interest
        countour_level: Value along which to find contours in the array
        padding: int. number of pixels to pad the autocrop boundaries by
        use_square: boolean. Whether or not the force the crop to be a square.
        
    Returns:
    --------
        countours: The countours found via skimage.measure.find_contours
        crop_array: Array of values defining the crop limits. 
            - To crop and image using the crop_array execute: img[crop_array[0]:crop_array[1],crop_array[2]:crop_array[3]]
        
    Notes:
    ------
        See https://scikit-image.org/docs/0.8.0/api/skimage.measure.find_contours.html for more details
    """
    
    # Find contours
    import skimage.measure
    contours = skimage.measure.find_contours(img, level = contour_level)
    
    if contours == []:
        yx_max = [img.shape[0]-1,img.shape[1]-1]
        yx_min = [0,0]
    else:
        #get corner indices
        yx_max = _np.array([[contours[i][:, 0].max(), contours[i][:, 1].max()] for i in range(len(contours))])
        yx_max = [int(yx_max[:,0].max()),int(yx_max[:,1].max())]

        yx_min = _np.array([[contours[i][:, 0].min(), contours[i][:, 1].min()] for i in range(len(contours))])
        yx_min = [int(yx_min[:,0].min()), int(yx_min[:,1].min())]
    
    #Build Cropping array  
    crop_array = __build_crop_array__(img, yx_min, yx_max, padding, use_square = use_square)
    
    return contours, crop_array

class auto_crop():
    """
    This class contains helper functions for autocropping an image
    """

    def use_countours(img, 
                      padding = 50,
                      show_plots = {'processed':True, 
                                    'processing steps':False},
                      use_square=False,
                      contour_level_max_offset_scalar = 2):
        """
        Wrapper to make img cropping simpler. The function converts the img to grayscale, runs the "find_img_countours_and_cropping_array" function, and applies the cropping to the original img (RGB) via img_cropped = img[crop_array[0]:crop_array[1],crop_array[2]:crop_array[3]]. img_cropped is then returned.
        
        Arguments:
        ----------
            img: RGB image of interest
            padding: int. number of pixels to pad the autocrop boundaries by
            show_plots: dictionary defining which of the autocropping operations to show plots for.
            use_square: boolean. Whether or not the force the crop to be a square.
            contour_level_max_offset_scalar:
            
        Returns:
        --------
            img_cropped: The image after autocropping
        """
        import skimage
        
        img = img/img.max()
        img_gray = skimage.color.rgb2gray(img)
        img_gray = img_gray/img_gray.max()

        contour_level = img_gray.max()/contour_level_max_offset_scalar

        contours, crop_array = __find_img_contours_and_cropping_array__(img_gray,
                                                             contour_level = contour_level,
                                                             padding = padding,
                                                                   use_square = use_square)

        img_cropped = img[crop_array[0]:crop_array[1],crop_array[2]:crop_array[3]]


        if show_plots['processing steps']:
            #original image
            __plt__.title(title+'\noriginal img')
            __plt__.imshow(img)
            __plt__.grid(which='both')
            __plt__.axis('off')
            __plt__.show()

            #gray with cropping points and contours
            __plt__.imshow(img_gray, interpolation='nearest', cmap='binary')
            for n, contour in enumerate(contours):
                 __plt__.plot(contour[:, 1], contour[:, 0], linewidth=1, color = 'r')
            __plt__.plot(crop_array[2:4],crop_array[0:2],'bo')
            __plt__.title('Cropping pts: '+str(crop_array))
            __plt__.grid(which='both')
            __plt__.axis('off')
            __plt__.show()

        if show_plots['processed']:
            __plt__.title(img.shape)
            __plt__.imshow(img_cropped)
            __plt__.grid(which='both')
            __plt__.axis('off')
            __plt__.show()

        return img_cropped
    
    def use_edges(img, 
                  edges_dict = {'sigma':10,
                                'low_threshold':None,
                                'high_threshold':None},
                  padding = (0,0),
                  show_plots = False,
                  verbose = 0):
        
        """
        Use skimage.feature.canny method to find edges in the image passed and autocrop on the outermost edges
        
        Arguments:
            img: RGB img
            edges_dict: dictionary containing 'sigma', 'low_threshold', 'high_threshold' settings passed to the canny edge detection method.
            padding: # of pixels you want to pad on the edges found by the canny edge filter
            show_plots: boolean to show or not show plots
            verbose: integer. Higher value will print more processing statements/info.
        Returns:
            img_cropped: RGB img with cropping applied
            img_cropped_gray: grayscale image with cropping applied.
        """
        import skimage, skimage.feature
        
        # instantiate img plot
        if show_plots:
            fig, ax_list = __plt__.subplots(1,4)
            i=0
        
            ax_list[i].set_title('original img')
            ax_list[i].imshow(img)
            ax_list[i].grid(which='both', visible=False)
            ax_list[i].axis('off')
            i+=1
        
        #convert to grayscale
        img_gray = skimage.color.rgb2gray(img)
        img_gray = img_gray/_np.mean(img_gray.flatten()) # mean normalized
        if show_plots:
            ax_list[i].set_title('grayscale img')
            ax_list[i].imshow(img_gray)
            ax_list[i].grid(which='both', visible=False)
            ax_list[i].axis('off')
            i+=1

        #find edges
        edges = skimage.feature.canny(img_gray,
                                        sigma = edges_dict['sigma'],
                                        low_threshold = edges_dict['low_threshold'],
                                        high_threshold = edges_dict['high_threshold'],
                                        mask=None,
                                        use_quantiles=False)
        if show_plots:
            ax_list[i].set_title('edges')
            ax_list[i].imshow(edges)
            ax_list[i].grid(which='both', visible=False)
            ax_list[i].axis('off')
            i+=1
        
        #fetch indices of coner edges
        edge_indices = _np.where(edges==True)
        if edge_indices[0].shape[0] != 0 and edge_indices[1].shape[0] != 0 :
            ylim = [_np.min(edge_indices[0])-padding[0],_np.max(edge_indices[0])+padding[0]]
            
            #ensure the padding doesn't extend beyond the image itself
            if ylim[0]<0:
                ylim[0]=0
            if ylim[1]>img.shape[0]:
                ylim[1] = img.shape[0]
            
            xlim = [_np.min(edge_indices[1])-padding[1],_np.max(edge_indices[1])+padding[1]]
            
            #ensure the padding doesn't extend beyond the image itself
            if xlim[0]<0:
                xlim[0]=0
            if xlim[1]>img.shape[1]:
                xlim[1] = img.shape[1]

            #plot cropped image
            img_cropped = img[ylim[0]:ylim[1], xlim[0]:xlim[1],:]
            img_cropped_gray = img_gray[ylim[0]:ylim[1], xlim[0]:xlim[1]]
        else:
            img_cropped = img
            img_cropped_gray = img_gray
            
        if show_plots:
            ax_list[i].set_title('cropped img')
            ax_list[i].imshow(img_cropped)
            ax_list[i].grid(which='both', visible=False)
            ax_list[i].axis('off')
            i+=1
            
        if show_plots:
            fig.tight_layout(rect=(0,0,3,1))
            __plt__.show()
           
        if verbose>=1:
            print('img.shape:',img.shape)
            print('img_cropped.shape',img_cropped.shape)
            print('img reduction factor:', _np.prod(img.shape)/_np.prod(img_cropped.shape))
            
        return img_cropped, img_cropped_gray
    
def autocrop_and_downscale(img, target_min_dim = 256, verbose = 0):
    """
    Apply edges-based autocropping and downscale using local mean to reduce the min dimension of an image to be equal to the 'target_min_dimension' argument.
    
    Arguments:
    ----------
        img: RGB or gray-scale
        target_min_dim: integer. default: 256. min dimension for the output image. If the image is rectangular, the longer axis will be scaled by the same amoutn as the shorter axis such that the output image is not distorted.
        verbose: integer. default: 0. verbosity of print statements
        
    Returns:
    --------
        img_autocrop_downscale: RGB image
    """
    import skimage.transform
    
    img_autocrop, _ = auto_crop.use_edges(img, show_plots = False, verbose=0)
    
    #fetch xy dimensions of autocropped image
    dims = list(img_autocrop.shape)[:2]
    
    #calculate downscale factors
    if len(img.shape)==3: 
        downscale_factors = (int(_np.min(dims)/target_min_dim), int(_np.min(dims)/target_min_dim), 1)
    else:
        downscale_factors = (int(_np.min(dims)/target_min_dim), int(_np.min(dims)/target_min_dim))
    
    if img_autocrop.max()>1:
        img_autocrop = img_autocrop/255
    
    #downscale img
    img_autocrop_downscale = skimage.transform.downscale_local_mean(img_autocrop, downscale_factors)

    if verbose>=1:
        print('img.shape:',img.shape)
        print('img_autocrop.shape:',img_autocrop.shape)
        print('img_autocrop_downscale.shape:',img_autocrop_downscale.shape)
        print('img size reduction factor:', round(_np.prod(img.shape)/_np.prod(img_autocrop_downscale.shape),0))
    
    return img_autocrop_downscale 

def decompose_video_to_img(path_video,
                           show_plots = True,
                           verbose = 1):
    """
    Use cv2 to pull out image frames from a video and save them as png files
    
    Arguments:
    ----------
        path_video: file path to the video of interest
        show_plots: whether or not to show the image slices decomposed from the video
        verbose: print-out verbosity
    
    Returns:
    --------
        None. The decomposed images will be saved in a subfolder having the videos name. The subfolder is in the path_video directory. The images are saved as .png.
    """
    if verbose>=1:
        print(os.path.split(path_video)[1])
    
    #fetch video object
    cap = __cv2__.VideoCapture(path_video)
    
    propid_dict = {'frame_width':3,
                   'frame_height':4,
                   'fps':5,
                   'frame_count':7,
                   'convert_to_RGB':16}
    prop_dict = {}
    for key in propid_dict.keys():
        prop_dict[key] = cap.get(propid_dict[key])
        if verbose>=1: print('\t',key,':', prop_dict[key])
    
    #make subfolder for frames
    path_frames_folder = os.path.join(path_artwork, os.path.splitext(file)[0])
    if os.path.isdir(path_frames_folder)==False:
        os.makedirs(path_frames_folder)
    
    if show_plots: #instantiate plots
        fig, ax_list = __plt__.subplots(1,5)
        p=0
        #build dummy img
        img_dummy = _np.zeros((int(prop_dict['frame_height']),int(prop_dict['frame_width']),3)).astype(int)+255
        
    for i in range(int(prop_dict['frame_count'])):
        retval, img = cap.read()
        
        #check if the video is encoded as RGB
        if bool(prop_dict['convert_to_RGB'])==False: 
            img = __cv2__.cvtColor(img, __cv2__.COLOR_BGR2RGB)
            
        #save the img
        filename = 'frame_'+str(i)+'.png'
        path_file = os.path.join(path_frames_folder,filename)
        __cv2__.imwrite(path_file,img)
        
        if verbose>=1:
            None
        if i%round(prop_dict['fps'])==0: #only show frame approx every second
            if show_plots:
                ax_list[p].imshow(img)
                ax_list[p].grid(which='both',visible=False)
                ax_list[p].axis('off')
                if p+1>len(ax_list)-1: 
                    p=0
                    fig.tight_layout(rect=(0,0,2.5,1))
                    __plt__.show()
                    fig, ax_list = __plt__.subplots(1,5)
                    for ax in ax_list: #fill in dummy imgs to prevent irregular formatting at end of frame list
                        ax.imshow(img_dummy)
                        ax.grid(which='both',visible=False)
                        ax.axis('off')
                else: p+=1
    fig.tight_layout(rect=(0,0,2.5,1))
    __plt__.show()
    
    cap.release()
    __cv2__.destroyAllWindows()
