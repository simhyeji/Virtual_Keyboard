# 영상을 돌리려면 Threading 모듈을 사용해야한다.

import cv2
from PIL import Image, ImageTk
import tkinter as tk
import numpy as np
import threading


class tk_window():
    def __init__(self, window:tk.Tk):
        self.window = window
        self.window.title("test1")
        self.window.geometry("900x750+300+300")
        self.window.resizable(False, False)

        self.imgtk = None

        button1 = tk.Button(self.window, text="close", overrelief="solid", width=15, command=self.window_close, repeatdelay=1000, repeatinterval=100)
        button1.pack()

        self.label = tk.Label(self.window, image=self.imgtk)
        self.label.pack()

    def window_close(self):
        print("close")
        self.window.quit()

    # def toggle_image(self):

    def convert_tkimage(self, cv_image):
        RGB = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(RGB)
        self.imgtk = ImageTk.PhotoImage(image=img)

        self.label.config(image=self.imgtk)
        self.label.image = self.imgtk

class Cam_Thread():
    def __init__(self, tk_win:tk_window):
        self.img = []
        self.tkimg = []
        self.cap = cv2.VideoCapture(0)
        self.tk_window = tk_win

    def run_thread(self):
        while True:
            if self.cap.isOpened() == False:
                print("Unable to read camera feed")
            else :
                print("Capturing Starts!")
                break

        while True:
            _, self.img = self.cap.read()
            self.tkimg = self.img
            if self.img != []:
                cv2.imshow('test cv window', self.img)
                self.tk_window.convert_tkimage(self.tkimg)

            cv2.waitKey(1)


def main():
    window = tk.Tk()
    tk_win = tk_window(window)
    cam_thread = Cam_Thread(tk_win)
    
    thread_img = threading.Thread(target=cam_thread.run_thread, args=())
    thread_img.daemon = True
    thread_img.start()

    window.mainloop()

if __name__ == "__main__":
    main()
