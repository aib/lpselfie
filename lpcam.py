#!/usr/bin/env python

import cv2
import PIL.Image

cam = cv2.VideoCapture(0)
s, img = cam.read()

cv2.imwrite("/tmp/img.jpg", img)

im = PIL.Image.open("/tmp/img.jpg")
aspect = im.size[0] / im.size[1]
im = im.resize((384, int(round(384 / aspect))), PIL.Image.BICUBIC)
im = im.convert("1", dither=PIL.Image.FLOYDSTEINBERG)
im.save("/tmp/img.png")

