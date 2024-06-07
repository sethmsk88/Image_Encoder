import os, sys
import PIL.Image as Image

img_source_dir = ".\\images\\" # At Home
img_out_dir = ".\\image_out\\"
filename  = "Fire 1.jpg" # Image file to load

new_img_height = 36

img_list = [] # [(width, filename), ...]

# For each image in directory, append image width and filename to img_list
for filename in os.listdir(img_source_dir):
	try:
		# Open image if current file is not a directory
		if os.path.isfile(f"{ img_source_dir }/{ filename }"):
			img = Image.open(img_source_dir + filename).convert("RGB")
		else:
			continue
	except Exception as ex:
		print(ex)
		continue		

	w, h = img.size
	new_img_width = int(float(w) * float(new_img_height) / float(h))
	new_img_size = new_img_width, h
	print(f"{ filename }, w:{ w }, h:{ h }")

	img_name, img_format = filename.split('.')
	img_list.append((new_img_width, filename))

	# Scale the image
	new_img = img.resize(new_img_size, Image.BICUBIC)

	new_img_filename = img_name + '_' + str(new_img_height) + '.' + img_format
	#new_img.save(img_out_dir + new_img_filename, img_format)
	new_img.save(img_out_dir + new_img_filename)

# Sort image list by width
img_list.sort(key=lambda val: val[0])
print(img_list)

'''
try:
	img = Image.open(img_source_dir + filename).convert("RGB")
	img_name = filename.split('.')[0]
	img_format = filename.split('.')[1]

	orig_img_width = img.size[0]
	orig_img_height = img.size[1]
	new_img_width = int(float(new_img_height) * (float(orig_img_width) / float(orig_img_height)))
	new_img_size = new_img_width, new_img_height

	# new_img = img.resize(new_img_size, Image.LANCZOS)
	new_img = img.resize(new_img_size, Image.BICUBIC)
	new_img_filename = img_name + '_' + str(new_img_height) + '.' + img_format
	#new_img.save(img_out_dir + new_img_filename, img_format)
	new_img.save(img_out_dir + new_img_filename)
except IOError as e:
	print("I/O Error({0}): {1}".format(e.errno, e.strerror))
'''