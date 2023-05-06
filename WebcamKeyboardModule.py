from pynput.keyboard import Key, Controller
import HandTrackingModule as HTM
import KeyboardModule as KM
import cv2
import numpy as np
import time

# Changes (11.01)
# 1. 187 line -> special key error corrected


# 웹캠의 사용을 전제하는 키보드 클래스
# 기존 KeyboardModule의 Keyboard클래스의 자식 클래스이다.
# HandTrackingModule의 handDetector클래스도 동시에 활용한다.
class Webcam_keyboard(KM.Keyboard):
    def __init__(self, window_size) :
        super().__init__(window_size)

        self.cap = cv2.VideoCapture(0)
        self.controller = Controller()
        self.detector = HTM.handDetector()

        self.c_key = [str(), str()]
        self.p_key = [str(), str()]
        self.base_time = [int(), int()]
        self.delta_time = [int(), int()]

        self.Wait_time = 500000000 # 0.5s in ns

        # 특수키를 pynput에 활용하기 위한 딕셔너리
        self.key_dict = {
            "backspace"     : Key.backspace,
            "tab"           : Key.tab,
            #"caps_lock"     : Key.caps_lock,
            "enter"         : Key.enter,
            #"shift"         : Key.shift,
            "ctrl"          : Key.ctrl,
            "space"         : Key.space,
            "alt"           : Key.alt,
            "left"          : Key.left,
            "right"         : Key.right,
            "up"            : Key.up,
            "down"          : Key.down
        }

        self.pTime = 0
        self.cTime = 0

        self.isFlipped = True
        self.is_inBoundary = [False, False]
        
        self.lmList = []
        self.diag_points = self.get_diag_keyposition()

        self.Keyboard_on = True
        self.knn_base_time = 0
        self.knn_delta_time = 0
        self.knn_Wait_time = 500000000 # 0.5s in ns

    # 키보드를 그리는 함수
    # knn이 동작중이라면, knn의 결과물이 0인 경우 이면서 check_gesturetime이 True인 경우에 키보드를 껏다가 킬 수 있게 구현
    # knn을 사용하지 않는다면, 손의 개수에 따라 키보드 바운더리, 키보드 입력등의 경우에 대응하도록 구현
    # 이후 키보드를 그리고 FPS를 좌측상단에 그린다.
    def run_keyboard(self, Usingimshow):
        self.Usingimshow = Usingimshow
        knn_result = [None, None]
        if self.cap.isOpened():
            ret, self.img = self.cap.read()
            self.img = cv2.resize(self.img, (self.window_size[1], self.window_size[0]))
            self.img_Flip()

            self.detector.findHands(self.img)
            self.lmList = self.detector.findPosition(
                self.img, realscale=True, 
                windowsize=[self.window_size[1], self.window_size[0]]
            )
            
            ###########################################
            ## Code Position for gesture recognition ##
            ###########################################
            
            if self.detector.knn_isCreated :
                if len(self.lmList) == 1:
                    knn_result[0] = self.detector.KNN_result()
                elif len(self.lmList) == 2:
                    for hand_index in range(2):
                        knn_result[hand_index] = self.detector.KNN_result(hand_index=hand_index)

            if (0 in knn_result) and self.check_gestureTime():
                if not self.Keyboard_on:
                    print("1")
                    self.Keyboard_on = True
                else:
                    print("2")
                    self.Keyboard_on = False


            # 클래스 내부에서 작동하기 때문에 이미지 업데이트과정이 불필요
            # self.get_image(self.img) 

            if ret and self.Keyboard_on:
            # 손이 두개인 경우와 한개인 경우 분기
                # 손이 1개인 경우
                if len(self.lmList) == 1:
                    hand_num = 1
                
                # 손이 2개인 경우
                elif len(self.lmList) == 2:
                    hand_num = 2
                
                # 손이 0개 혹은 3개 이상 나오는 경우
                else :
                    pass

                if len(self.lmList) != 0:
                    # --- boundary condition ---
                    self.check_boundary(hand_num=hand_num)

                    # --- To measure how long the c_key keeps ---
                    self.check_ckey_Keeps(hand_num=hand_num)

                # --- Draw Keyboard ---
                self.drawing_keyboard()

            # --- Draw FPS rate ---
            self.draw_fps_rate()

    # 특정 제스처가 수행된 뒤에 그것을 재인식하기까지 필요한 딜레이를 구현한 함수
    def check_gestureTime(self):
        temp = time.time_ns()
        if self.knn_delta_time == 0:
            self.knn_delta_time = temp
        else :
            self.knn_base_time = temp - self.knn_delta_time
            self.knn_delta_time = temp

        if self.knn_base_time > self.knn_Wait_time:
            self.knn_delta_time = 0
            self.knn_base_time = 0
            return True
        else :
            return False

    # OpenCV의 imshow메서드로 opencv윈도우를 켜게하는 메서드
    def run_CV_window(self):
        if self.Usingimshow:
            cv2.imshow("test", self.img)
            if cv2.waitKey(1) != -1:
                return True
            else :
                return False

    # 현재 FPS를 그리는 메서드
    def draw_fps_rate(self):
        self.cTime = time.time()
        fps = 1/(self.cTime-self.pTime)
        self.pTime = self.cTime
        cv2.putText(
            self.img, str(int(fps)) + "FPS", (10, 70), 
            cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3 )

    # 현재 입력된 키가 얼마나 지속되는지 계산하고 지속 시간에 맞춰 키입력을 수행하는 메서드
    def check_ckey_Keeps_base(self, iter):
        if self.c_key[iter] != self.p_key[iter]:
                self.p_key[iter] = self.c_key[iter]
                self.base_time[iter] = 0
                self.delta_time[iter] = 0

        elif self.is_inBoundary[iter] :
            temp = time.time_ns()
            if self.delta_time[iter] == 0:
                self.delta_time[iter] = temp

            else :
                self.base_time[iter] += temp - self.delta_time[iter]
                self.delta_time[iter] = temp
            
            if self.base_time[iter] > self.Wait_time:
                print(f'iter = {iter}, base_time = {self.base_time[iter]}')
                try:
                    print(f"try block : c_key = {self.c_key[iter]}")
                    self.controller.press(self.c_key[iter])
                    self.controller.release(self.c_key[iter])
                except ValueError:
                    if self.c_key[iter] in ('Lng', 'shift_l', 'shift_r', 'caps_lock', 'OPT_l', 'OPT_r'):
                        print("Key Changed!")
                        self.change_key(self.c_key[iter])
                        self.diag_points = self.get_diag_keyposition()
                    else :
                        print(f"except block : c_key = {self.c_key[iter]}")
                        self.controller.press(self.key_dict[self.c_key[iter]])
                        self.controller.release(self.key_dict[self.c_key[iter]])
                except:
                    pass

                self.base_time[iter]  = 0
                self.delta_time[iter] = 0

    # 손의 개수에 따라서 개형이 약간 달라지는 점을 보완하기 위해 구현된 check_ckey_Keeps_base의 상위 모듈 함수
    def check_ckey_Keeps(self, hand_num=1):
        if hand_num == 1:
            self.check_ckey_Keeps_base(iter=hand_num-1)

        elif hand_num == 2:
            for i in range(hand_num):
                self.check_ckey_Keeps_base(iter=i)
        else :
            pass

    
    # 키보드 바운더리에 특정 landmark좌표(여기서는 8번::검지손가락 가장 끝 랜드마크)가 키보드 바운더리에 들어와 있는지 확인하는 메서드
    def check_boundary_base(self, iter=1):
        for key, points in self.diag_points.items():
                if (points[0][0] < self.lmList[iter][8][1]) and (self.lmList[iter][8][1] < points[1][0]) :
                        if (points[0][1] < self.lmList[iter][8][2]) and (self.lmList[iter][8][2] < points[1][1]) :
                                self.c_key[iter] = key
                                self.is_inBoundary[iter] = True
                                break
                        else:
                            self.is_inBoundary[iter] = False
                else:
                    self.is_inBoundary[iter] = False

    # 손의 수에 따라 변경되는점을 보완하기 위해 구현한 check_boundary_base의 상위 모듈 메서드
    def check_boundary(self, hand_num=1):
        if hand_num == 1:
            self.check_boundary_base(iter=hand_num-1)
            return self.is_inBoundary

        elif hand_num == 2 :
            for i in range(hand_num):
                self.check_boundary_base(iter=i)
            return self.is_inBoundary

        else :
            pass
    
    # 이미지 반전 메서드
    def img_Flip(self):
        if self.isFlipped:
            self.img = cv2.flip(self.img, 1)




def __main():
    size_x, size_y, channel_ = 1280, 720, 3
    webcam_keyboard = Webcam_keyboard(window_size=(size_y, size_x, channel_))
    Usingimshow = True

    while True:
        webcam_keyboard.run_keyboard(Usingimshow)
        if webcam_keyboard.run_CV_window():
            break

if __name__ == "__main__":
    __main()

