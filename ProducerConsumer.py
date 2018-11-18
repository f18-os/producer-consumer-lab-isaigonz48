#!/usr/bin/env python3

import threading
import time
from threading import Thread
import cv2
import numpy as np
import base64
import queue


class ExtractThread(Thread):
    def __init__(self, filename, extractionQueue):
        Thread.__init__(self, daemon=False)
        self.fname = filename
        self.eQueue = extractionQueue
        self.start()
    def run(self):
        extractFrames(self.fname,self.eQueue)
        print("THREAD 1 DONE")
        self.eQueue.doneInput = 1
    
class ConvertThread(Thread):
    def __init__(self, extractionQueue, convertedQueue):
        Thread.__init__(self, daemon=False)
        self.eQueue = extractionQueue
        self.cQueue = convertedQueue
        self.start()
    def run(self):
        ConvertToGrayscale(self.eQueue, self.cQueue)
        print("THREAD 2 DONE")
        self.cQueue.doneInput = 1


class DisplayThread(Thread):
    def __init__(self, convertedQueue):
        Thread.__init__(self, daemon=False)
        self.cQueue = convertedQueue
        self.start()
    def run(self):
        displayFrames(self.cQueue)
        print("THREAD 3 DONE")

class ProConQueue(queue.Queue):
    def __init__(self,size):
        queue.Queue.__init__(self,size)
        self.doneInput = 0
        self.doneOutput = 0
    def pcPut(self, something):
        self.put(something)

    def pcGet(self):
        if(self.doneInput == 1):
            if(self.empty()):
                doneOutput = 1
                return
            return self.get()
        
        else:
            startTime = 0 #time() + 0
            while self.empty():
                time.sleep(.1)
                startTime += 1
                if(startTime == 10):
                    self.doneOutput = 1
                    break
            return self.get()

def extractFrames(fileName, outputBuffer):
    # Initialize frame count 
    count = 0

    # open video file
    vidcap = cv2.VideoCapture(fileName)
    
    # read first image
    success,image = vidcap.read()
    
    print("Reading frame {} {} ".format(count, success))
    while success:
        # get a jpg encoded frame
        success, jpgImage = cv2.imencode('.jpg', image)
        
        #encode the frame as base 64 to make debugging easier
        jpgAsText = base64.b64encode(jpgImage)
        
        # add the frame to the buffer
        outputBuffer.pcPut(jpgAsText)
       
        success,image = vidcap.read()
        print('Reading frame {} {}'.format(count, success))
        count += 1

    print("Frame extraction complete")

def ConvertToGrayscale(inputBuffer, outputBuffer):
    count = 0

    while True:
        #########
        ######### INPUTTTT
        frameAsText = inputBuffer.pcGet()
        
        # decode the frame 
        if(not frameAsText):
            break
        jpgRawImage = base64.b64decode(frameAsText)

        # convert the raw frame to a numpy array
        jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)
        
        # get a jpg encoded frame
        img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED)
        ########
        print("Converting frame {}".format(count))
        
        grayscaleFrame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        success, grayImg = cv2.imencode('.jpg',grayscaleFrame)

        if(success):
            grayAsText = base64.b64encode(grayImg)
            outputBuffer.pcPut(grayAsText)
        
        count += 1
        if(inputBuffer.doneOutput == 1):
            break

    print("Finisshed grayscaling all queue")

    
def displayFrames(inputBuffer):
    # initialize frame count
    count = 0

    while True:
        # get the next frame
        frameAsText = inputBuffer.pcGet()
        if(not frameAsText):
            break
        # decode the frame 
        jpgRawImage = base64.b64decode(frameAsText)

        # convert the raw frame to a numpy array
        jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)
        
        # get a jpg encoded frame
        img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED)

        print("Displaying frame {}".format(count))        

        # display the image in a window called "video" and wait 42ms
        # before displaying the next frame
        cv2.imshow("Video", img)
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break

        count += 1
        if(inputBuffer.doneOutput == 1):
            break

    print("Finished displaying all frames")
    
    cv2.destroyAllWindows()

filename = 'clip.mp4'

extractionQueue = ProConQueue(10)
convertedQueue = ProConQueue(10)

ExtractThread(filename, extractionQueue)
ConvertThread(extractionQueue, convertedQueue)
DisplayThread(convertedQueue)
