import cv2
import HandTrackingModule as HTM
import KeyboardModule as KM
import time
import mouse
from pynput import keyboard as kb
import numpy as np


controller = kb.Controller()

cap = cv2.VideoCapture(0)       # using 0 indexed webcam
pTime = 0                       # previous time
cTime = 0                       # current time
detector = HTM.handDetector()
isFlipped = True

x_size, y_size = 1280, 720
scale_ratio = 1                 # for DPI setting
bias_ratio = 0                  # for DPI setting
windowsize = [x_size, y_size]

x_base, y_base = int(x_size * 0.01), int(y_size * 0.01)
x_avg, y_avg = int(), int()
MPosHist = []                   # elements for getting average point to calibrate wobblling mouse pointer
MPosHist_size = 10

points = np.array([[500, 500], [500, 600], [600, 600], [600, 500]], np.int32)
blue_color= (255,0,0)

while True:
    success, img = cap.read()
    img = cv2.resize(img, (1280,720))

    if isFlipped:
        img = cv2.flip(img, 1)
    detector.findHands(img)
    lmList = detector.findPosition(img, realscale=True, windowsize=windowsize, scale_ratio=scale_ratio, bias_ratio=bias_ratio)
    if len(lmList) != 0:
        # print(lmList[4])        # if you want landmark N's position, input N for the index
                    
        # mouse.move(lmList[8][1], lmList[8][2], absolute=True, duration=0 )
        print(lmList[8][1:])
        MPosHist.append(lmList[8][1:])
        if len(MPosHist) > MPosHist_size:
            del(MPosHist[0])

        # boundary condition
        if (points[0][0] < lmList[8][1]) and (lmList[8][1] < points[2][0]) :
            if (points[0][1] < lmList[8][2]) and (lmList[8][2] < points[2][1]) :
                print("yes")
                controller.press('a')
                controller.release('a')
                print("success")
                
    
    if len(MPosHist) == MPosHist_size:                  # mouse wobblling calibration Using L1 norm
        x_avg, y_avg = int(np.mean([MPosHist[xpos][0] for xpos in range(MPosHist_size-1)])), int(np.mean([MPosHist[xpos][1] for xpos in range(MPosHist_size-1)]))

        if (abs(MPosHist[MPosHist_size-1][0] - x_avg) > x_base) or (abs(MPosHist[MPosHist_size-1][1] - y_avg) > y_base):
            x_avg, y_avg = int(np.mean([MPosHist[xpos][0] for xpos in range(MPosHist_size)])), int(np.mean([MPosHist[xpos][1] for xpos in range(MPosHist_size)]))
            mouse.move(MPosHist[MPosHist_size-1][0], MPosHist[MPosHist_size-1][1], absolute=True, duration=0)
        else:
            mouse.move(x_avg, y_avg, absolute=True, duration=0)

    
        
    # --- draw key ---
    img = cv2.polylines(img, [points], True, blue_color, 1)

    # --- Draw FPS rate ---
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)) + "FPS", (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3 )

    # image
    cv2.imshow("Hand Tracking Image", img)    # run webcam
    # cv2.imshow("Original Image", ori_img)    # run webcam
    if cv2.waitKey(1) != -1:
        break

def main():

    return 0

if __name__ == "__main__":
    main()