# Image Encoder Script Documentation

## Overview

The `encode_image.py` script is a Python utility that converts PNG images into a custom binary data format (`.dat` files) suitable for LED display systems or embedded applications. It processes images from a source directory and outputs encoded data files organized into numbered groups.

## What It Does

### Core Functionality

1. **Image Processing**: Loads PNG images and converts them to RGB format
2. **Gamma Correction**: Applies gamma correction (γ = 2.7) to make colors appear more natural on LED displays
3. **Data Encoding**: Converts RGB pixel data to hexadecimal format
4. **File Organization**: Groups output files into directories containing up to 10 images each
5. **Mapping Generation**: Creates a mapping file to track the relationship between source images and output data files

### Technical Details

- **Gamma Correction**: Uses a gamma value of 2.7 to adjust color brightness for LED displays
- **Color Format**: Converts each pixel to 24-bit RGB hex format (RRGGBB)
- **File Structure**: Creates numbered directories (0, 1, 2, etc.) containing up to 10 `.dat` files each
- **Naming Convention**: Output files are named with zero-padded numbers (0000.dat, 0001.dat, etc.)

## Directory Structure

The script expects and creates the following directory structure:

```
image_encoder/
├── encode_image.py
├── img/
│   └── sd_card_images/        # Source PNG images
└── img_data/                  # Output directory
    ├── 0/                     # First group (images 0-9)
    │   ├── 0000.dat
    │   ├── 0001.dat
    │   └── ...
    ├── 1/                     # Second group (images 10-19)
    │   ├── 0010.dat
    │   ├── 0011.dat
    │   └── ...
    └── map.txt               # Mapping file
```

## How to Use

### Prerequisites

- Python 3.x installed
- PIL (Pillow) library: `pip install Pillow`
- PNG images in the source directory

### Setup

1. **Prepare Source Images**:
   - Place your PNG images in `../img/sd_card_images/` relative to the script location
   - Ensure all images have consistent dimensions
   - Only PNG files will be processed

2. **Clean Output Directory**:
   - Delete any existing files/folders in `../img_data/` before running
   - The script will create new numbered directories automatically

### Running the Script

```bash
python encode_image.py
```

### Interactive Process

1. The script will process images in alphanumeric order
2. Progress will be displayed showing the mapping between source files and output files
3. If existing data is found, you'll be prompted to clean the output directory
4. Upon completion, press Enter to close the program

### Example Output

```
Encoding images...

0/0000.dat ==> fire_01.png
0/0001.dat ==> fire_02.png
0/0002.dat ==> lightning_01.png
...
1/0010.dat ==> pattern_01.png
1/0011.dat ==> pattern_02.png

20 images encoded
Press Enter to close program...
```

## Output Files

### Data Files (.dat)

Each `.dat` file contains:
- **First line**: Image width (in pixels)
- **Subsequent data**: Gamma-corrected RGB hex values for each pixel
- **Format**: Column-major order (all pixels in column 1, then column 2, etc.)
- **Color encoding**: 6-character hex strings (RRGGBB) without separators

### Mapping File (map.txt)

Located at `../map.txt`, this file contains:
- Line-by-line mapping of output files to source images
- Format: `directory/filename.dat ==> source_image.png`
- Useful for tracking which encoded file corresponds to which original image

## Important Notes

### Limitations

- **File Format**: Only processes PNG images (other formats are skipped)
- **Directory Structure**: Requires specific relative path structure
- **Clean Start**: Requires manual cleanup of output directory between runs
- **Memory Usage**: Loads entire images into memory (may be intensive for very large images)

### Best Practices

1. **Consistent Dimensions**: Ensure all source images have the same width and height
2. **File Naming**: Use descriptive filenames as they appear in the mapping file
3. **Backup**: Keep backups of original images before processing
4. **Testing**: Test with a small batch of images first

### Error Handling

- **Existing Data**: Script will halt if output directories already exist
- **File Access**: Ensure proper read/write permissions for source and output directories
- **Missing Directories**: Parent directories must exist before running

## Use Cases

This script is particularly useful for:

- **LED Matrix Displays**: Converting images for programmable LED arrays
- **Embedded Systems**: Creating image data for microcontroller projects
- **Custom Display Hardware**: Preparing images for specialized display systems
- **Batch Processing**: Converting multiple images to a custom format efficiently

## Customization Options

You can modify the script to:

- Change the gamma correction value (currently 2.7)
- Adjust the group size (currently 10 images per directory)
- Modify the output format or file structure
- Add support for additional image formats
- Implement different color encoding schemes
