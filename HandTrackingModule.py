import cv2
import mediapipe as mp          # for skeletal hand model
import time                     # for checking frame rate
import numpy as np

# Changes(10.25)
# 1. 2 New function added 
#       * handDetector.KNN(self, mode_on=True, data_path='./DataSet.txt) 
#           -> make knn model instance
#       * handDetector.KNN_result(self, hand_index=0) 
#           -> get result through knn model
# 2. 2 Existing function changed
#       * handDetector.findHands() 
#           -> new parameter makes drawing hand index under the 0-indexed lm position
#       * handDetector.findPosition() 
#           -> return all hand Landmarks

# 손의 움직임을 감지하기 위한 클래스
# __init__ : mpHands, mpDraw와 같은 mediapipe 패키지의 Hands모듈 사용하는 인스턴스들을 구성
class handDetector():
    def __init__(self,
               static_image_mode=False,
               max_num_hands=2,
               model_complexity=1,
               min_detection_confidence=0.5,
               min_tracking_confidence=0.5):

        self.mode = static_image_mode
        self.maxHands = max_num_hands
        self.complexity = model_complexity
        self.detectionCon = min_detection_confidence
        self.trackingCon = min_tracking_confidence

        self.mpHands = mp.solutions.hands    # get mp.solutions.hands module
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.complexity,  # make Hands() class instance, use default
                                        self.detectionCon, self.trackingCon)        # for optimization, using non-static parameter                                                                                         
        self.mpDraw = mp.solutions.drawing_utils

        self.knn_isCreated = False
        
    # KNN인스턴스를 만드는 메서드
    # data_path에서 받은 데이터셋 텍스트파일을 np.genfromtxt() 메서드로 열어서 2차원 ndarray로 구성
    # 각 행의 맨 마지막 원소가 label이고, 처음부터 -2번째 원소가 각 landmark들의 각도에 관한 정보이다.
    # cv2.ml.KNearest_create() 메서드를 이용해 읽어들인 데이터로 empty knn distance(region) map을 구성하고 train()메서드를 통해 학습을 진행한다.
    # KNN distance map의 학습까지 완료되면 knn_isCreated라는 클래스 내부 부울변수를 이용해 KNN맵 생성 여부를 체크할 수 있다.
    def KNN(self, mode_on=True, data_path='./DataSet.txt'):
        file = np.genfromtxt(data_path, delimiter=',')
        angle = file[:,:-1].astype(np.float32)
        label = file[:, -1].astype(np.float32)
        self.knn = cv2.ml.KNearest_create()
        self.knn.train(angle, cv2.ml.ROW_SAMPLE, label)
        self.knn_isCreated = True

    # 손을 디텍팅하는 메서드
    # mediapipe의 모든 디텍터는 RGB이미지를 받기 때문에 OpenCV의 Videocapture()메서드를 통해 받은 BGR이미지를 RGB로 변환해야한다.
    # RGB로 변환된 이미지를 mediapipe Hands 모듈에 탑재된 soluctions.process()메서드에 입력하면 반환값으로 
    # 해당 이미지에서 탐지된 손의 Landmarks를 results변수에 저장한다.
    # 첫번째 if문에서 results의 값이 None이 아닌 경우에 이하 for루프가 동작한다.
    # for 루프에서는 mpDraw 인스턴스의 draw_landmarks() 메서드를 이용해 입력된 이미지 위에 손의 Landmarks와 그 연결을 그린다.
    # 두번째 if문에서 draw_hand_index가 True라면 각 landmark 위치에 해당 landmark 인덱스를 그린다.
    # 합성된 RGB이미지를 반환한다.
    def findHands(self, img, draw_hand_index=False):

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                                    # mphands use only RGB images but cv2 images are BGR images.
                                    # So, it is necessary to convert

        self.results = self.hands.process(imgRGB)

        #print(results.multi_hand_landmarks)                # for checking hand position

        if self.results.multi_hand_landmarks:            
            for index, handLms in enumerate(self.results.multi_hand_landmarks):    # handLms is a single hand!
                self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)         # draw landmarks points and connections on img
                
                if draw_hand_index:
                    cv2.putText(img=img, text=str(index), 
                    org=(int(handLms.landmark[0].x * img.shape[1] - 10), int(handLms.landmark[0].y * img.shape[0] + 40)),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255,255,255), thickness=3)
        return img

    # ratio로 제공되는 landmarks의 값을 이미지 크기(windowsize)에 맞춰 정수로 변환하는 함수
    # realscale이 True라면 입력된 windowsize에 맞춰 변환되고, False라면 입력된 이미지 크기에 맞춰 자동 변환된다.
    # 변환된 값들은 리스트 형식으로 lmList에 append된다.
    # cz값은 활용하지 않는데, 2차원 화면에 사용하는 데에는 3차원 축이 필요 없기 때문이다.
    def findPosition(self, img, realscale=False, windowsize=[], 
                        draw=False, scale_ratio=1, bias_ratio=0
    ):                                                                  # 개선점 : 맨 처음에 탐지되던 손만 추적탐지하는것이 아니라 새로 탐지한 손의 handNo가 
                                                                        # 0번 인덱스가 되어서 손이 왔다갔다 하면 디텍팅이 안된다.
        lmList = []

        if self.results.multi_hand_landmarks:
            for myHand in self.results.multi_hand_landmarks:
                temp = []
                for id, lm in enumerate(myHand.landmark):    # 0~20 landmarks
                    #print(id)                               # id point
                    #print(lm)                               # landmark position(x, y, z), These values are ratio

                    if realscale:
                        cx, cy = int(lm.x*windowsize[0]*scale_ratio - windowsize[0]*bias_ratio), int(lm.y*windowsize[1]*scale_ratio - windowsize[1]*bias_ratio)
                    else :
                        h, w, c = img.shape                      # get img's height, width, channel
                        cx, cy = int(lm.x*w), int(lm.y*h)        # get current x, y coordinate in integer               

                    temp.append([id, cx, cy])              # landmarks(0~20) are added to lmList consequently
                    # print([id, cx, cy])                    # print coordinates and ids

                    if draw: 
                        cv2.circle(img, (cx, cy), 8, (255, 255, 0), cv2.FILLED)
                        cv2.putText(img, str(id), (cx, cy-10), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3 )

                lmList.append(temp)

        return lmList

    # 학습된 KNN distance map 에 현재 landmarks를 입력하여 어떤 제스처인지 확인하는 메서드이다.
    # 각 손의 landmarks를 정해진 순서에 맞춰 벡터연산한 뒤에 정규화 해준다.
    # 정규화 된 값들을 각도로써 비교하기 위해 아인슈타인합(einsum())을 취한 값에 arccos을 취한다.
    # 이렇게 얻은 값은 라디안 값이기 때문에 사람이 해석하기 쉬운 60분법으로 np.degrees(angle) 메서드를 이용해 변환시킨다.
    # 이렇게 얻은 각도값을 float32타입 ndarray로 만든 뒤 findNearest()메서드를 사용하여 key값을 취한다.
    # 얻은 key를 반환한다.
    def KNN_result(self, hand_index=0): # for One-hand landmarks 
        myHand = self.results.multi_hand_landmarks[hand_index]
        joint = np.zeros((21,3))
        for j, lm in enumerate(myHand.landmark):
            joint[j] = [lm.x, lm.y, lm.z]
        
        v1 = joint[[0, 1, 2, 3, 0, 5, 6, 7, 0,  9, 10, 11,  0, 13, 14, 15,  0, 17, 18, 19], :]
        v2 = joint[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], :]

        v = v2 - v1
        v = v / np.linalg.norm(v, axis=1)[:, np.newaxis]

        compareV1 = v[[0, 1, 2, 4, 5, 6, 7,  8,  9, 10, 12, 13, 14, 16, 17], :]
        compareV2 = v[[1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19], :]

        angle = np.arccos(np.einsum('nt,nt->n', compareV1, compareV2))

        angle = np.degrees(angle)

        data = np.array([angle], dtype=np.float32)
        ret, results, neighbours, dist = self.knn.findNearest(data,3)
        key = int(results[0][0])
        
        return key

    
    

    # def drawLMcircle(self, img, landmarks, COLOR, ):
    #     cv2.cir

def __main():
    cap = cv2.VideoCapture(0)       # using 0 indexed webcam
    pTime = 0                       # previous time
    cTime = 0                       # current time
    detector = handDetector()
    isFlipped = True

    while True:
        success, img = cap.read()
        img = cv2.resize(img, (1280,720))
        if isFlipped:
            img = cv2.flip(img, 1)
        detector.findHands(img, draw_hand_index=True)
        detector.KNN()
        All_lmList = detector.findPosition(img)
        for index, lmList in enumerate(All_lmList):
            # if len(lmList) != 0:
            #     print(index)
            #     print(lmList[4])        # if you want landmark N's position, input N for the index
            print(f'{index} hand : {detector.KNN_result(hand_index=index)}')

        # --- Draw FPS rate ---
        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)) + "FPS", (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3 )

        # image
        cv2.imshow("Hand Tracking Image", img)    # run webcam
        # cv2.imshow("Original Image", ori_img)    # run webcam

        if cv2.waitKey(1) != -1:    # for realtime
            break


if __name__ == "__main__":
    __main()