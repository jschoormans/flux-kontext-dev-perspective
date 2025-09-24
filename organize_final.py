#!/usr/bin/env python3
"""
Script to organize train files into three folders:
- train_control: vanishing point images (N_start.jpg -> N.jpg)
- train_end: original images (N_end.jpg -> N.jpg) 
- train_captions: caption files (N_caption.txt -> N.txt)
"""

import shutil
from pathlib import Path

def organize_final_files(train_dir, output_base_dir):
    """
    Organize files from train directory into three separate folders.
    """
    train_path = Path(train_dir)
    output_base_path = Path(output_base_dir)
    
    # Create output directories
    control_dir = output_base_path / "train_control"
    end_dir = output_base_path / "train_end"
    
    for dir_path in [control_dir, end_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
        # Clear existing files
        for f in dir_path.iterdir():
            if f.is_file():
                f.unlink()
    
    print("Organizing files...")
    
    # Find all start images (vanishing points)
    start_images = sorted(list(train_path.glob("*_start.jpg")))
    print(f"Found {len(start_images)} vanishing point images")
    
    processed = 0
    
    for start_image in start_images:
        image_id = start_image.stem.split('_')[0]
        
        # Copy vanishing point image to train_control (N_start.jpg -> N.jpg)
        control_dest = control_dir / f"{image_id}.jpg"
        shutil.copy2(start_image, control_dest)
        
        # Copy original image to train_end (N_end.jpg -> N.jpg)
        end_image = train_path / f"{image_id}_end.jpg"
        if end_image.exists():
            end_dest = end_dir / f"{image_id}.jpg"
            shutil.copy2(end_image, end_dest)
        else:
            print(f"Warning: No end image found for {image_id}")
        
        # Copy caption to train_end (N_caption.txt -> N.txt)
        caption_file = train_path / f"{image_id}_caption.txt"
        if caption_file.exists():
            caption_dest = end_dir / f"{image_id}.txt"
            shutil.copy2(caption_file, caption_dest)
        else:
            print(f"Warning: No caption found for {image_id}")
        
        processed += 1
        if processed % 100 == 0:
            print(f"Processed {processed} files...")
    
    print(f"\nOrganization complete!")
    print(f"Processed {processed} image sets")
    print(f"Files organized into:")
    print(f"  - train_control: {len(list(control_dir.glob('*.jpg')))} vanishing point images")
    print(f"  - train_end: {len(list(end_dir.glob('*.jpg')))} original images + {len(list(end_dir.glob('*.txt')))} caption files")

if __name__ == "__main__":
    train_directory = "/Users/Jasper/Projects/kontext_hack/train"
    output_directory = "/Users/Jasper/Projects/kontext_hack"
    organize_final_files(train_directory, output_directory)
