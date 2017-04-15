#!/usr/bin/env python

from __future__ import division

import sys
from PIL import Image

def main():
	im = Image.open(sys.argv[1])
	aspect = im.size[0] / im.size[1]
	im = im.resize((384, int(round(384 / aspect))), Image.BICUBIC)
	im = im.convert("1", dither=Image.FLOYDSTEINBERG)

	pix = im.load()
	with open(sys.argv[2], 'wb') as of:
		raster_image(of, im.width, im.height, pix)
		of.write('\n\n\n\n\x1d\x56\x01') #feed and cut

def raster_image(of, width, height, pixels):
	of.write('\x1d\x76' + chr(48) + chr(0)) #raster, normal size

	of.write(chr((width//8) & 0xff) + chr((width//8) >> 8))
	of.write(chr(height & 0xff) + chr(height >> 8))

	for y in range(height):
		for x in range(width//8):
			byteval = 0
			for i in range(8):
				bitval = pixels[x*8 + i, y]
				byteval |= (0 if bitval else 1) << (7-i)
			of.write(chr(byteval))

if __name__ == '__main__':
	main()
