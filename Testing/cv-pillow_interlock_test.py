import numpy as np
from PIL import ImageFont, ImageDraw, Image
import cv2
img = np.zeros((200,400,3),np.uint8)


b,g,r,a = 255,255,255,255
fontpath = "fonts/gulim.ttc"
font = ImageFont.truetype(fontpath, 20)
img_pil = Image.fromarray(img)
draw = ImageDraw.Draw(img_pil)
draw.text((60, 70),  "김형준ABC123#GISDeveloper", font=font, fill=(b,g,r,a))

'''
img_pil = Image.fromarray(self.img)
point = int(self.x + (text_position_scaler[1] * self.s)), int(self.y + (text_position_scaler[0] * self.s)) 
ImageDraw.Draw(img_pil).text((point[0],point[1]), str(key), font = self.font, fill = text_color)
self.img = np.array(img_pil)
'''


img = np.array(img_pil)
cv2.putText(img,  "by Dip2K", (250,120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (b,g,r), 1, cv2.LINE_AA)


cv2.imshow("res", img)
cv2.waitKey()
cv2.destroyAllWindows()

# TODO
# 1. 투명한 바탕에 텍스트를 그리고 그것을 이미지 합성하기 -> 글자 하나 그릴때마다 전체화면 연산 안해도 되니까 나을듯?