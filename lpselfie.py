#!/usr/bin/env python

from __future__ import division
from __future__ import print_function

import cv2
import numpy as np
import PIL.Image
import RPi.GPIO
import sys
import threading

class Grabber():
	def __init__(self, num):
		self._cap = cv2.VideoCapture(num)
		self._lock = threading.Lock()
		self._frame = None

	def run(self):
		while True:
			s, img = self._cap.read()
			if s:
				self._lock.acquire()
				self._frame = img
				self._lock.release()

	def getFrame(self):
		while True:
			with self._lock:
				ret = self._frame
			if ret is not None:
				return ret

def processImage(img, printWidth):
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # convert to grayscale
	img = cv2.equalizeHist(img) # equalize histogram for better contrast

	(w, h) = img.shape[1::-1]
	if w > h:
		img = cv2.transpose(img)
		(w, h) = (h, w)

	aspect = w / h # always <=1
	newSize = (int(printWidth), int(printWidth / aspect))
	img = cv2.resize(img, newSize) # resize for printing

	imgPil = PIL.Image.fromarray(img, mode='L') # convert for dithering
	imgPil = imgPil.convert("1", dither=PIL.Image.FLOYDSTEINBERG) # dither

	return imgPil

def printImage(img, dev):
	with open(dev, 'wb') as of:
		raster_image(of, img.size[0], img.size[1], img.load())
		of.write('\n\n\n\n\x1d\x56\x01') # feed and cut

def raster_image(of, width, height, pixels):
	of.write('\x1d\x76' + chr(48) + chr(0)) # raster, normal size

	of.write(chr((width//8) & 0xff) + chr((width//8) >> 8))
	of.write(chr(height & 0xff) + chr(height >> 8))

	for y in range(height):
		for x in range(width//8):
			byteval = 0
			for i in range(8):
				bitval = pixels[x*8 + i, y]
				byteval |= (0 if bitval else 1) << (7-i)
#				print('X' if bitval else ' ', end="")
			of.write(chr(byteval))
#		print("")

def main():
	grabber = Grabber(0)
	grabberThread = threading.Thread(target=grabber.run)
	grabberThread.daemon = True
	grabberThread.start()

	RPi.GPIO.setmode(RPi.GPIO.BOARD)
	RPi.GPIO.setup(5, RPi.GPIO.IN)
	prev = RPi.GPIO.input(5)
	while True:
		cur = RPi.GPIO.input(5)
		if cur == 1 and prev == 0:
			img = processImage(grabber.getFrame(), 384)
			printImage(img, "/dev/usb/lp0")
		prev = cur

if __name__ == '__main__':
	main()
