# Main program
import WebcamKeyboardModule as WKM
import cv2
import tkinter as tk
import threading
from PIL import Image, ImageTk
import time
import numpy as np

# tkinter을 활용하기 위한 클래스
class tk_window():
    def __init__(self, window:tk.Tk, win_size_x='1300', win_size_y='800', win_pos_x='300', win_pos_y='300'):
        self.window = window
        self.window.title("test1")
        self.window.geometry(win_size_x + 'x' + win_size_y + '+' + win_pos_x + '+' + win_pos_y)
        self.window.resizable(False, False)

        self.imgtk = None

        button1 = tk.Button(self.window, text="close", overrelief="solid", width=15, command=self.window_close, repeatdelay=1000, repeatinterval=100)
        button1.pack()

        self.label = tk.Label(self.window, image=self.imgtk)
        self.label.pack()

        self.entry = tk.Entry(self.window)
        self.entry.pack()
        self.entry.focus()

    # close 버튼에 할당하기 위한 창닫기 메서드
    def window_close(self):
        print("close")
        self.window.quit()

    # tkinter 이미지를 올리기 위한 메서드
    # tkinter에 올릴 수 있는 이미지는 ImageTK타입 이미지이기 떄문에 그 타입으로 변환해 준 것
    # 이후 label.image에 imgtk를 assign하는 것으로 tkwindow상의 이미지 업데이트를 구현, while루프에서 동작한다면 이것이 영상이 된다.
    def convert_tkimage(self, cv_image):
        RGB = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(RGB)
        self.imgtk = ImageTk.PhotoImage(image=img)

        self.label.config(image=self.imgtk)
        self.label.image = self.imgtk

# 스레드 상에서 WebcamKeyboard 클래스를 활용하기 위해 만든 상속 클래스
class Cam_Thread(WKM.Webcam_keyboard):
    def __init__(self, tk_win:tk_window, window_size, Usingimshow):
        super().__init__(window_size)
        self.tkimg = []
        self.tk_window = tk_win
        self.Usingimshow = Usingimshow
    
    # while 루프를 돌리기 위한 메서드
    # 별개의 스레드에서 동작하기 때문에 동시에 두가지 루프(아래 루프와 main함수의 mainloop() 메서드)를 동작시킬 수 있다.
    # 부모 클래스인 Webcam_keyboard의 run_keyboard메서드로 키보드 관련 작업을 구성하고, 
    # 변경된 self.img를 tk_window의 convert_tkimage()메서드를 이용해 tk_window img를 변경해준다
    def run_thread(self):
        while True:
            self.run_keyboard(self.Usingimshow)
            self.tk_window.convert_tkimage(self.img)



def main():

    # tkinter 의 창 크기, 창이 켜지는 좌표
    win_size_x, win_size_y = '1300', '800'
    win_pos_x, win_pos_y = '300', '300'

    # tkinter 인스턴스 생성
    root = tk.Tk()
    # tk_window 인스턴스 생성
    tk_win = tk_window(root, win_size_x, win_size_y, win_pos_x, win_pos_y)

    # Cam_Thread에서 이미지 resize를 위해 필요한 size값
    size_x, size_y, channel = 1280, 720, 3
    window_size = (size_y, size_x, channel)
    # OpenCV에서 제공하는 imshow메소드를 사용할 것인지
    Usingimshow = True
    # Cam_Thread 인스턴스 생성
    cam_thread = Cam_Thread(tk_win, window_size=window_size, Usingimshow=Usingimshow)

    # KNN instance has been created
    # KNN을 사용하여 제스처인식을 하려는 경우에 사용
    cam_thread.detector.KNN()

    # thread_img라는 하위 스레드 인스턴스를 생성, 해당 스레드에서는 cam_thread.run_thread를 실행
    thread_img = threading.Thread(target=cam_thread.run_thread, args=())

    # thread_img를 데몬 스레드로 구성, <- tk_window 스레드에 종속되기 때문에 tkinter 창이 종료되면 해당 프로세스도 종료됨
    thread_img.daemon = True

    # therad_img 데몬스레드 실행
    thread_img.start()

    # tkinter 메인루프 실행
    root.mainloop()

if __name__ == "__main__":
    main()