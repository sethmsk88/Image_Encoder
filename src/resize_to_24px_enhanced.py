import os
import sys
import json
import argparse
from datetime import datetime
import PIL.Image as Image
from PIL import ImageEnhance, ImageFilter

# Get the project root directory (parent of src)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
import numpy as np

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

def load_enhancement_settings(settings_file=None):
    """
    Load enhancement settings from JSON file
    
    Args:
        settings_file: Path to the JSON settings file
        
    Returns:
        tuple: (settings_dict, preset_name) where preset_name is extracted from filename
    """
    if settings_file is None:
        settings_file = os.path.join(PROJECT_ROOT, "config", "enhancement_settings.json")
    else:
        # If relative path provided, make it relative to project root
        if not os.path.isabs(settings_file):
            settings_file = os.path.join(PROJECT_ROOT, settings_file)
    try:
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                data = json.load(f)
                settings = data.get('enhancement_settings', {})
                print(f"Loaded enhancement settings from '{settings_file}'")
                
                # Extract preset name from filename
                filename = os.path.basename(settings_file)
                if filename.startswith('enhancement_') and filename.endswith('.json'):
                    # Extract the preset name (e.g., "dramatic" from "enhancement_dramatic.json")
                    preset_name = filename[12:-5]  # Remove "enhancement_" prefix and ".json" suffix
                else:
                    preset_name = None
                
                return settings, preset_name
        else:
            print(f"Settings file '{settings_file}' not found. Using default values.")
            return {}, None
    except Exception as e:
        print(f"Error reading settings file '{settings_file}': {e}")
        print("Using default values.")
        return {}, None

def enhance_image_quality(img, enhance_contrast=1.2, enhance_saturation=1.3, enhance_sharpness=1.1, enhance_brightness=1.05):
    """
    Apply multiple enhancements to improve image quality after scaling
    
    Args:
        img: PIL Image object
        enhance_contrast: Contrast multiplier (1.0 = no change, >1.0 = more contrast)
        enhance_saturation: Saturation multiplier (1.0 = no change, >1.0 = more saturated)
        enhance_sharpness: Sharpness multiplier (1.0 = no change, >1.0 = sharper)
        enhance_brightness: Brightness multiplier (1.0 = no change, >1.0 = brighter)
    
    Returns:
        Enhanced PIL Image object
    """
    # Apply contrast enhancement
    if enhance_contrast != 1.0:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(enhance_contrast)
    
    # Apply saturation enhancement
    if enhance_saturation != 1.0:
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(enhance_saturation)
    
    # Apply brightness enhancement
    if enhance_brightness != 1.0:
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(enhance_brightness)
    
    # Apply sharpness enhancement
    if enhance_sharpness != 1.0:
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(enhance_sharpness)
    
    return img

def apply_gamma_correction(img, gamma=0.8):
    """
    Apply gamma correction to brighten mid-tones
    
    Args:
        img: PIL Image object
        gamma: Gamma value (< 1.0 brightens mid-tones, > 1.0 darkens them)
    
    Returns:
        Gamma-corrected PIL Image object
    """
    # Convert to numpy array
    img_array = np.array(img, dtype=np.float32)
    
    # Normalize to 0-1 range
    img_array = img_array / 255.0
    
    # Apply gamma correction
    img_array = np.power(img_array, gamma)
    
    # Convert back to 0-255 range
    img_array = (img_array * 255.0).astype(np.uint8)
    
    # Convert back to PIL Image
    return Image.fromarray(img_array)

def apply_unsharp_mask(img, radius=1.0, percent=150, threshold=3):
    """
    Apply unsharp masking to enhance edge definition
    
    Args:
        img: PIL Image object
        radius: Blur radius for the mask
        percent: Strength of the sharpening effect
        threshold: Minimum difference required to apply sharpening
    
    Returns:
        Sharpened PIL Image object
    """
    # Create a blurred version
    blurred = img.filter(ImageFilter.GaussianBlur(radius))
    
    # Convert to numpy arrays
    original = np.array(img, dtype=np.float32)
    blurred_array = np.array(blurred, dtype=np.float32)
    
    # Calculate the difference (unsharp mask)
    mask = original - blurred_array
    
    # Apply threshold
    mask = np.where(np.abs(mask) < threshold, 0, mask)
    
    # Apply the mask with specified strength
    sharpened = original + (mask * percent / 100.0)
    
    # Clamp values to valid range
    sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
    
    return Image.fromarray(sharpened)

