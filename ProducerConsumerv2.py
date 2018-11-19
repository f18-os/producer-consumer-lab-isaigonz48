#!/usr/bin/env python3

import threading
import time
from threading import Thread
from threading import Lock
import cv2
import numpy as np
import base64
#import queue

class Q:
    def __init__(self, initArray = []):
        self.a = []
        self.a = [x for x in initArray]
    def put(self, item):
        self.a.append(item)
    def get(self):
        a = self.a
        item = a[0]
        del a[0]
        return item
    def __repr__(self):
        return "Q(%s)" % self.a

class ExtractThread(Thread):
    def __init__(self, filename, extractionQueue):
        Thread.__init__(self, daemon=False)
        self.fname = filename
        ##### Kept mostly the same naming convention as used in ExtractAndDisplay.py
        self.outputBuffer = extractionQueue
        self.start()
    def run(self):
        self.extractFrames()
        print("---Extract thread done---")
        ##### Signals that there will be no more inputting into the queue
        self.outputBuffer.doneInput = 1

    def extractFrames(self):
        ##### Mostly code from ExtractAndDisplay.py
        count = 0

        vidcap = cv2.VideoCapture(self.fname)
    
        success,image = vidcap.read()
    
        print("Reading frame {} {} ".format(count, success))
        while success:
            success, jpgImage = cv2.imencode('.jpg', image)
        
            jpgAsText = base64.b64encode(jpgImage)
        
            self.outputBuffer.pcPut(jpgAsText)
        
            success,image = vidcap.read()
            print('Reading frame {} {}'.format(count, success))
            count += 1

        #print("Frame extraction complete")

        
class ConvertThread(Thread):
    def __init__(self, extractionQueue, convertedQueue):
        Thread.__init__(self, daemon=False)
        ##### Get frames from extractionQueue, put frames into convertedQueue
        self.inputBuffer = extractionQueue
        self.outputBuffer = convertedQueue
        self.start()
    def run(self):
        self.ConvertToGrayscale()
        print("---Converting thread done---")
        self.outputBuffer.doneInput = 1


    def ConvertToGrayscale(self):
        count = 0
        
        while True:
            frameAsText = self.inputBuffer.pcGet()
            
            if(not frameAsText):
                break

            jpgRawImage = base64.b64decode(frameAsText)
            
            jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)
            
            img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED)
            
            print("Converting frame {}".format(count))
            
            grayscaleFrame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            ##### After converting to gray, must encode it as text (opposite of when it got decoded)
            ##### Code like the Extract method
            
            success, grayImg = cv2.imencode('.jpg',grayscaleFrame)
            
            if(success):
                grayAsText = base64.b64encode(grayImg)
                self.outputBuffer.pcPut(grayAsText)
                
            count += 1
            ##### If all the frames have been output (Not really needed because of the code that checks if pcGet() return None, but just in case
            if(self.inputBuffer.doneOutput == 1):
                break

        #print("Finished grayscaling all queue")

        
class DisplayThread(Thread):
    def __init__(self, convertedQueue):
        Thread.__init__(self, daemon=False)
        self.inputBuffer = convertedQueue
        ##### Wasn't exactly sure how to get 24 fps, so I just used the number used in DisplayFrames.py
        self.frameDelay = 42
        self.start()
    def run(self):
        self.displayFrames()
        print("---Displaying thread done---")

    def displayFrames(self):
        # initialize frame count
        count = 0

        while True:

            startTime = time.time()

            ##### Mostly from ExtractAndDisplay.py
            frameAsText = self.inputBuffer.pcGet()

            ##### If pcGet() returned None, then there are no more frames
            if(not frameAsText):
                break
            
            jpgRawImage = base64.b64decode(frameAsText)

            jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)
        
            img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED)
            
            print("Displaying frame {}".format(count))        
            
            cv2.imshow("Video", img)

            ##### Mostly from DisplayFrames.py
            elapsedTime = int((time.time() - startTime) * 1000)
            #print("Time to process frame {} ms".format(elapsedTime))
    
            timeToWait = max(1, self.frameDelay - elapsedTime)
            
            if cv2.waitKey(timeToWait) and 0xFF == ord("q"):
                break    

            count += 1

            if(self.inputBuffer.doneOutput == 1):
                break
            
        #print("Finished displaying all frames")
    
        cv2.destroyAllWindows()

##### The producer consumer queue
class ProConQueue(Q):
    def __init__(self,size, lock):
        Q.__init__(self)

        self.lock = lock
        self.maxSize = 10
        self.size = 0
        ##### 1 if no more input is expected
        self.doneInput = 0
        ##### 1 if no more output is expected
        self.doneOutput = 0

    ##### pcPut and pcGet (producer consumer put/get)
    def pcPut(self, something):
        startTime = 0
        ##### Checks if the queue is full (size == 10)
        ##### If it is, sleep for .01 seconds and then try again
        while(self.size == 10):
            time.sleep(.01)
            startTime += 1
            if(startTime == 500):
                self.doneInput = 1
                break
        self.lock.acquire()
        self.size += 1
        self.put(something)
        self.lock.release()
        
    def pcGet(self):
        ##### No more input is expected, so get until the queue is empty, return None when empty
        if(self.doneInput == 1):
            if(self.empty()):
                self.doneOutput = 1
                return
            self.lock.acquire()
            self.size -= 1
            item = self.get()
            self.lock.release()
            return item
        ##### If the queue is still receiving input, get if the queue is not empty
        ##### otherwise, sleep for .01 seconds (No reason for .1), then increase counter nd try again
        ##### If the counter reaches 500, 5 second have passed and the queue has not received input, so it will be assumed that no more is expected from the queue 
        else:
            startTime = 0
            while self.empty():
                time.sleep(.01)
                startTime += 1
                if(startTime == 500):
                    self.doneOutput = 1
                    break
                
            self.lock.acquire()
            self.size -= 1
            item = self.get()
            self.lock.release()
            return item

    def empty(self):
        return self.size == 0
filename = 'clip.mp4'

##### One queue shared by extraction and convertion, and one shared by convertion and displaying. Each queue uses different lock
extractionLock = Lock()
convertedLock = Lock()

extractionQueue = ProConQueue(10, extractionLock)
convertedQueue = ProConQueue(10, convertedLock)

ExtractThread(filename, extractionQueue)
ConvertThread(extractionQueue, convertedQueue)
DisplayThread(convertedQueue)
