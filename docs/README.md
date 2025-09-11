# Image Encoder for LED Displays

This Python project converts images into C header files containing RGB color data, optimized for WS2812B LED strip displays and Arduino/embedded systems. The project includes comprehensive image processing capabilities with quality enhancement options and automated workflow tools.

## Features

- 🎨 **Advanced Image Processing**: Multiple resize scripts with quality enhancement options
- 🔧 **Smart Image Resizing**: Maintains aspect ratio while resizing to target heights (24px, 36px, 70px)
- ⚡ **Quality Enhancement**: Gamma correction, contrast/saturation boosting, and unsharp masking
- 🌈 **WS2812B Compatible**: Reorders RGB to GRB format for WS2812B LED compatibility
- 📊 **Batch Processing**: Process multiple images with different enhancement presets
- 🖼️ **Composite Generation**: Create visual grids of processed images for comparison
- 💾 **C/Arduino Compatible**: Generates C header files with `PROGMEM` constants for Arduino
- ⚙️ **VS Code Integration**: Comprehensive task system for automated workflows

## Project Structure

```
image_encoder/
├── src/                          # Source code
│   ├── resize_to_24px.py         # Basic resize script with enhancements
│   ├── resize_to_24px_enhanced.py # Advanced resize with JSON settings
│   ├── image_rectangle.py        # Composite image generator
│   ├── image_encoder.py          # Main encoding script
│   └── create_thumbnail.py       # Thumbnail generator (36px)
├── config/                       # Configuration files
│   ├── enhancement_settings.json # Default enhancement settings
│   ├── enhancement_subtle.json   # Subtle enhancement preset
│   ├── enhancement_vibrant.json  # Vibrant enhancement preset
│   ├── enhancement_sharp.json    # Sharp & crisp preset
│   ├── enhancement_warm.json     # Warm & bright preset
│   ├── enhancement_dramatic.json # High contrast preset
│   └── enhancement_soft.json     # Soft & natural preset
├── images/
│   ├── originals/                # Source images (input)
│   ├── processed/                # Processed images organized by size
│   │   ├── 24px/                # Output from resize scripts
│   │   ├── 36px/                # Thumbnail outputs  
│   │   └── 70px/                # Encoded image outputs
│   └── composites/              # Composite images from image_rectangle.py
├── data/                        # Generated data files
├── scripts/                     # Automation scripts
├── .vscode/                     # VS Code configuration
│   └── tasks.json
├── docs/                        # Documentation
│   ├── README.md               # This file
│   └── MIGRATION_SUMMARY.md    # Directory structure migration details
└── build/                      # Build artifacts
```

## Scripts Overview

### 1. `resize_to_24px.py` - Enhanced Basic Resizer

A versatile script that resizes images to 24px height with optional quality enhancements:

**Features:**
- Maintains aspect ratio during resize
- Optional contrast, saturation, and brightness enhancements
- Generates unique filenames to prevent overwriting
- Processes entire directories recursively

**Usage:**
```bash
# From project root
python src/resize_to_24px.py
```

### 2. `resize_to_24px_enhanced.py` - Advanced Quality Enhancement

Advanced resize script with comprehensive quality enhancement options:

**Features:**
- JSON-based configuration system with multiple presets
- Gamma correction for LED color accuracy
- Unsharp masking for edge enhancement
- Preset-based filename generation
- Support for 6 different enhancement styles

**Configuration Presets:**
- **Subtle**: Gentle enhancements for natural look
- **Vibrant**: Enhanced saturation and contrast
- **Sharp**: Crisp edges and definition
- **Warm**: Warm tones and brightness
- **Dramatic**: High contrast for impact
- **Soft**: Natural and balanced

**Usage:**
```bash
# Use default settings
python src/resize_to_24px_enhanced.py --enhanced

# Use specific preset
python src/resize_to_24px_enhanced.py --enhanced --settings config/enhancement_vibrant.json
```

### 3. `image_rectangle.py` - Composite Generator

Creates visual composite grids from processed images for comparison and visualization:

**Features:**
- Processes entire directories of images
- Generates scaled composite images
- Groups images by width for organized layout
- Unique filename generation with timestamps

**Usage:**
```bash
# Generate composite from 24px images
python src/image_rectangle.py images/processed/24px 5
```

### 4. `image_encoder.py` - LED Data Encoder

Converts processed images into C header files for Arduino/embedded systems:

**Key Configuration:**
```python
img_dir_path = "images/processed/70px/"  # Input directory
img_data_filename = "img_data_70.h"      # Output header file
IMG_HEIGHT = 70                          # Fixed image height
```

### 5. `create_thumbnail.py` - 36px Thumbnail Generator

Specialized script for creating 36px thumbnails:

**Key Configuration:**
```python
img_source_dir = "images/originals/"     # Source directory
img_out_dir = "images/processed/36px/"   # Output directory  
new_img_height = 36                      # Target height in pixels
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
1. Place your source images in the `images/originals/` directory
2. Choose your processing workflow based on desired quality:

#### Basic Resize (24px):
```bash
python src/resize_to_24px.py
```

#### Enhanced Resize with Presets:
```bash
# Test all enhancement presets
python src/resize_to_24px_enhanced.py --enhanced --settings config/enhancement_subtle.json
python src/resize_to_24px_enhanced.py --enhanced --settings config/enhancement_vibrant.json
python src/resize_to_24px_enhanced.py --enhanced --settings config/enhancement_dramatic.json
```

#### Generate Thumbnails (36px):
```bash
python src/create_thumbnail.py
```

### Step 2: Create Visual Comparisons
Generate composite images to compare processing results:
```bash
# Create composite from 24px processed images
python src/image_rectangle.py images/processed/24px 5

