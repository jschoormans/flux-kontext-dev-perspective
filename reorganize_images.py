#!/usr/bin/env python3
"""
Script to reorganize processed images into train folder with new naming scheme.
- Original images: N_start.jpg
- Vanishing point images: N_end.jpg
- Both in the same folder
- Start counting from 1
"""

import os
import shutil
from pathlib import Path

def reorganize_images():
    """
    Reorganize images into train folder with new naming scheme.
    """
    # Source directories
    images_dir = Path("/Users/Jasper/Projects/kontext_hack/processed_images/images")
    vp_only_dir = Path("/Users/Jasper/Projects/kontext_hack/processed_images/vanishing_points_only")
    
    # Target directory
    train_dir = Path("/Users/Jasper/Projects/kontext_hack/train")
    
    # Ensure train directory exists
    train_dir.mkdir(parents=True, exist_ok=True)
    
    # Get list of original images
    original_images = list(images_dir.glob("*.jpg"))
    original_images.sort()  # Sort to ensure consistent ordering
    
    print(f"Found {len(original_images)} original images")
    
    counter = 1
    
    for original_image in original_images:
        # Get the image ID from filename
        image_id = original_image.stem
        
        # Find corresponding vanishing point image
        vp_image = vp_only_dir / f"{image_id}_vp_only.jpg"
        
        if vp_image.exists():
            # Copy original image as N_end.jpg
            end_name = f"{counter}_end.jpg"
            end_path = train_dir / end_name
            shutil.copy2(original_image, end_path)
            print(f"Copied: {original_image.name} -> {end_name}")
            
            # Copy vanishing point image as N_start.jpg
            start_name = f"{counter}_start.jpg"
            start_path = train_dir / start_name
            shutil.copy2(vp_image, start_path)
            print(f"Copied: {vp_image.name} -> {start_name}")
            
            counter += 1
        else:
            print(f"Warning: No vanishing point image found for {original_image.name}")
    
    print(f"\nReorganization complete!")
    print(f"Created {counter - 1} pairs of images in {train_dir}")
    print(f"Files: 1_start.jpg, 1_end.jpg, 2_start.jpg, 2_end.jpg, ...")

if __name__ == "__main__":
    reorganize_images()
