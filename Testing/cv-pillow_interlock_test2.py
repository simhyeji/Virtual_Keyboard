from PIL import Image, ImageDraw
import numpy as np
import cv2

img1 = Image.new('RGBA', (100, 100), (255, 0, 0, 0))

draw = ImageDraw.Draw(img1)
draw.ellipse((25, 25, 75, 75), fill=(255, 0, 0))

print(img1)
print(type(img1))
print('-'*10)
# print(np.array(img1))
print(np.array(img1).shape)

cv2.imshow("1234", np.array(img1))  # 클래스 내부 이미지 변수를 이용하여 이미지 출력
cv2.waitKey()               # 키 입력들어올때까지 대기
cv2.destroyAllWindows()

'''
img_pil = Image.fromarray(self.img)
point = int(self.x + (text_position_scaler[1] * self.s)), int(self.y + (text_position_scaler[0] * self.s)) 
ImageDraw.Draw(img_pil).text((point[0],point[1]), str(key), font = self.font, fill = text_color)
self.img = np.array(img_pil)
'''