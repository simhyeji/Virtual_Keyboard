import cv2
import numpy

cap = cv2.VideoCapture(0)

while True:
    ret, img = cap.read()

    k = cv2.waitKey(1)
    print(k)

    # 각도 보정





    cv2.imshow("test", img)
    if k != -1:
        print(k)
        break

# f : 102