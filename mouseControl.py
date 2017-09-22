import cv2
import numpy as np
from pynput.mouse import Button, Controller
import wx

mouse = Controller()
app = wx.App(False)
(sx,sy) = wx.GetDisplaySize() #wx.GetDisplaySize() to get the screen resolution
(camx,camy) = (int(sx),int(sy))

lowerBound = np.array([33,80,40])
upperBound = np.array([102,255,255])

kernelOpen = np.ones((5,5))
kernelClose = np.ones((20,20))

mOld = np.array([0,0])
mouseLoc=np.array([0,0])
damp = 2
cam = cv2.VideoCapture(0)

pinch = 0

while True:
    check, img = cam.read()
    img = cv2.resize(img, (camx,camy))

    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(imgHSV,lowerBound,upperBound)

    maskOpen = cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)
    maskClose = cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)

    maskFinal = maskClose
    counts, h = cv2.findContours(maskFinal.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2:]

    if(len(counts)==2):
        if(pinch==1):
            pinch=0
            mouse.release(Button.left)
        x1,y1,w1,h1 = cv2.boundingRect(counts[0])
        x2,y2,w2,h2 = cv2.boundingRect(counts[1])

        cv2.rectangle(img, (x1,y1), (x1+w1,y1+h1), (255,0,0),2)
        cv2.rectangle(img, (x2,y2), (x2+w2,y2+h2), (255,0,0),2)

        cx1 = int(x1+w1/2)
        cy1 = int(y1+h1/2)

        cx2 = int(x2+w2/2)
        cy2 = int(y2+h2/2)

        cx = int((cx1+cx2)/2)
        cy = int((cy1+cy2)/2)

        cv2.line(img,(cx1,cy1), (cx2,cy2),(255,0,0),2)
        cv2.circle(img, (cx,cy), 2, (0,0,255),2)
        mouseLoc = mOld + ((cx,cy)-mOld)/damp
        #mouseLoc=(int((mouseLoc[0]*sx)/camx), int((mouseLoc[1]*sy)/camy))
        tloc = (cx,cy)
        mouse.position= tloc
        while mouse.position!=tloc:
            pass
    elif(len(counts)==1):
        #https://scratch.mit.edu/projects/124331/
        x,y,w,h = cv2.boundingRect(counts[0])
        if(pinch==0):
            pinch=1
            mouse.press(Button.left)
        cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0),2)

        cx = int(x+w/2)
        cy = int(y+h/2)

        cv2.circle(img,(cx,cy),int((w+h)/4),(0,0,255),2)

        mouseLoc = (mOld + ((cx,cy)-mOld)/damp)
        #mouseLoc=(int((mouseLoc[0]*sx)/camx), int((mouseLoc[1]*sy)/camy))
        tloc = (cx,cy)
        mouse.position= tloc
        while mouse.position!=tloc:
            pass

    cv2.imshow("cam", img)
    if cv2.waitKey(1) == ord('q'):
        break

#Important Links - 
#https://pypi.python.org/pypi/pynput
#https://stackoverflow.com/questions/10948589/choosing-correct-hsv-values-for-opencv-thresholding-with-inranges
