# 데이터 수집을 위한 프로그램

import mediapipe as mp
import numpy as np
import cv2
# import tkinter as tk
# from pynput import keyboard
import time


max_num_hands = 2

# 수집할 제스처
gesture = {
    0:'open', 1:'close', 2:'index_finger', 3:'Bunch'
}

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    max_num_hands = max_num_hands,
    min_detection_confidence = 0.5,
    min_tracking_confidence = 0.5
)

# 수집한 데이터가 저장될 위치
f = open('./Training/test.txt', 'w')

# 테스트 학습
file = np.genfromtxt('./Training/DataSet.txt', delimiter=',')

angleFile = file[:,:-1]
labelFile = file[:,-1]

angle = angleFile.astype(np.float32)
label = labelFile.astype(np.float32)

knn = cv2.ml.KNearest_create()
knn.train(angle, cv2.ml.ROW_SAMPLE, label)

cap = cv2.VideoCapture(0)

startTime = time.time()
prev_index = 0
sentence = ''
recognizeDelay = 1

while True:
    ret, img = cap.read()
    if not ret:
        continue
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(imgRGB)

    pressed_key = cv2.waitKey(1) # 키 입력

    if result.multi_hand_landmarks is not None:
        for res in result.multi_hand_landmarks:
            joint = np.zeros((21, 3))
            for j, lm in enumerate(res.landmark):
                joint[j] = [lm.x, lm.y, lm.z]
            
            v1 = joint[[0, 1, 2, 3, 0, 5, 6, 7, 0,  9, 10, 11,  0, 13, 14, 15,  0, 17, 18, 19], :]
            v2 = joint[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], :]

            v = v2 - v1
        
            v = v / np.linalg.norm(v, axis=1)[:, np.newaxis]

            compareV1 = v[[0, 1, 2, 4, 5, 6, 7,  8,  9, 10, 12, 13, 14, 16, 17], :]
            compareV2 = v[[1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19], :]

            angle = np.arccos(np.einsum('nt,nt->n', compareV1, compareV2))

            angle = np.degrees(angle)

            # opencv창 활성화 상태에서 a키 입력시 test.txt에 저장
            if pressed_key == 97:
                for num in angle:
                    num = round(num, 6)
                    f.write(str(num))
                    f.write(',')
                f.write("3.000000") # change Intager part to dict_key which you want to get data
                f.write('\n')
                print("next")


            data = np.array([angle], dtype=np.float32)
            ret, results, neighbours, dist = knn.findNearest(data,3)
            index = int(results[0][0])

            if index in gesture.keys():
                cv2.putText(img=img, text=gesture[index].upper(), 
                            org=(int(res.landmark[0].x * img.shape[1] - 10), int(res.landmark[0].y * img.shape[0] + 40)),
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255,255,255), thickness=3)
            
            mp_drawing.draw_landmarks(img, res, mp_hands.HAND_CONNECTIONS)

    cv2.imshow('HandTracking', img)
    if pressed_key != -1 and pressed_key != 97:
        break

f.close()



