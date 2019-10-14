import cv2
import numpy as np
import pyautogui
import random
import time


class Search:
    '''
input :
image : path to the image file (see opencv imread for supported types)
precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8
debugg: if true its will save the captured region and write output image with boxes drawn around occurances dufault is False
'''
    def __init__(self, image, precision=0.8, debugg=False):
        self.image=image
        self.precision=precision
        self.debugg=debugg

    '''
Searchs for an image on the screen

returns :
the top left corner coordinates of the element if found as an array [x,y] or [-1,-1] if not

    '''
    def imagesearch(self):

        im = pyautogui.screenshot()
        if self.debugg==True:
            im.save('testarea.png')# usefull for debugging purposes, this will save the captured region as "testarea.png"
        img_rgb = np.array(im)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(self.image, 0)
        template.shape[::-1]

        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val < self.precision:
            return [-1,-1]
        return max_loc

    '''
Searchs for an image on screen continuously until it's found.

input :
time : Waiting time after failing to find the image 

returns :
the top left corner coordinates of the element if found as an array [x,y] 

    '''
    def imagesearch_loop(self, timesample):
        pos = self.imagesearch()
        while pos[0] == -1:
            print(image+" not found, waiting")
            time.sleep(timesample)
            pos = imagesearch(image, precision)
        return pos

    '''
Searchs for an image on screen continuously until it's found or max number of samples reached.

input :
time : Waiting time after failing to find the image
maxSamples: maximum number of samples before function times out.

returns :
the top left corner coordinates of the element if found as an array [x,y] 

    '''
    def imagesearch_numLoop(self, timesample, maxSamples):
        pos = self.imagesearch()
        count = 0
        while pos[0] == -1:
            print(image+" not found, waiting")
            time.sleep(timesample)
            pos = imagesearch(self.image, self.precision)
            count = count + 1
            if count>maxSamples:
                break
        return pos

    '''
Searches for an image on the screen and counts the number of occurrences.

returns :
the number of times a given image appears on the screen.
optionally an output image with all the occurances boxed with a red outline.

    '''
    def imagesearch_count(self):
        img_rgb = pyautogui.screenshot()
        img_rgb = np.array(img_rgb)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(self.image, 0)
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= self.precision)
        count = 0
        for pt in zip(*loc[::-1]):  # Swap columns and rows
            if self.debugg==True:

                cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)# to draw boxes around found occurances

            count = count + 1
        if self.debugg==True:

            cv2.imwrite('result.png', img_rgb)#to write output image with boxes drawn around occurances
        return count
