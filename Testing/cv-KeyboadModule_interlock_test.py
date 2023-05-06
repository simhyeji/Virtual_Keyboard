import cv2
import KeyboardModule as kb


vfile = cv2.VideoCapture(0)             # 0번 웹캠 객체 생성(캠이 켜지는데 시간이 걸림)
keyboard = kb.Keyboard()                # 키보드 클래스 생성

if vfile.isOpened():                    #비디오객체가 열렸는지 트리거
    while True:
        vret, img = vfile.read()        # 프레임별로 이미지를 불러옴
        if vret:                        # 프레임이 가져와진다면
            img = cv2.flip(img,1)       # 이미지 뒤집기
            img = cv2.resize(img, (1920, 1080))

            # cv2.imshow("webcam_nonmirror", img)    # 해당 프레임 출력
            # cv2.imshow("webcam_horizontal", cv2.flip(img, 1))
            # cv2.imshow("webcam_both", cv2.flip(img, -1))

            keyboard.get_image(img)
            keyboard.drawing_keyboard()
            cv2.imshow("webcam_vertical", keyboard.img)

            if cv2.waitKey(1) != -1:        # 1000/N ms마다 wait, 1은 거의 실시간, 웹캠에서 사용
                # print(type(img))
                # print(img)
                print(f"H : {keyboard.get_keyposition('H')}")
                break
        else:
            print("프레임이 정상적이지 않음")
            break
else:
    print("파일을 열 수 없습니다.")

vfile.release()                     #영상객체 릴리즈
cv2.destroyAllWindows()