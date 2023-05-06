import numpy as np
import cv2
# PIL은 OpenCV상에서 한글을 이미지에 그릴 수 없기 때문에 활용한다.
# PIL이미지는 tkinter에서도 활용되므로 프로세스를 개선하면 동작속도의 개선을 예상할 수 있다.
from PIL import ImageFont, ImageDraw, Image 
       

# 키보드를 그리기 위한 클래스
class Keyboard():
    # window_size는 3 element tuple로 구성
    # window_size = (y(height), x(width), 3(channel))
    def __init__(self, window_size=(720, 1280, 3)):
        # 모두 0으로 되어 있는 빈 canvas(검정색) - 크기는 기본을 (720,1280,3)으로 설정해둠
        # 바탕 이미지 변수
        self.img = np.zeros(window_size, np.uint8)
        self.window_size = window_size   

        # 키보드 최상단-좌측 좌표(시작 좌표): 
        # x, y -> 화면 좌표
        # s    -> 기본사이즈 키의 한 변 크기
        self.s = int(self.img.shape[0] * 0.0764)
        self.x = int(self.img.shape[1] * 0.172)
        self.y = self.img.shape[0] - int(self.img.shape[0] * 0.118) - (self.s * 5)
        
        # 키보드 배열
        # '\n'을 기준으로 다음 행으로 넘어간다.
        self.key_list_index = 0
        self.key_list_big = ['`','1','2','3','4','5','6','7','8','9','0','-','=','backspace','\n',
                    'tab', 'Q','W','E','R','T','Y','U','I','O','P','[',']','\\','\n',
                    'caps_lock','A','S','D','F','G','H','J','K','L',';','\'','enter', '\n',
                    'shift_l','Z','X','C','V','B','N','M',',','.','/','shift_r', '\n',
                    'FN','ctrl','OPT_l','alt','space','Lng','OPT_r','left', 'up','down','right']
        self.key_list_small = ['`','1','2','3','4','5','6','7','8','9','0','-','=','backspace','\n',
                    'tab', 'q','w','e','r','t','y','u','i','o','p','[',']','\\','\n',
                    'caps_lock','a','s','d','f','g','h','j','k','l',';','\'','enter', '\n',
                    'shift_l','z','x','c','v','b','n','m',',','.','/','shift_r', '\n',
                    'FN','ctrl','OPT_l','alt','space','Lng','OPT_r','left', 'up','down','right']
        self.key_list_kor = ['`','1','2','3','4','5','6','7','8','9','0','-','=','backspace','\n',
                    'tab', 'ㅂ','ㅈ','ㄷ','ㄱ','ㅅ','ㅛ','ㅕ','ㅑ','ㅐ','ㅔ','[',']','\\','\n',
                    'caps_lock','ㅁ','ㄴ','ㅇ','ㄹ','ㅎ','ㅗ','ㅓ','ㅏ','ㅣ',';','\'','enter', '\n',
                    'shift_l','ㅋ','ㅌ','ㅊ','ㅍ','ㅠ','ㅜ','ㅡ',',','.','/','shift_r', '\n',
                    'FN','ctrl','OPT_l','alt','space','Lng','OPT_r','left', 'up','down','right']
        self.key_list_shift = ['`','1','2','3','4','5','6','7','8','9','0','-','=','backspace','\n',
                    'tab', 'ㅃ','ㅉ','ㄸ','ㄲ','ㅆ','ㅛ','ㅕ','ㅑ','ㅒ','ㅖ','[',']','\\','\n',
                    'caps_lock','ㅁ','ㄴ','ㅇ','ㄹ','ㅎ','ㅗ','ㅓ','ㅏ','ㅣ',';','\'','enter', '\n',
                    'shift_l','ㅋ','ㅌ','ㅊ','ㅍ','ㅠ','ㅜ','ㅡ',',','.','/','shift_r', '\n',
                    'FN','ctrl','OPT_l','alt','space','Lng','OPT_r','left', 'up','down','right']
        self.key_list_opt = ['OPT_l','~','!','@','#','$','%','^','&','*','?','\n','(',')','_','+','{','}','|',':','"','<','>']
        self.key_list = [self.key_list_small, self.key_list_big, self.key_list_kor, self.key_list_shift, self.key_list_opt]
        self.all_key_position = self.init_get_keyposition()

        # 한글 작성시 필요한 폰트 정보
        self.font = ImageFont.truetype('fonts/gulim.ttc', 20)


    # 이미지 업데이트 함수
    def get_image(self, img): 
        self.img = img

    # 좌표 초기화 함수
    # s(변의 길이, 편향), x, y값이 변경되는 상황이 발생할 수 있기 때문에 고정된 정수형으로 반환하는 함수.
    def init_coordinate(self, elements:list):
        for element in elements:
            if element == 's':
                self.s = int(self.img.shape[0] * 0.0764)
            elif element == 'x':
                self.x = int(self.img.shape[1] * 0.172)
            elif element == 'y':
                self.y = self.img.shape[0] - int(self.img.shape[0] * 0.118) - (self.s * 5)
            else :
                raise Exception("argument(list)'s element is not available")
    
    # 클래스 인스턴스를 생성하자마자 바로 실행하여 현재 화면에서의 전체 키보드 레이아웃의 보더라인 꼭짓점 좌표를
    # 인덱스에 대한 딕셔너리 형식으로 리턴한다.
    # 각 자판의 보더라인 꼭짓점의 리스트 순서는 [좌상, 좌하, 우하, 우상] 순서로 진행된다.
    # 키값들 scale값 조정하는 함수
    def init_get_keyposition(self)->dict:   
        temp = {}
        if self.key_list_index < 4:   #opt 키리스트 제외 나머지 키 리스트 위치
            for idx, key in enumerate(self.key_list[self.key_list_index]):  #idx - key위치
                scaler = 1.0
                if idx in (14, 29, 43, 56):           # key == '\n' case
                    self.y += self.s + 2 
                    self.init_coordinate(['x'])  #\n 일때 y값은 +2, x 값은 init_coordinate 함수로 초기화
                else :
                    if idx in (13, 15, 30, 42, 44, 55, 61): # special keys
                        if idx == 13 or idx == 15:     # backspace, tab -> 1.5
                            scaler = 1.5
                        elif idx == 30:                 # caps_loc       -> 1.75
                            scaler = 1.75
                        elif idx == 42:                 # enter          -> 1.8
                            scaler = 1.8
                        elif idx == 44 or idx == 55:   # shift          -> 2.31
                            scaler = 2.31
                        elif idx == 61:                 # space          -> 4.7
                            scaler = 4.7

                    temp[idx] = [key, [[self.x, self.y],                                  # up-left
                            [self.x, self.y + self.s],                           # down-left
                            [self.x + int(scaler * self.s), self.y + self.s],    # down-right
                            [self.x + int(scaler * self.s), self.y]]]             # up-right
                    self.x += int(scaler * self.s) + 2
            self.init_coordinate(['x', 's', 'y'])
        
        #OPT키 그리기
        else : 
            for idx, key in enumerate(self.key_list[4]):
                scaler = 1.0
                if idx == 11:           # key == '\n' case
                    self.y += self.s + 2 
                    self.init_coordinate(['x'])
                else: 
                    temp[idx] = [key, [[self.x, self.y],                                  # up-left
                        [self.x, self.y + self.s],                           # down-left
                        [self.x + int(scaler * self.s), self.y + self.s],    # down-right
                        [self.x + int(scaler * self.s), self.y]]]             # up-right
                    self.x += int(scaler * self.s) + 2
            self.init_coordinate(['x', 's', 'y'])
        return temp
    
    # self.all_key_position에서 key와 대각선 point 성분을 dict형으로 만들어서 리턴
    def get_diag_keyposition(self):
        self.all_key_position = self.init_get_keyposition()
        temp = {}
        for element in self.all_key_position.values():
            temp[element[0]] = [element[1][0], element[1][2]]  #temp[키이름] = [위 왼쪽 좌표, 아래 오른쪽 좌표]

        return temp

    # 시도 1. 알파값을 이용한 그림 합성으로 한글 텍스트 그리기
    # 시도 2. 그냥 self.img 이미지에다가 글자 하나씩이 아니라 한번에 다 그려버리기 

    
    # 한번에 모든 레이아웃(바운더리)를 그리는 함수 -> 바운더리를 하나 그리고 글자 하나 쓰는 것은 비효율적.
    def draw_all_layout(self, all_key_positions, boundary_color=(255,0,0)):
        for key_position in all_key_positions:
            self.img = cv2.polylines(self.img, np.array([key_position[1]]), True, boundary_color, 1)

    # 한번에 모든 키(한, 영 무관)를 그리는 함수
    # key값이 특수키인 경우에 대해 글자 위치를 조절
    def draw_all_keys(self, all_key_positions, text_color=(255,0,0)):
        if self.key_list_index in (0, 1, 4):
            for key, key_position in all_key_positions:
                if key == 'space' :
                    self.text_position_scaler = (0.5, 1.9) # space
                elif len(key) == 1:
                    self.text_position_scaler = (0.5, 0.5) # len(key) == 1
                else :
                    self.text_position_scaler = (0.5, 0.1) # base -> (y_scaler, x_scaler)

                text_position = [int(key_position[0][0] + (self.text_position_scaler[1] * self.s)), 
                                int(key_position[0][1] + (self.text_position_scaler[0] * self.s))]

                cv2.putText(self.img, str(key), text_position, cv2.FONT_HERSHEY_PLAIN, 1, text_color, 1, cv2.LINE_AA)

        elif self.key_list_index in (2, 3):
            temp_img = Image.fromarray(self.img)
            draw = ImageDraw.Draw(temp_img)
            for key, key_position in all_key_positions:
                if key == 'space' :
                    self.text_position_scaler = (0.5, 1.9) # space
                elif len(key) == 1:
                    self.text_position_scaler = (0.5, 0.5) # len(key) == 1
                else :
                    self.text_position_scaler = (0.5, 0.1) # base -> (y_scaler, x_scaler)

                text_position = int(key_position[0][0] + (self.text_position_scaler[1] * self.s)), int(key_position[0][1] + (self.text_position_scaler[0] * self.s))

                draw.text((text_position[0], text_position[1]), key, font=self.font, fill=text_color)
            self.img = np.array(temp_img)



    # 키보드를 그리는 함수(레이아웃 다 그리고 텍스트 그리는 방식)
    def drawing_keyboard(self):
        self.draw_all_layout(self.all_key_position.values())
        self.draw_all_keys(self.all_key_position.values())
        return self.img

    # 키보드의 한/영 이나 shift, caps_lock, opt키 등 키배열이나 키 텍스트의 변형을 주는 함수
    def change_key(self, key_name):
        if key_name == 'Lng':
            if self.key_list_index == 0:
                self.key_list_index = 2
            elif self.key_list_index == 2:
                self.key_list_index = 0
        elif key_name == 'caps_lock':
            if self.key_list_index == 0:
                self.key_list_index = 1
            elif self.key_list_index == 1:
                self.key_list_index = 0 
        elif key_name in ('shift_l', 'shift_r'):
            if self.key_list_index == 2:
                self.key_list_index = 3
            elif self.key_list_index == 3:
                self.key_list_index = 2
        elif key_name in ('OPT_l', 'OPT_r'):
            if self.key_list_index != 4:
                self.key_list_index = 4
            else:
                self.key_list_index = 0
        
        

def __main():
    kb = Keyboard()             # 키보드 클래스 가져오기
    kb.drawing_keyboard()       # 키보드 클래스의 drawing_keyboard 함수 사용
    # print(kb.all_key_position)
    

    cv2.imshow("1234", kb.img)  # 클래스 내부 이미지 변수를 이용하여 이미지 출력
    cv2.waitKey()               # 키 입력들어올때까지 대기
    cv2.destroyAllWindows()

if __name__ == "__main__":
    __main()

