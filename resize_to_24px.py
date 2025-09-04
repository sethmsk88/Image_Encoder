import os
import sys
import argparse
from datetime import datetime
import PIL.Image as Image
from PIL import ImageEnhance

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

def enhance_small_image(img, contrast_boost=1.15, saturation_boost=1.2, brightness_boost=1.03):
    """
    Apply subtle enhancements to small images to prevent washed-out appearance
    
    Args:
        img: PIL Image object
        contrast_boost: Contrast multiplier (default 1.15 = 15% increase)
        saturation_boost: Saturation multiplier (default 1.2 = 20% increase)
        brightness_boost: Brightness multiplier (default 1.03 = 3% increase)
    
    Returns:
        Enhanced PIL Image object
    """
    # Apply contrast enhancement
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(contrast_boost)
    
    # Apply saturation enhancement to make colors more vivid
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(saturation_boost)
    
    # Apply slight brightness boost
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(brightness_boost)
    
    return img

def resize_images_to_24px(enable_enhancement=True):
    """
    Resize all images in images/originals to 24 pixels tall
    and save them to images/24px directory
    
    Args:
        enable_enhancement: Whether to apply image enhancements (default: True)
    """
    # Define directories
    source_dir = "images/originals"
    output_dir = "images/24px"
    target_height = 24
    
    # Check if source directory exists
    if not os.path.exists(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist!")
        print("Please create the directory and add your original images.")
        return False
    
    # Create output directory if it doesn't exist
    create_directory_if_not_exists(output_dir)
    
    # Get list of image files recursively
    supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    image_files = []
    
    for root, dirs, files in os.walk(source_dir):
        for filename in files:
            file_path = os.path.join(root, filename)
            _, ext = os.path.splitext(filename.lower())
            if ext in supported_extensions:
                # Store relative path from source_dir for better organization
                rel_path = os.path.relpath(file_path, source_dir)
                image_files.append(rel_path)
    
    if not image_files:
        print(f"No supported image files found in '{source_dir}'")
        print(f"Supported formats: {', '.join(supported_extensions)}")
        return False
    
    print(f"Found {len(image_files)} image(s) to process...")
    if enable_enhancement:
        print("Enhancement mode: ENABLED (contrast +15%, saturation +20%, brightness +3%)")
    else:
        print("Enhancement mode: DISABLED (basic resize only)")
    print()
    
    # Process each image
    processed_count = 0
    failed_count = 0
    
    for rel_path in image_files:
        try:
            # Open and convert image to RGB
            source_path = os.path.join(source_dir, rel_path)
            img = Image.open(source_path).convert("RGB")
            
            # Get original dimensions
            orig_width, orig_height = img.size
            
            # Calculate new width maintaining aspect ratio
            new_width = int(float(orig_width) * float(target_height) / float(orig_height))
            new_size = (new_width, target_height)
            
            # Resize image using high-quality Lanczos resampling (better for small images)
            resized_img = img.resize(new_size, Image.LANCZOS)
            
            # Apply enhancements if enabled
            if enable_enhancement:
                final_img = enhance_small_image(resized_img)
            else:
                final_img = resized_img
            
            # Generate output filename
            filename = os.path.basename(rel_path)
            name, ext = os.path.splitext(filename)
            if enable_enhancement:
                output_filename = f"{name}_24px{ext}"
            else:
                output_filename = f"{name}_24px_basic{ext}"
            output_path = os.path.join(output_dir, output_filename)
            
            # Get unique output path to prevent overwriting
            unique_output_path = get_unique_filename(output_path)
            
            # Save the resized image with appropriate quality
            if ext.lower() in ['.jpg', '.jpeg']:
                final_img.save(unique_output_path, quality=95 if enable_enhancement else 85)
            else:
                final_img.save(unique_output_path)
            
            # Show appropriate message
            if unique_output_path != output_path:
                print(f"✓ {rel_path} ({orig_width}x{orig_height}) → {os.path.basename(unique_output_path)} ({new_width}x{target_height}) [timestamped]")
            else:
                print(f"✓ {rel_path} ({orig_width}x{orig_height}) → {output_filename} ({new_width}x{target_height})")
            processed_count += 1
            
        except Exception as e:
            print(f"✗ Failed to process {rel_path}: {e}")
            failed_count += 1
    
    # Summary
    print(f"\nProcessing complete!")
    print(f"Successfully processed: {processed_count} images")
    if failed_count > 0:
        print(f"Failed to process: {failed_count} images")
    print(f"Output directory: {output_dir}")
    
    return processed_count > 0

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Resize images to 24 pixels tall while maintaining aspect ratio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python resize_to_24px.py                    # Enhanced processing (default)
  python resize_to_24px.py --enhance          # Enhanced processing (explicit)
  python resize_to_24px.py --no-enhance       # Basic processing only
  python resize_to_24px.py -e                 # Enhanced processing (short form)
  python resize_to_24px.py -n                 # Basic processing (short form)

Enhancement includes:
  - Contrast boost (+15%)
  - Saturation boost (+20%) 
  - Brightness boost (+3%)
  - Higher quality JPEG compression
        """
    )
    
    # Create mutually exclusive group for enhancement options
    enhance_group = parser.add_mutually_exclusive_group()
    enhance_group.add_argument(
        '--enhance', '-e',
        action='store_true',
        default=True,
        help='Enable image enhancement (default behavior)'
    )
    enhance_group.add_argument(
        '--no-enhance', '-n',
        action='store_true',
        help='Disable image enhancement, basic resize only'
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Determine enhancement setting
    enable_enhancement = not args.no_enhance
    
    print("Image Resizer - Scaling images to 24px height")
    print("=" * 50)
    
    success = resize_images_to_24px(enable_enhancement)
    
    if success:
        mode = "enhanced" if enable_enhancement else "basic"
        print(f"\nImages have been successfully resized to 24 pixels tall ({mode} mode)!")
        print("You can now use these images with the image_encoder.py script.")
    else:
        print("\nNo images were processed. Please check the error messages above.")
    
    input("\nPress Enter to exit...")
