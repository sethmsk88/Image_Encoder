import os, sys
import PIL.Image as Image

# proj_dir = "C:\\Users\\kerrs\\Dropbox\\Arduino\\pov_light_stick_17\\img\\" # At work
proj_dir = "E:\\Dropbox\\Arduino\\pov_light_stick_17\\img\\" # At Home
filename  = "lightning_1_smaller.png" # Image file to load

new_img_height = 17

try:
	img = Image.open(proj_dir + filename).convert("RGB")
	img_name = filename.split('.')[0]
	img_format = filename.split('.')[1]

	orig_img_width = img.size[0]
	orig_img_height = img.size[1]
	new_img_width = int(float(new_img_height) * (float(orig_img_width) / float(orig_img_height)))
	new_img_size = new_img_width, new_img_height

	# new_img = img.resize(new_img_size, Image.LANCZOS)
	new_img = img.resize(new_img_size, Image.BICUBIC)
	new_img_filename = img_name + '_edit.' + img_format;
	new_img.save(proj_dir + new_img_filename, img_format)
except IOError as e:
	print("I/O Error({0}): {1}".format(e.errno, e.strerror))
