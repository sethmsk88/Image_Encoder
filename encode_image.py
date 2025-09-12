#!/usr/bin/python
import PIL.Image as Image
import os
import sys
import re
import argparse
from datetime import datetime


def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(data, key=alphanum_key)


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Encode images to .dat format for LED displays (supports JPG, JPEG, PNG, BMP, GIF, TIFF, WEBP)')
    parser.add_argument('input_dir', nargs='?', default='images/', 
                        help='Input directory containing image files (default: images/)')
    parser.add_argument('--output-dir', default='img_data/', 
                        help='Output directory for encoded data files (default: img_data/)')
    args = parser.parse_args()

    # Calculate gamma correction table, makes mid-range colors look 'right':
    gamma = bytearray(256)
    for i in range(256):
        gamma[i] = int(pow(float(i) / 255.0, 2.7) * 255.0 + 0.5)

    # Setup directory paths
    img_dir_path = args.input_dir.rstrip('/\\') + '/'
    base_output_dir = args.output_dir.rstrip('/\\')
    
    # Create a unique timestamped output directory to avoid collisions
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_output_name = f"{os.path.basename(os.path.normpath(img_dir_path))}_{timestamp}"
    img_data_dir_path = os.path.join(base_output_dir, unique_output_name) + '/'
    
    # Ensure input directory exists
    if not os.path.exists(img_dir_path):
        print(f"ERROR: Input directory '{img_dir_path}' does not exist!")
        sys.exit(1)
    
    # Get the directory name for the data filename
    img_dir_name = os.path.basename(os.path.normpath(img_dir_path))
    if not img_dir_name:
        img_dir_name = "images"

    # WARNING: The image height and width MUST match
    # the height and width of the files in the image directory

    # Open file to export data
    img_data_filename = img_dir_name + ".dat"

    # Ensure output directory exists
    os.makedirs(img_data_dir_path, exist_ok=True)

    # Create image map file to show mapping between source images and dat files
    map_file_path = os.path.join(img_data_dir_path, "map.txt")
    map_file = open(map_file_path, 'w')
    map_file.truncate(0)  # clear file contents if there are any
    mapping = ""

    # Define supported image extensions
    supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    
    print("Encoding images...")
    print(f"Input directory: {img_dir_path}")
    print(f"Output directory: {img_data_dir_path}")
    print(f"Supported formats: {', '.join(sorted(supported_extensions))}")
    print()

    group_dir_num = -1
    img_group_size = 10  # this number of images will be in each group/directory
    img_i = 0

    filenames = sorted_alphanumeric(os.listdir(img_dir_path))

    # Count supported image files first
    supported_files = []
    for filename in filenames:
        _filename, _file_extension = os.path.splitext(filename.lower())
        if _file_extension in supported_extensions:
            supported_files.append(filename)
    
    if not supported_files:
        print(f"No supported image files found in '{img_dir_path}'")
        print(f"Supported formats: {', '.join(sorted(supported_extensions))}")
        sys.exit(1)
    
    print(f"Found {len(supported_files)} supported image file(s) to process...")
    print()

    for filename in supported_files:

        # create a group directory if img_group_size has been reached
        if img_i % img_group_size == 0:
            group_dir_num += 1
            group_dir_path = os.path.join(img_data_dir_path, str(group_dir_num))
            os.makedirs(group_dir_path, exist_ok=True)

        mapping = str(group_dir_num) + "/" + str(img_i).zfill(4) + ".dat" + " ==> " + filename
        map_file.write(mapping + "\n")
        print(mapping)

        # Create data file for this image
        dat_file_path = os.path.join(img_data_dir_path, str(group_dir_num), str(img_i).zfill(4) + ".dat")
        out_file = open(dat_file_path, 'w')

        # Load image in RGB format and get dimensions:
        img_file_path = os.path.join(img_dir_path, filename)
        img = Image.open(img_file_path).convert("RGB")
        pixels = img.load()  # load the image data
        height = img.height
        width = img.width

        out_file.write(str(width) + "\n")

        # Set padding for format function so hex values are printed with leading zeros when necessary
        padded_hex_format = "{0:0{1}X}"
        padding = 2

        for x in range(width):  # For each column of image...
            for y in range(height):  # For each pixel in column...
                value = pixels[x, y]  # Read pixel in image

                # Convert rgb values to hex
                r_hex = padded_hex_format.format(gamma[value[0]], padding)
                g_hex = padded_hex_format.format(gamma[value[1]], padding)
                b_hex = padded_hex_format.format(gamma[value[2]], padding)

                # Write hex values to file as a 32-bit hex color code
                out_file.write(r_hex + g_hex + b_hex)

        out_file.close()
        img_i += 1

    map_file.close()
    print(f"\n{len(supported_files)} images encoded")
    print(f"Output directory: {img_data_dir_path}")
    print(f"Map file: {map_file_path}")

    try:
        key = input("Press Enter to close program...")
    except:
        pass
