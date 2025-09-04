import os
import sys
import PIL.Image as Image

def create_directory_if_not_exists(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

def resize_images_to_24px():
    """
    Resize all images in images/originals to 24 pixels tall
    and save them to images/24px directory
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
    
    # Get list of image files
    supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    image_files = []
    
    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)
        if os.path.isfile(file_path):
            _, ext = os.path.splitext(filename.lower())
            if ext in supported_extensions:
                image_files.append(filename)
    
    if not image_files:
        print(f"No supported image files found in '{source_dir}'")
        print(f"Supported formats: {', '.join(supported_extensions)}")
        return False
    
    print(f"Found {len(image_files)} image(s) to process...")
    
    # Process each image
    processed_count = 0
    failed_count = 0
    
    for filename in image_files:
        try:
            # Open and convert image to RGB
            source_path = os.path.join(source_dir, filename)
            img = Image.open(source_path).convert("RGB")
            
            # Get original dimensions
            orig_width, orig_height = img.size
            
            # Calculate new width maintaining aspect ratio
            new_width = int(float(orig_width) * float(target_height) / float(orig_height))
            new_size = (new_width, target_height)
            
            # Resize image using high-quality bicubic interpolation
            resized_img = img.resize(new_size, Image.BICUBIC)
            
            # Generate output filename
            name, ext = os.path.splitext(filename)
            output_filename = f"{name}_24px{ext}"
            output_path = os.path.join(output_dir, output_filename)
            
            # Save the resized image
            resized_img.save(output_path)
            
            print(f"✓ {filename} ({orig_width}x{orig_height}) → {output_filename} ({new_width}x{target_height})")
            processed_count += 1
            
        except Exception as e:
            print(f"✗ Failed to process {filename}: {e}")
            failed_count += 1
    
    # Summary
    print(f"\nProcessing complete!")
    print(f"Successfully processed: {processed_count} images")
    if failed_count > 0:
        print(f"Failed to process: {failed_count} images")
    print(f"Output directory: {output_dir}")
    
    return processed_count > 0

if __name__ == "__main__":
    print("Image Resizer - Scaling images to 24px height")
    print("=" * 50)
    
    success = resize_images_to_24px()
    
    if success:
        print("\nImages have been successfully resized to 24 pixels tall!")
        print("You can now use these images with the image_encoder.py script.")
    else:
        print("\nNo images were processed. Please check the error messages above.")
    
    input("\nPress Enter to exit...")
