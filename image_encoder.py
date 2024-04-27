#!/usr/bin/python
import PIL.Image as Image
import os

# Calculate gamma correction table, makes mid-range colors look 'right':
gamma = bytearray(256)
for i in range(256):
	gamma[i] = int(pow(float(i) / 255.0, 2.7) * 255.0 + 0.5)

'''
	NEW METHOD
'''
# img_dir_name = "img"
img_dir_path = "./images/"
# img_data_dir_path = "../"
img_data_filename = "img_data.h"
IMG_HEIGHT = 70	# image height is constant

# Get number of image files in directory
# num_images = len([name for name in os.listdir(img_dir_path) if os.path.isfile(os.path.join(img_dir_path, name))])

img_list = [] # [(width, filename), ...]

# For each image in directory, append image width and filename to img_list
for filename in os.listdir(img_dir_path):
	try:
		# Open image if current file is not a directory
		if os.path.isfile(f"{ img_dir_path }/{ filename }"):
			img = Image.open(img_dir_path + filename).convert("RGB")
		else:
			continue
	except Exception as ex:
		print(ex)
		continue		

	w, h = img.size
	# print(f"{ filename }, w:{ w }, h:{ h }")

	img_list.append((w, filename))

# Sort image list by width
img_list.sort(key=lambda val: val[0])
print(img_list)

# Open output file for writing
out_file = open(f"./{ img_data_filename }", 'w')

# Write code for NUM_IMAGES variable
out_file.write(f"const uint8_t NUM_IMAGES = { len(img_list) };\n")

# Set padding for format function so hex values are printed with leading zeros when necessary
padded_hex_format = "{0:0{1}X}"
pad = 2

img_i = -1	# index of current image in image list
curr_img_width = 0
img_num_pixels = 0
img_group_count_list = []	# number of images in each image group size
img_group_img_index_list = []	# starting indexes for images in each img group
img_group_count = 0
img_group_img_index = 0
img_width_list = []	# list of image group widths

for w, img_filename in img_list:
	img_i += 1
	img = Image.open(img_dir_path + img_filename).convert("RGB")
	pixels = img.load() # load the image data
	
	# If image width is different from previous image
	if w != curr_img_width:
		
		img_width_list.append(w)

		# Update curr_img_width with the width of the currrent image group
		curr_img_width = w
		img_num_pixels = w * IMG_HEIGHT
		
		# If not the first image
		if img_i > 0:
			# Write code to close the previous image size array
			out_file.write("\n};\n")

			# Append the starting image index for the current image group
			img_group_img_index_list.append(img_group_img_index)

			# Append the previous group's number of images to the image group count list, and reset counter			
			img_group_count_list.append(img_group_count)
			img_group_count = 1
		else:
			img_group_count += 1

		# Write the image data array declaration
		out_file.write(f"const PROGMEM uint32_t img_{ IMG_HEIGHT }x{ w }_data[][{ img_num_pixels }]" + "{\n")
	else:		
		# if not first image in list
		if img_i > 0:
			img_group_count += 1
		
		# Print before next image pixel array
		out_file.write(',')
		out_file.write("\n")

	img_group_img_index += 1

	# Begin writing code for array for current image pixels
	out_file.write('{')

	for x in range(curr_img_width):			# For each column of image...
		for y in range(IMG_HEIGHT):		# For each pixel in column...
			val = pixels[x, y]    	# Read pixel in image
			
			# Convert rgb values to hex
			# Reordering RGB to GRB to be compatible with WS2812B LEDs
			g_hex = padded_hex_format.format(gamma[val[0]], pad)
			r_hex = padded_hex_format.format(gamma[val[1]], pad)
			b_hex = padded_hex_format.format(gamma[val[2]], pad)

			# Write hex values to file as a 32-bit hex color code
			out_file.write('0x' + g_hex + r_hex + b_hex)

			# Print a comma if this is not the last pixel in the image
			if x < (curr_img_width - 1) or y < (IMG_HEIGHT - 1):
				out_file.write(',')

	# End writing code for current image
	out_file.write('}')

out_file.write("\n};")

out_file.write("\nconst uint16_t IMG_HEIGHT = " + str(IMG_HEIGHT) + ";")

# Append the last group's number of images to the image group count list
img_group_count_list.append(img_group_count)

# Append the last image group's starting image index
img_group_img_index_list.append(img_group_img_index)

# Write code to file for array containing the starting image index in each image group
out_file.write("\nconst uint8_t IMG_GROUP_STARTING_INDEXES[]{")
for i in range(len(img_group_img_index_list)):
	out_file.write(str(img_group_img_index_list[i]))

	if i < len(img_group_img_index_list) - 1:
		out_file.write(",")

out_file.write("};")

# Write code to file for array containing the number of images in each image group
out_file.write("\nconst uint8_t NUM_IMAGES_PER_GROUP[]{")
for i in range(len(img_group_count_list)):
	out_file.write(str(img_group_count_list[i]))
	
	if i < len(img_group_count_list) - 1:
		out_file.write(",")

out_file.write("};")

# Write code to file for array containing the width of the images in each image group
out_file.write("\nconst uint8_t IMAGE_GROUP_WIDTHS[]{")
for i in range(len(img_width_list)):
	out_file.write(str(img_width_list[i]))
	
	if i < len(img_width_list) - 1:
		out_file.write(",")

out_file.write("};")

out_file.close()
