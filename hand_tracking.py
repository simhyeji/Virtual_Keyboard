import cv2
import mediapipe as mp          # for skeletal hand model
import time                     # for checking frame rate
import copy

cap = cv2.VideoCapture(0)       # using 0 indexed webcam

mpHands = mp.solutions.hands    # get mp.solutions.hands module

hands = mpHands.Hands(False)    # make Hands() class instance, use default
                                # for optimization, using non-static parameter

mpDraw = mp.solutions.drawing_utils




# FPS rate
pTime = 0   # previous time
cTime = 0   # current time


while True:



    success, img = cap.read()   # success : bool, img : ndarray img
    #ori_img = img              # This is Shallow copy
    # ori_img = copy.deepcopy(img)    # This is Deep copy

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                                # mphands use only RGB images but cv2 images are BGR images.
                                # So, it is necessary to convert

    results = hands.process(imgRGB)

    #print(results.multi_hand_landmarks)                # for checking hand position

    if results.multi_hand_landmarks:            
        for handLms in results.multi_hand_landmarks:    # handLms is a single hand!
            for id, lm in enumerate(handLms.landmark):
                #print(id)                               # id point
                #print(lm)                               # landmark position(x, y, z), These values are ratio

                h, w, c = img.shape                     # get img's height, width, channel
                cx, cy = int(lm.x*w), int(lm.y*h)       # get current x, y coordinate in integer
                # print([id, cx, cy])                     # print coordinates and ids

                #if id == 4:
                cv2.circle(img, (cx, cy), 15, (255, 255, 0), cv2.FILLED)

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)         # draw landmarks points and connections on img


    # --- Draw FPS rate ---
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, str(int(fps)) + "FPS", (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3 )

    cv2.polylines()


    # image
    cv2.imshow("Hand Tracking Image", img)    # run webcam
    # cv2.imshow("Original Image", ori_img)    # run webcam

    if cv2.waitKey(1) != -1:    # for realtime
        break