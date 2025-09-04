# Image Encoder for LED Displays

This Python project converts images into C header files containing RGB color data, optimized for WS2812B LED strip displays and Arduino/embedded systems. The project consists of two main Python scripts that work together to prepare and encode images for LED display applications.

## Features

- 🎨 **Batch Image Processing**: Processes multiple images in a directory simultaneously
- 🔧 **Automatic Image Resizing**: Maintains aspect ratio while resizing to target height
- ⚡ **Gamma Correction**: Applies gamma correction (2.7) for better color representation on LEDs
- 🌈 **WS2812B Compatible**: Reorders RGB to GRB format for WS2812B LED compatibility
- 📊 **Optimized Data Structure**: Groups images by width for efficient memory usage
- 💾 **C/Arduino Compatible**: Generates C header files with `PROGMEM` constants for Arduino

## Project Structure

```
image_encoder/
├── image_encoder.py        # Main encoding script
├── create_thumbnail.py     # Image preprocessing/resizing script
├── img_data_35.h          # Generated header file (35px height)
├── img_data_36.h          # Generated header file (36px height)  
├── img_data_70.h          # Generated header file (70px height)
├── images_35/             # Source images (35px height)
├── images_70/             # Source images (70px height)
├── image_out/             # Processed thumbnail images
└── README.md              # This file
```

## Scripts Overview

### 1. `create_thumbnail.py` - Image Preprocessor

This script prepares images for encoding by:
- Reading all images from a source directory (`./images/`)
- Maintaining aspect ratio while resizing to a target height (36px by default)
- Using bicubic interpolation for high-quality resizing
- Saving processed images to an output directory (`./image_out/`)
- Generating a list of images sorted by width

**Key Configuration:**
```python
img_source_dir = ".\\images\\"     # Source directory
img_out_dir = ".\\image_out\\"     # Output directory  
new_img_height = 36                # Target height in pixels
```

### 2. `image_encoder.py` - Main Encoder

This is the core script that converts processed images into C header files:

**Key Features:**
- **Gamma Correction**: Applies gamma curve (γ=2.7) to make colors appear correct on LEDs
- **Color Format Conversion**: Converts RGB to GRB format for WS2812B compatibility
- **Memory Optimization**: Groups images by width to create efficient 2D arrays
- **Metadata Generation**: Creates arrays for image counts, dimensions, and indexing

**Key Configuration:**
```python
img_dir_path = "./images_70/"       # Input directory
img_data_filename = "img_data_70.h" # Output header file
IMG_HEIGHT = 70                     # Fixed image height
```

## Generated C Header File Structure

The output header file contains several important data structures:

```c
// Total number of images
const uint8_t NUM_IMAGES = 53;

// Fixed image height
const uint16_t IMG_HEIGHT = 70;

// 2D array of pixel data grouped by width
const PROGMEM uint32_t img_70x70_data[][4900] = {
    {0x000000, 0x000000, ...},  // First image pixels
    {0x000000, 0x000000, ...},  // Second image pixels
    // ... more images of same width
};

// Starting index for each width group  
const uint8_t IMG_GROUP_STARTING_INDEXES[] = {0, 5, 12, ...};

// Number of images in each width group
const uint8_t NUM_IMAGES_PER_GROUP[] = {5, 7, 8, ...};

// Width of images in each group
const uint8_t IMAGE_GROUP_WIDTHS[] = {45, 52, 70, ...};
```

## Usage Instructions

### Step 1: Prepare Your Images
1. Place your source images in the `./images/` directory
2. Run the preprocessing script:
   ```bash
   python create_thumbnail.py
   ```
3. Check the resized images in `./image_out/` directory

### Step 2: Generate Header Files
1. Move your resized images to the appropriate folder (e.g., `./images_70/`)
2. Configure the target height and paths in `image_encoder.py`:
   ```python
   img_dir_path = "./images_70/"
   img_data_filename = "img_data_70.h"
   IMG_HEIGHT = 70
   ```
3. Run the encoder:
   ```bash
   python image_encoder.py
   ```
4. Use the generated header file in your Arduino/C++ project

### Step 3: Use in Arduino Project
```cpp
#include "img_data_70.h"

void setup() {
    // Initialize your LED strip
    // FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS);
}

void loop() {
    // Display first image
    for(int i = 0; i < IMG_HEIGHT * IMAGE_GROUP_WIDTHS[0]; i++) {
        leds[i] = img_70x70_data[0][i];
    }
    FastLED.show();
}
```

## Technical Details

### Color Format
- **Input**: Standard RGB format from image files
- **Processing**: Gamma correction applied (γ=2.7) 
- **Output**: 24-bit GRB format (0xGGRRBB) for WS2812B LEDs

### Memory Organization  
Images are grouped by width to optimize memory usage:
- Images with the same width are stored in the same 2D array
- Metadata arrays help locate and iterate through image groups
- `PROGMEM` directive stores data in flash memory (Arduino)

### Gamma Correction Formula
```python
gamma[i] = int(pow(float(i) / 255.0, 2.7) * 255.0 + 0.5)
```

## Requirements

### Python Dependencies
```bash
pip install Pillow  # PIL (Python Imaging Library)
```

### Arduino Libraries (for using generated files)
- FastLED (recommended for WS2812B control)
- NeoPixel (alternative LED library)

## Supported Image Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)  
- BMP (.bmp)
- Any format supported by PIL/Pillow

## Example Use Cases

- **LED Matrix Displays**: Show animations or static images
- **Wearable Electronics**: Display patterns on LED clothing/accessories  
- **Art Installations**: Create dynamic visual displays
- **Gaming Projects**: Show sprites or game graphics on LED panels
- **IoT Displays**: Status indicators with custom graphics

## Tips for Best Results

1. **Image Quality**: Use high-contrast images with distinct colors
2. **Size Considerations**: Keep image dimensions reasonable (larger = more memory)
3. **Color Palette**: LEDs work best with vibrant, saturated colors
4. **Testing**: Always test with a few images before batch processing
5. **Memory Management**: Monitor Arduino memory usage with large image sets

## License

This project is open source. Feel free to modify and distribute according to your needs.
