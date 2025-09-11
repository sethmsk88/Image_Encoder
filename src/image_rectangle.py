import math
import sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import glob
from datetime import datetime

# Get the project root directory (parent of src)  
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

def create_directory_if_not_exists(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

def get_unique_filename(filepath):
    """
    Generate a unique filename by adding timestamp if file already exists
    
    Args:
        filepath: Original file path
        
    Returns:
        str: Unique file path that doesn't exist yet
    """
    if not os.path.exists(filepath):
        return filepath
    
    # File exists, add timestamp
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)
    
    # Generate timestamp string (time only, no date)
    timestamp = datetime.now().strftime("%H%M%S")
    
    # Create new filename with timestamp
    new_filename = f"{name}_{timestamp}{ext}"
    new_filepath = os.path.join(directory, new_filename)
    
    # If somehow this still exists (unlikely), add milliseconds
    if os.path.exists(new_filepath):
        timestamp_ms = datetime.now().strftime("%H%M%S_%f")[:-3]  # Remove last 3 digits for milliseconds
        new_filename = f"{name}_{timestamp_ms}{ext}"
        new_filepath = os.path.join(directory, new_filename)
    
    return new_filepath

def create_single_rectangle_image(data_file: str, scale_factor: int = 5):
    """Create a single rectangle image from a .dat file and return the PIL Image object"""
    # Read the file
    with open(data_file, 'r') as file:
        lines = file.readlines()

    # Parse data
    num_cols = int(lines[0].strip())
    num_rows = 24  # Fixed height
    hex_string = lines[1].strip()

    # Split into RGB hex values
    hex_values = [hex_string[i:i+6] for i in range(0, len(hex_string), 6)]
    pixels = [(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)) for h in hex_values]

    # Validate pixel count
    expected_pixels = num_cols * num_rows
    if len(pixels) != expected_pixels:
        raise ValueError(f"Pixel count mismatch in {data_file}! Expected {expected_pixels}, got {len(pixels)}")

    # Calculate how many times to repeat the image to reach at least 30 pixels wide
    min_width = 30
    repeat_count = max(1, (min_width + num_cols - 1) // num_cols)  # Ceiling division
    final_width = num_cols * repeat_count
    
    # Create blank image (width = final_width, height = num_rows)
    rect_img = Image.new("RGB", (final_width, num_rows), (0, 0, 0))
    pixels_out = rect_img.load()

    # Draw columns from left to right, repeating the pattern
    for repeat in range(repeat_count):
        for col in range(num_cols):
            final_col = repeat * num_cols + col
            for row in range(num_rows):
                # Calculate pixel index (same as circle version)
                idx = col * num_rows + row
                color = pixels[idx]
                
                # Set pixel at (final_column, row)
                pixels_out[final_col, row] = color

    # Scale up the image with slight blending
    scaled_size = (final_width * scale_factor, num_rows * scale_factor)
    if scale_factor > 1:
        # Use Bilinear resampling for high-quality downsampling
        rect_img = rect_img.resize(scaled_size, Image.BILINEAR)

    return rect_img

def create_single_image_scaled(image_file: str, scale_factor: int = 5):
    """Create a scaled image from an image file and return the PIL Image object"""
    try:
        # Open and convert image to RGB
        img = Image.open(image_file).convert("RGB")
        
        # Scale up the image
        original_size = img.size
        scaled_size = (original_size[0] * scale_factor, original_size[1] * scale_factor)
        
        # Use high-quality resampling for scaling
        if scale_factor > 1:
            scaled_img = img.resize(scaled_size, Image.LANCZOS)
        else:
            scaled_img = img
        
        return scaled_img
        
    except Exception as e:
        raise ValueError(f"Error processing image {image_file}: {e}")

def create_led_rectangle_image(data_file: str, output_file: str, scale_factor: int = 5):
    """Create a single rectangle image and save it - legacy function for single file processing"""
    rect_img = create_single_rectangle_image(data_file, scale_factor)
    
    # Save image with unique filename
    unique_output_file = get_unique_filename(output_file)
    rect_img.save(unique_output_file)
    
    if unique_output_file != output_file:
        print(f"File already existed, saved with timestamp: {unique_output_file}")
        print(f"Rectangle image saved (scaled {scale_factor}x, size: {rect_img.size[0]}x{rect_img.size[1]})")
    else:
        print(f"Rectangle image saved to {unique_output_file} (scaled {scale_factor}x, size: {rect_img.size[0]}x{rect_img.size[1]})")

def find_dat_files_grouped(directory):
    """Find all .dat files grouped by subdirectory"""
    groups = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.dat'):
                # Get relative path from the input directory
                rel_path = os.path.relpath(root, directory)
                if rel_path == '.':
                    group_name = 'root'
                else:
                    group_name = rel_path.replace('\\', '/').replace('/', '_')
                
                if group_name not in groups:
                    groups[group_name] = []
                groups[group_name].append(os.path.join(root, file))
    
    # Sort files within each group
    for group in groups:
        groups[group] = sorted(groups[group])
    
    return groups

def find_image_files_grouped(directory):
    """Find all image files grouped by subdirectory"""
    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    
    groups = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_lower = file.lower()
            if any(file_lower.endswith(ext) for ext in image_extensions):
                # Get relative path from the input directory
                rel_path = os.path.relpath(root, directory)
                if rel_path == '.':
                    group_name = 'root'
                else:
                    group_name = rel_path.replace('\\', '/').replace('/', '_')
                
                if group_name not in groups:
                    groups[group_name] = []
                groups[group_name].append(os.path.join(root, file))
    
    # Sort files within each group
    for group in groups:
        groups[group] = sorted(groups[group])
    
    return groups

def detect_file_type(directory):
    """Detect whether directory contains .dat files or image files"""
    dat_count = 0
    image_count = 0
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.dat'):
                dat_count += 1
            elif any(file.lower().endswith(ext) for ext in image_extensions):
                image_count += 1
    
    if dat_count > 0 and image_count > 0:
        return 'mixed'
    elif dat_count > 0:
        return 'dat'
    elif image_count > 0:
        return 'image'
    else:
        return 'none'

def find_dat_files(directory):
    """Legacy function - find all .dat files in directory and subdirectories (for backward compatibility)"""
    dat_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.dat'):
                dat_files.append(os.path.join(root, file))
    return sorted(dat_files)

def get_font(size=12):
    """Get a font, fallback to default if specific font not available"""
    try:
        # Try to use a common system font
        return ImageFont.truetype("arial.ttf", size)
    except:
        try:
            # Try another common font
            return ImageFont.truetype("calibri.ttf", size)
        except:
            # Fall back to default font
            return ImageFont.load_default()

def create_text_image(text, font_size=16, text_color=(255, 255, 255), bg_color=(0, 0, 0)):
    """Create an image containing the specified text"""
    font = get_font(font_size)
    
    # Calculate text size
    temp_img = Image.new('RGB', (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)
    bbox = temp_draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Add more padding to account for font descenders and larger fonts
    horizontal_padding = 10
    vertical_padding = max(12, font_size // 3)  # Increased base padding and ratio
    
    # Create image with text and proper padding
    img_width = text_width + (horizontal_padding * 2)
    img_height = text_height + (vertical_padding * 2)
    img = Image.new('RGB', (img_width, img_height), bg_color)
    draw = ImageDraw.Draw(img)
    draw.text((horizontal_padding, vertical_padding), text, fill=text_color, font=font)
    
    return img

def create_composite_image(directory: str, output_file: str, scale_factor: int = 5, max_width: int = 2000, gap: int = 2, image_gap: int = 10):
    """Create a composite image from all files in a directory, supporting both .dat and image files"""
    
    # Detect file type in directory
    file_type = detect_file_type(directory)
    
    if file_type == 'none':
        print(f"No .dat or image files found in {directory}")
        return
    elif file_type == 'mixed':
        print(f"Directory contains both .dat and image files. Processing .dat files only.")
        file_type = 'dat'
    
    # Get file groups based on type
    if file_type == 'dat':
        file_groups = find_dat_files_grouped(directory)
        print(f"Processing .dat files...")
    else:  # file_type == 'image'
        file_groups = find_image_files_grouped(directory)
        print(f"Processing image files...")
    
    if not file_groups:
        print(f"No valid files found in {directory}")
        return
    
    total_files = sum(len(files) for files in file_groups.values())
    print(f"Found {total_files} files in {len(file_groups)} groups")
    
    # Process all images and organize by groups
    all_elements = []  # List of (type, data) tuples where type is 'header', 'image', or 'label'
    
    for group_name in sorted(file_groups.keys()):
        files = file_groups[group_name]
        
        # Add group header
        group_header = create_text_image(f"Group {group_name}", font_size=40, text_color=(255, 255, 0))
        all_elements.append(('header', group_header))
        
        # Process images in this group
        group_images = []
        for file_path in files:
            try:
                # Process based on file type
                if file_type == 'dat':
                    img = create_single_rectangle_image(file_path, scale_factor)
                else:  # image files
                    img = create_single_image_scaled(file_path, scale_factor)
                
                filename = os.path.splitext(os.path.basename(file_path))[0]
                label_img = create_text_image(filename, font_size=26, text_color=(200, 200, 200))
                
                group_images.append((img, label_img, filename))
                print(f"Processed: {file_path}")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        # Add images with labels to elements
        all_elements.append(('images', group_images))
    
    if not any(element[0] == 'images' and element[1] for element in all_elements):
        print("No valid images to composite")
        return
    
    # Calculate layout for the entire composite
    composite_sections = []
    total_height = 0
    
    for element_type, element_data in all_elements:
        if element_type == 'header':
            # Header takes full width with extra spacing
            header_spacing = gap * 4  # More spacing around headers
            section_height = element_data.size[1] + header_spacing
            composite_sections.append(('header', element_data, section_height))
            total_height += section_height
            
        elif element_type == 'images' and element_data:
            # Layout images in rows
            rows = []
            current_row = []
            current_width = 0
            
            for img, label_img, filename in element_data:
                # Calculate combined height (image + label + larger gap for bigger fonts)
                label_gap = 4  # Increased gap between image and label
                combined_height = img.size[1] + label_img.size[1] + label_gap
                img_width = max(img.size[0], label_img.size[0])
                width_with_gap = img_width + (image_gap if current_row else 0)
                
                if current_width + width_with_gap > max_width and current_row:
                    rows.append(current_row)
                    current_row = [(img, label_img, filename)]
                    current_width = img_width
                else:
                    current_row.append((img, label_img, filename))
                    current_width += width_with_gap
            
            if current_row:
                rows.append(current_row)
            
            # Calculate section height with proper spacing for larger fonts
            row_gap = gap * 4  # Further increased gap between rows
            section_height = sum(
                4 + max(img.size[1] + label.size[1] + 8 for img, label, _ in row) + row_gap  # +4 for top+bottom borders
                for row in rows
            ) + gap * 3 + 6  # More extra spacing at end of each group + 6 pixels for purple border
            
            composite_sections.append(('images', rows, section_height))
            total_height += section_height
    
    # Create composite image
    composite = Image.new("RGB", (max_width, total_height), (0, 0, 0))
    
    # Place all sections
    y_offset = 0
    for section_type, section_data, section_height in composite_sections:
        if section_type == 'header':
            # Center the header
            header_x = (max_width - section_data.size[0]) // 2
            composite.paste(section_data, (header_x, y_offset))
            # Use much larger gap after headers to prevent overlap
            header_gap = gap * 6  # Six times the gap for headers with large fonts
            y_offset += section_data.size[1] + header_gap
            
        elif section_type == 'images':
            rows = section_data
            for row in rows:
                # Draw top white border for the row
                draw = ImageDraw.Draw(composite)
                draw.rectangle([0, y_offset, max_width, y_offset + 2], fill=(255, 255, 255))
                y_offset += 2  # Move past the top border
                
                x_offset = 0
                label_gap = 8  # Further increased gap between image and label
                row_height = max(img.size[1] + label.size[1] + label_gap for img, label, _ in row)
                
                for i, (img, label_img, filename) in enumerate(row):
                    # Center image and label within their allocated width
                    item_width = max(img.size[0], label_img.size[0])
                    img_x = x_offset + (item_width - img.size[0]) // 2
                    label_x = x_offset + (item_width - label_img.size[0]) // 2
                    
                    # Place image and label with consistent spacing
                    composite.paste(img, (img_x, y_offset))
                    composite.paste(label_img, (label_x, y_offset + img.size[1] + label_gap))
                    
                    x_offset += item_width
                    
                    # Fill gap between images with white pixels (only middle 2 columns)
                    if i < len(row) - 1:
                        # Create white rectangle for the gap - only middle 2 pixels
                        gap_start_x = x_offset + (image_gap // 2) - 1  # Center the 2-pixel white area
                        gap_width = 2  # Only 2 pixels wide
                        gap_height = row_height
                        
                        # Draw white rectangle in the middle of the gap area
                        draw = ImageDraw.Draw(composite)
                        draw.rectangle([gap_start_x, y_offset, gap_start_x + gap_width, y_offset + gap_height], 
                                     fill=(255, 255, 255))
                        
                        x_offset += image_gap
                
                y_offset += row_height  # Move past the row content
                
                # Draw bottom white border for the row
                draw.rectangle([0, y_offset, max_width, y_offset + 2], fill=(255, 255, 255))
                y_offset += 2  # Move past the bottom border
                
                row_gap = gap * 4  # Increased row gap to match calculations
                y_offset += row_gap
            
            # Draw purple border line after the last row of images in the group
            draw = ImageDraw.Draw(composite)
            draw.rectangle([0, y_offset, max_width, y_offset + 6], fill=(128, 0, 128))  # Purple color, 6 pixels thick
            y_offset += 6  # Move past the purple border
        
        # y_offset is now correctly positioned for the next section
    
    # Save composite with unique filename
    unique_output_file = get_unique_filename(output_file)
    composite.save(unique_output_file)
    
    if unique_output_file != output_file:
        print(f"File already existed, saved with timestamp: {unique_output_file}")
    else:
        print(f"Composite image saved to {unique_output_file}")
    
    print(f"Final size: {composite.size[0]}x{composite.size[1]} pixels")
    print(f"Total groups: {len(file_groups)}")
    print(f"Total files: {total_files}")
    print(f"File type processed: {file_type}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python image_rectangle.py <data_file_or_directory> [scale_factor]")
        print("  For single .dat file: python image_rectangle.py file.dat [scale_factor]")
        print("  For .dat directory:   python image_rectangle.py img_data/ [scale_factor]")
        print("  For image directory:  python src/image_rectangle.py images/processed/24px/ [scale_factor]")
        print("  ")
        print("Supports:")
        print("  - .dat files (LED data format)")
        print("  - Image files (.jpg, .jpeg, .png, .bmp, .gif, .tiff, .webp)")
        print("  - Mixed directories (prioritizes .dat files)")
        sys.exit(1)

    input_path = sys.argv[1]
    scale_factor = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    # Create output directory if it doesn't exist
    output_dir = "output_images"
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if input is a directory or file
    if os.path.isdir(input_path):
        # Directory mode - create composite image
        # Create composites directory for composite output images
        composites_dir = os.path.join(PROJECT_ROOT, "images", "composites")
        os.makedirs(composites_dir, exist_ok=True)
        
        dir_name = os.path.basename(os.path.normpath(input_path))
        
        # Detect file type to determine output filename
        file_type = detect_file_type(input_path)
        if file_type == 'dat' or file_type == 'mixed':
            output_file = os.path.join(composites_dir, f"{dir_name}_composite_rectangle.png")
        elif file_type == 'image':
            output_file = os.path.join(composites_dir, f"{dir_name}_composite_scaled.png")
        else:
            print(f"No supported files found in {input_path}")
            sys.exit(1)
        
        create_composite_image(input_path, output_file, scale_factor)
    elif os.path.isfile(input_path) and input_path.endswith('.dat'):
        # Single .dat file mode - still uses output_images directory
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_file = os.path.join(output_dir, f"{base_name}_rectangle.png")
        create_led_rectangle_image(input_path, output_file, scale_factor)
    else:
        print(f"Error: '{input_path}' is not a valid .dat file or directory containing supported files")
        print("Supported file types: .dat files or image files (.jpg, .jpeg, .png, .bmp, .gif, .tiff, .webp)")
        sys.exit(1)
