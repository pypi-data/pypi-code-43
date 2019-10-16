
import cv2 as __cv2__

def build_artwork_video(path_artwork,
                        path_list_artwork,
                        video_name = 'artwork_video.mp4',
                        fps= 60):
    frame_array = []
    for i in range(len(path_list_artwork)):
        if i%10==0:
            print('Progress:',round(i/len(path_list_artwork)*100,1),end='\r')
        filename=path_list_artwork[i]
        #reading each files
        img = __cv2__.imread(filename)
        height, width, layers = img.shape
        size = (width,height)
        #print(filename)
        #inserting the frames into an image array
        frame_array.append(img)
     
    path_video = os.path.join(path_artwork,video_name)
    out = __cv2__.VideoWriter(path_video,__cv2__.VideoWriter_fourcc(*'DIVX'), fps, size)
 
    for i in range(len(frame_array)):
        # writing to a image array
        out.write(frame_array[i])
    out.release()

def decompose_video_to_img(path_video,
                           show_plots = True,
                           verbose = 1):
    
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
        fig, ax_list = plt.subplots(1,5)
        p=0
        #build dummy img
        img_dummy = np.zeros((int(prop_dict['frame_height']),int(prop_dict['frame_width']),3)).astype(int)+255
        
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
                    plt.show()
                    fig, ax_list = plt.subplots(1,5)
                    for ax in ax_list: #fill in dummy imgs to prevent irregular formatting at end of frame list
                        ax.imshow(img_dummy)
                        ax.grid(which='both',visible=False)
                        ax.axis('off')
                else: p+=1
    fig.tight_layout(rect=(0,0,2.5,1))
    plt.show()
    
    cap.release()
    __cv2__.destroyAllWindows()