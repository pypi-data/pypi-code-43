import cv2
import numpy as np


class GreenLevelAssesement:
    def __init__(self, 
                 resize_height, 
                 resize_width,
                 grid_height,
                 grid_width):

        """Constructor
        
        Arguments:
            resize_height {integer} -- the height of input image will be resized
            resize_width {integer} -- the width of input image will be resized
            num_vertical_grid {integer} -- the number of vertical cluster grid
            num_horizontal_grid {integer} -- the number of horizontal cluster grid
        """
        
        self.resize_height = resize_height
        self.resize_width = resize_width
        self.kernel = np.ones((3,3),np.float32)/9.
        
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.num_vertical_grid = int(self.resize_height / self.grid_height) 
        self.num_horizontal_grid = int(self.resize_width / self.grid_width) 
        
        self.green_class_dict = {}
        self.green_class_dict['a'] = np.full((self.grid_height, self.grid_width, 3), (19, 81, 27)).astype(np.uint8)
        self.green_class_dict['b'] = np.full((self.grid_height, self.grid_width, 3), (31, 135, 44)).astype(np.uint8)
        self.green_class_dict['c'] = np.full((self.grid_height, self.grid_width, 3), (95, 196, 45)).astype(np.uint8)
        self.green_class_dict['d'] = np.full((self.grid_height, self.grid_width, 3), (75, 242, 110)).astype(np.uint8)
        self.green_class_dict['e'] = np.full((self.grid_height, self.grid_width, 3), (76, 242, 177)).astype(np.uint8)
        self.green_class_dict['f'] = np.full((self.grid_height, self.grid_width, 3), (76, 200, 200)).astype(np.uint8)
        self.green_class_dict['g'] = np.full((self.grid_height, self.grid_width, 3), (76, 200, 255)).astype(np.uint8)
        self.green_class_dict['h'] = np.full((self.grid_height, self.grid_width, 3), (76, 165, 255)).astype(np.uint8)
        self.green_class_dict['i'] = np.full((self.grid_height, self.grid_width, 3), (76, 135, 255)).astype(np.uint8)
        self.green_class_dict['j'] = np.full((self.grid_height, self.grid_width, 3), (76, 100, 255)).astype(np.uint8)

        #for i in self.green_class_dict:
        #    self.green_class_dict[i] = cv2.putText(self.green_class_dict[i], i, (0,20), cv2.FONT_HERSHEY_SIMPLEX, 1, 255)

        
    
    def get_green_index(self, 
                        img,
                        alpha = 0,
                        beta = 0,
                        method = cv2.NORM_MINMAX, 
                        dtype= cv2.CV_32F):
        """Method for getting the greeness index
        
        Arguments:
            img {numpy array} -- opencv image as an input
        
        Keyword Arguments:
            alpha {int} -- the alpha value (default: {0})
            beta {int} -- the beta value (default: {0})
            method {opencv normalized method} -- the normalize method (default: {cv2.NORM_MINMAX})
            dtype {opencv data type} -- the opencv data type (default: {cv2.CV_32F})
        
        Returns:
            g_index {numpy array} -- opencv image format of green index
            norm_img {numpy array} -- opencv image format of normalized image
        """
    
        img = cv2.filter2D(img, -1, self.kernel)
        
        norm_img = cv2.normalize(img, 
                                 None, 
                                 alpha=alpha, 
                                 beta=beta, 
                                 norm_type=method, 
                                 dtype=dtype)
        
        g_index = (norm_img[:, :, 1] * 255 /(norm_img[:, :, 0] + norm_img[:, :, 1] + norm_img[:, :, 2] + 0.001)).astype(np.uint8)
        
        return g_index, norm_img
    
    
    def green_grid(self, img):
        """Method for getting greenness grid
        
        Arguments:
            img {numpy array} -- input image 
        
        Returns:
            res {numpy array} -- grid image
        """

        img = cv2.resize(img, (self.resize_width, self.resize_height))
        print (img.shape, self.num_vertical_grid, self.num_horizontal_grid, self.grid_height, self.grid_width, self.resize_width, self.resize_height)
        crops = []

        for i in range (self.num_vertical_grid):
            tmp = []
            
            for j in range(self.num_horizontal_grid):
                crop = img[i*self.grid_height:(i+1)*self.grid_height, j*self.grid_width:(j+1)*self.grid_width]
                mean = np.mean(crop)
                
                if mean < 40:
                    tmp.append(self.green_class_dict['j'])
                elif mean < 50:
                    tmp.append(self.green_class_dict['i'])
                elif mean < 60:
                    tmp.append(self.green_class_dict['h'])
                elif mean < 70:
                    tmp.append(self.green_class_dict['g'])
                elif mean < 80:
                    tmp.append(self.green_class_dict['f'])
                elif mean < 90:
                    tmp.append(self.green_class_dict['e'])
                elif mean < 100:
                    tmp.append(self.green_class_dict['d'])
                elif mean < 110:
                    tmp.append(self.green_class_dict['c'])
                elif mean < 120:
                    tmp.append(self.green_class_dict['b'])
                else:
                    tmp.append(self.green_class_dict['a'])
                    
            crops.append(tmp)
            
        res = np.full((self.resize_height, self.resize_width, 3), (0, 0, 0))

        for i in range (self.num_vertical_grid):
            for j in range(self.num_horizontal_grid):
                res[i*self.grid_height:(i+1)*self.grid_height, j*self.grid_width:(j+1)*self.grid_width] = crops[i][j]
                
        return res