# Create composite from thumbnails
python src/image_rectangle.py images/processed/36px 5
```

### Step 3: Generate Header Files for Arduino
1. Process images to your target size (typically 70px for encoding)
2. Configure the encoder in `src/image_encoder.py`:
   ```python
   img_dir_path = "images/processed/70px/"
   img_data_filename = "data/img_data_70.h"
   IMG_HEIGHT = 70
   ```
3. Run the encoder:
   ```bash
   python src/image_encoder.py
   ```

### VS Code Integration
If using VS Code, you can access pre-configured tasks:
- **Ctrl+Shift+P** → "Tasks: Run Task" → Choose from available tasks:
  - "Resize Images to 24px"
  - "Resize Images to 24px (Enhanced)" 
  - "Test All Enhancement Presets"
  - "Generate 24px Composite Image"
  - Individual enhancement preset tasks

### Enhancement Preset Configuration
Customize enhancement settings by editing JSON files in `config/`:

```json
{
    "contrast": 1.4,
    "saturation": 1.8, 
    "brightness": 1.1,
    "sharpness": 1.3,
    "gamma": 0.8,
    "unsharp_mask": true,
    "unsharp_radius": 0.8,
    "unsharp_percent": 120,
    "unsharp_threshold": 2
}
```

### Step 4: Use in Arduino Project
```cpp
#include "data/img_data_70.h"

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

## Enhancement System

### Quality Enhancement Features
The enhanced resize system provides multiple quality improvement techniques:

#### Gamma Correction
- Adjusts mid-tone brightness for LED displays
- Values < 1.0 brighten mid-tones, > 1.0 darken them
- Typical range: 0.7 - 1.2

#### Unsharp Masking
- Enhances edge definition and detail
- **Radius**: Blur radius for edge detection (0.5 - 2.0)
- **Percent**: Enhancement strength (100 - 200)  
- **Threshold**: Minimum difference to apply sharpening (1 - 5)

#### Color Enhancements
- **Contrast**: Overall image contrast (0.8 - 2.0)
- **Saturation**: Color intensity (0.8 - 2.5)
- **Brightness**: Overall brightness (0.9 - 1.3)
- **Sharpness**: Edge sharpness (0.8 - 2.0)

### Preset Characteristics
| Preset | Best For | Contrast | Saturation | Notable Features |
|--------|----------|----------|------------|------------------|
| **Subtle** | Natural images | 1.1x | 1.2x | Gentle enhancement |
| **Vibrant** | Graphics/logos | 1.4x | 1.8x | High color pop |
| **Sharp** | Text/details | 1.3x | 1.4x | Enhanced edges |
| **Warm** | Photos | 1.2x | 1.2x | Warm color tone |
| **Dramatic** | Art/effects | 1.8x | 1.6x | Maximum impact |
| **Soft** | Portraits | 1.0x | 1.1x | Natural and smooth |

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
pip install Pillow numpy  # PIL (Python Imaging Library) + NumPy
```

### Development Environment
- **VS Code** (recommended): Includes pre-configured tasks and workflow
- **Python 3.7+**: Required for all scripts
- **Git**: For version control and collaboration

### Arduino Libraries (for using generated files)
- **FastLED** (recommended for WS2812B control)
- **NeoPixel** (alternative LED library)

## Supported Image Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)  
- BMP (.bmp)
- TIFF (.tiff)
- WebP (.webp)
- GIF (.gif)
- Any format supported by PIL/Pillow

## Example Use Cases

### LED Matrix Applications
- **Digital Art Displays**: Show high-quality images with enhancement processing
- **Interactive Installations**: Dynamic image switching with multiple presets
- **Gaming Displays**: Sprite and graphic display with sharp enhancement
- **Status Indicators**: Clear, readable graphics with appropriate presets

### Workflow Applications  
- **Batch Processing**: Process hundreds of images with consistent settings
- **A/B Testing**: Compare enhancement presets with composite generation
- **Quality Control**: Visual verification through composite images
- **Prototyping**: Rapid iteration with VS Code task integration

### Professional Applications
- **LED Sign Manufacturing**: Consistent image processing workflows
- **Art Installation Design**: Visual preview and quality optimization
- **Product Development**: Embedded display content creation
- **Educational Projects**: LED programming with pre-processed content

## Tips for Best Results

### Image Quality Optimization
1. **Source Images**: Use high-resolution source images (1024px+ recommended)
2. **Contrast**: High-contrast images work best for LED displays
3. **Color Choice**: Vibrant, saturated colors show well on LEDs
4. **Enhancement Selection**: 
   - Use **Vibrant** for logos and graphics
   - Use **Subtle** for photographs
   - Use **Sharp** for text and fine details
   - Use **Dramatic** for artistic effects

### Processing Workflow
1. **Test First**: Process a few images before batch processing
2. **Compare Results**: Use composite generation to compare presets
3. **Memory Planning**: Monitor Arduino memory usage with large image sets
4. **Size Considerations**: Balance image quality vs. memory constraints

### LED Display Optimization
1. **Gamma Correction**: Essential for accurate color representation
2. **Brightness Levels**: Consider viewing environment when setting brightness
3. **Color Calibration**: Test colors on actual LED hardware
4. **Power Management**: Account for power consumption with bright images

### Development Workflow
1. **Use VS Code Tasks**: Streamlined processing with pre-configured tasks
2. **Organize by Size**: Keep different sizes in separate processed directories
3. **Version Control**: Track enhancement settings in config files
4. **Documentation**: Use composite images to document processing results

## License

This project is open source. Feel free to modify and distribute according to your needs.