def resize_images_to_24px_enhanced(settings_file=None):
    """
    Resize all images in images/originals to 24 pixels tall with quality enhancements
    and save them to images/processed/24px directory
    
    Args:
        settings_file: Path to the JSON file containing enhancement settings
    """
    # Define directories relative to project root
    source_dir = os.path.join(PROJECT_ROOT, "images", "originals")
    output_dir = os.path.join(PROJECT_ROOT, "images", "processed", "24px")
    target_height = 24
    
    # Load enhancement settings from file
    file_settings, preset_name = load_enhancement_settings(settings_file)
    
    # Enhancement settings with defaults
    settings = {
        'contrast': file_settings.get('contrast', 1.2),           # Default: 20% increase
        'saturation': file_settings.get('saturation', 1.3),       # Default: 30% increase
        'brightness': file_settings.get('brightness', 1.05),      # Default: 5% increase
        'sharpness': file_settings.get('sharpness', 1.1),         # Default: 10% increase
        'gamma': file_settings.get('gamma', 0.85),                # Default: brighten mid-tones
        'unsharp_mask': file_settings.get('unsharp_mask', {}).get('enabled', True),
        'unsharp_radius': file_settings.get('unsharp_mask', {}).get('radius', 0.8),
        'unsharp_percent': file_settings.get('unsharp_mask', {}).get('percent', 120),
        'unsharp_threshold': file_settings.get('unsharp_mask', {}).get('threshold', 2)
    }
    
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
    print("Enhancement settings:")
    print(f"  - Contrast: {settings['contrast']}x")
    print(f"  - Saturation: {settings['saturation']}x")
    print(f"  - Brightness: {settings['brightness']}x")
    print(f"  - Sharpness: {settings['sharpness']}x")
    print(f"  - Gamma correction: {settings['gamma']}")
    print(f"  - Unsharp masking: {'Enabled' if settings['unsharp_mask'] else 'Disabled'}")
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
            
            # Resize image using high-quality Lanczos resampling (better than bicubic for downsampling)
            resized_img = img.resize(new_size, Image.LANCZOS)
            
            # Apply enhancements to combat washed-out appearance
            print(f"Enhancing {rel_path}...")
            
            # 1. Apply basic enhancements (contrast, saturation, brightness, sharpness)
            enhanced_img = enhance_image_quality(
                resized_img,
                enhance_contrast=settings['contrast'],
                enhance_saturation=settings['saturation'],
                enhance_brightness=settings['brightness'],
                enhance_sharpness=settings['sharpness']
            )
            
            # 2. Apply gamma correction to brighten mid-tones
            enhanced_img = apply_gamma_correction(enhanced_img, gamma=settings['gamma'])
            
            # 3. Apply unsharp masking for better edge definition
            if settings['unsharp_mask']:
                enhanced_img = apply_unsharp_mask(
                    enhanced_img,
                    radius=settings['unsharp_radius'],
                    percent=settings['unsharp_percent'],
                    threshold=settings['unsharp_threshold']
                )
            
            # Generate output filename (flatten subdirectory structure)
            filename = os.path.basename(rel_path)
            name, ext = os.path.splitext(filename)
            
            # Include preset name in filename if available
            if preset_name:
                output_filename = f"{name}_24px_{preset_name}{ext}"
            else:
                output_filename = f"{name}_24px{ext}"
            
            output_path = os.path.join(output_dir, output_filename)
            
            # Get unique output path to prevent overwriting
            unique_output_path = get_unique_filename(output_path)
            
            # Save the enhanced resized image
            enhanced_img.save(unique_output_path, quality=95 if ext.lower() in ['.jpg', '.jpeg'] else None)
            
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

def resize_images_to_24px_basic():
    """
    Original basic resize function without enhancements (for comparison)
    """
    # Define directories relative to project root
    source_dir = os.path.join(PROJECT_ROOT, "images", "originals")
    output_dir = os.path.join(PROJECT_ROOT, "images", "processed", "24px")
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
            
            # Resize image using high-quality bicubic interpolation
            resized_img = img.resize(new_size, Image.BICUBIC)
            
            # Generate output filename (flatten subdirectory structure)
            filename = os.path.basename(rel_path)
            name, ext = os.path.splitext(filename)
            output_filename = f"{name}_24px{ext}"
            output_path = os.path.join(output_dir, output_filename)
            
            # Get unique output path to prevent overwriting
            unique_output_path = get_unique_filename(output_path)
            
            # Save the resized image
            resized_img.save(unique_output_path)
            
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
        description="Enhanced image resizer - Scale images to 24 pixels tall with advanced quality enhancements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python resize_to_24px_enhanced.py                      # Interactive mode (default)
  python resize_to_24px_enhanced.py --enhanced           # Enhanced processing using settings file
  python resize_to_24px_enhanced.py --basic              # Basic processing
  python resize_to_24px_enhanced.py --settings custom.json  # Use custom settings file

Enhancement settings are loaded from 'config/enhancement_settings.json'.
Edit this file to customize enhancement parameters.
        """
    )
    
    # Create mutually exclusive group for processing options
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--enhanced', '-e',
        action='store_true',
        help='Use enhanced processing mode with settings from config/enhancement_settings.json'
    )
    mode_group.add_argument(
        '--basic', '-b',
        action='store_true',
        help='Use basic processing mode (simple resize only)'
    )
    mode_group.add_argument(
        '--interactive', '-i',
        action='store_true',
        default=True,
        help='Use interactive mode to choose processing type (default)'
    )
    
    # Settings file argument
    parser.add_argument(
        '--settings', '-s',
        default=None,
        help='Path to JSON settings file (default: config/enhancement_settings.json)'
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    print("Enhanced Image Resizer - Scaling images to 24px height with quality enhancements")
    print("=" * 80)
    
    # Determine processing mode
    if args.enhanced:
        print("\nUsing enhanced processing mode...")
        success = resize_images_to_24px_enhanced(args.settings)
    elif args.basic:
        print("\nUsing basic processing mode...")
        success = resize_images_to_24px_basic()
    else:
        # Interactive mode (default when no arguments provided)
        while True:
            choice = input("\nChoose processing mode:\n1. Enhanced (recommended) - Applies contrast, saturation, and sharpening\n2. Basic - Simple resize only\n\nEnter choice (1 or 2): ").strip()
            
            if choice == '1':
                print("\nUsing enhanced processing mode...")
                success = resize_images_to_24px_enhanced(args.settings)
                break
            elif choice == '2':
                print("\nUsing basic processing mode...")
                success = resize_images_to_24px_basic()
                break
            else:
                print("Invalid choice. Please enter 1 or 2.")
    
    if success:
        print("\nImages have been successfully processed!")
        print("You can now use these images with the image_encoder.py script.")
    else:
        print("\nNo images were processed. Please check the error messages above.")
    
    # Only pause for input in interactive mode
    if not (args.enhanced or args.basic):
        input("\nPress Enter to exit...")
