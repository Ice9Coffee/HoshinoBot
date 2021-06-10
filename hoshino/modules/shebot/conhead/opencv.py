import os
from random import randint

import cv2
from PIL import Image


# opencv无法使用中文路径
# PicPath = config.PIC_PATH + 'JieTou/'

def add(filename, outfile, cascade_file=os.path.dirname(os.path.abspath(__file__)) + "/data/lbpcascade_animeface.xml"):
    print(cascade_file)
    cascade = cv2.CascadeClassifier(cascade_file)
    cvimg = cv2.imread(filename, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(cvimg, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    faces = cascade.detectMultiScale(gray,
                                     scaleFactor=1.1,
                                     minNeighbors=5,
                                     minSize=(24, 24))
    if not len(faces):
        return 0
    img = Image.open(filename)
    img = img.convert("RGBA")
    top_shift_scale = 0.45
    x_scale = 0.25
    for (x, y, w, h) in faces:
        y_shift = int(h * top_shift_scale)
        x_shift = int(w * x_scale)
        face_w = max(w + 2 * x_shift, h + y_shift)
        faceimg = Image.open(os.path.dirname(os.path.abspath(__file__)) + "/data/猫猫头_" + str(randint(0, 6)) + ".png")
        faceimg = faceimg.resize((face_w, face_w))
        r, g, b, a = faceimg.split()
        img.paste(faceimg, (x - x_shift, y - y_shift), mask=a)
    img.save(outfile)
    return 1
