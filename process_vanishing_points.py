#!/usr/bin/env python3
"""
Script to process images with vanishing point data from AVA dataset.
Creates overlays with vanishing points and separate images with only vanishing points.
"""

import os
import shutil
import numpy as np
import cv2
from pathlib import Path
import argparse

def calculate_vanishing_point(line1, line2):
    """
    Calculate the vanishing point from two lines.
    Each line is represented as [x1, y1, x2, y2]
    """
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2
    
    # Convert to homogeneous coordinates
    line1_hom = np.cross([x1, y1, 1], [x2, y2, 1])
    line2_hom = np.cross([x3, y3, 1], [x4, y4, 1])
    
    # Find intersection (vanishing point)
    vanishing_point = np.cross(line1_hom, line2_hom)
    
    if vanishing_point[2] != 0:
        vanishing_point = vanishing_point / vanishing_point[2]
        return int(vanishing_point[0]), int(vanishing_point[1])
    else:
        return None, None

def read_vp_data(vp_file):
    """
    Read vanishing point data from a .txt file.
    Returns image dimensions and two lines defining the vanishing point.
    """
    with open(vp_file, 'r') as f:
        lines = f.readlines()
    
    # First line: width height
    width, height = map(int, lines[0].strip().split())
    
    # Second and third lines: the two lines
    line1 = list(map(float, lines[1].strip().split()))
    line2 = list(map(float, lines[2].strip().split()))
    
    return width, height, line1, line2

def create_overlay_image(image_path, vp_file, output_path):
    """
    Create an overlay image with vanishing point and lines marked.
    """
    # Read vanishing point data first to get original dimensions
    vp_width, vp_height, line1, line2 = read_vp_data(vp_file)
    
    # Read the original image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Could not read image: {image_path}")
        return False
    
    # Get current image dimensions
    current_height, current_width = image.shape[:2]
    
    # Scale the line coordinates to match the current image size
    scale_x = current_width / vp_width
    scale_y = current_height / vp_height
    
    # Scale the line coordinates
    scaled_line1 = [line1[0] * scale_x, line1[1] * scale_y, line1[2] * scale_x, line1[3] * scale_y]
    scaled_line2 = [line2[0] * scale_x, line2[1] * scale_y, line2[2] * scale_x, line2[3] * scale_y]
    
    # Calculate vanishing point using scaled coordinates
    vp_x, vp_y = calculate_vanishing_point(scaled_line1, scaled_line2)
    
    if vp_x is None or vp_y is None:
        print(f"Could not calculate vanishing point for {vp_file}")
        return False
    
    # Check if vanishing point is outside image boundaries
    if vp_x < 0 or vp_x >= current_width or vp_y < 0 or vp_y >= current_height:
        print(f"Vanishing point ({vp_x}, {vp_y}) is outside image boundaries ({current_width}x{current_height}) - skipping")
        return False
    
    # Create a copy for overlay
    overlay = image.copy()
    
    # Draw the two lines using scaled coordinates
    cv2.line(overlay, (int(scaled_line1[0]), int(scaled_line1[1])), (int(scaled_line1[2]), int(scaled_line1[3])), (0, 255, 0), 3)
    cv2.line(overlay, (int(scaled_line2[0]), int(scaled_line2[1])), (int(scaled_line2[2]), int(scaled_line2[3])), (0, 255, 0), 3)
    
    # Draw the vanishing point
    cv2.circle(overlay, (vp_x, vp_y), 10, (0, 0, 255), -1)
    cv2.circle(overlay, (vp_x, vp_y), 15, (255, 255, 255), 2)
    
    # Add text label
    cv2.putText(overlay, f"VP: ({vp_x}, {vp_y})", (vp_x + 20, vp_y - 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Save the overlay
    cv2.imwrite(output_path, overlay)
    return True

def create_vanishing_point_only(image_path, vp_file, output_path):
    """
    Create an image with only the vanishing point marked on a black background.
    Shows red dot with equi-angular grid lines radiating from it.
    """
    # Read vanishing point data first to get original dimensions
    vp_width, vp_height, line1, line2 = read_vp_data(vp_file)
    
    # Read the original image to get its dimensions
    image = cv2.imread(image_path)
    if image is None:
        print(f"Could not read image: {image_path}")
        return False
    
    # Get current image dimensions
    current_height, current_width = image.shape[:2]
    
    # Scale the line coordinates to match the current image size
    scale_x = current_width / vp_width
    scale_y = current_height / vp_height
    
    # Scale the line coordinates
    scaled_line1 = [line1[0] * scale_x, line1[1] * scale_y, line1[2] * scale_x, line1[3] * scale_y]
    scaled_line2 = [line2[0] * scale_x, line2[1] * scale_y, line2[2] * scale_x, line2[3] * scale_y]
    
    # Calculate vanishing point using scaled coordinates
    vp_x, vp_y = calculate_vanishing_point(scaled_line1, scaled_line2)
    
    if vp_x is None or vp_y is None:
        print(f"Could not calculate vanishing point for {vp_file}")
        return False
    
    # Check if vanishing point is outside image boundaries
    if vp_x < 0 or vp_x >= current_width or vp_y < 0 or vp_y >= current_height:
        print(f"Vanishing point ({vp_x}, {vp_y}) is outside image boundaries ({current_width}x{current_height}) - skipping")
        return False
    
    # Create black background with current image dimensions
    vp_image = np.zeros((current_height, current_width, 3), dtype=np.uint8)
    
    # Draw equi-angular grid lines radiating from vanishing point (every 20 degrees)
    import math
    for angle in range(0, 360, 20):
        # Convert angle to radians
        angle_rad = math.radians(angle)
        
        # Calculate line endpoints - extend to image boundaries
        # We'll draw lines that extend from the vanishing point to the image edges
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)
        
        # Calculate intersections with image boundaries
        intersections = []
        
        # Top edge (y = 0)
        if sin_angle != 0:
            t = -vp_y / sin_angle
            if t > 0:
                x = vp_x + t * cos_angle
                if 0 <= x <= current_width:
                    intersections.append((int(x), 0))
        
        # Bottom edge (y = current_height)
        if sin_angle != 0:
            t = (current_height - vp_y) / sin_angle
            if t > 0:
                x = vp_x + t * cos_angle
                if 0 <= x <= current_width:
                    intersections.append((int(x), current_height))
        
        # Left edge (x = 0)
        if cos_angle != 0:
            t = -vp_x / cos_angle
            if t > 0:
                y = vp_y + t * sin_angle
                if 0 <= y <= current_height:
                    intersections.append((0, int(y)))
        
        # Right edge (x = current_width)
        if cos_angle != 0:
            t = (current_width - vp_x) / cos_angle
            if t > 0:
                y = vp_y + t * sin_angle
                if 0 <= y <= current_height:
                    intersections.append((current_width, int(y)))
        
        # Draw line from vanishing point to the intersection point
        if intersections:
            # Choose the closest intersection to avoid lines going outside the image
            closest_intersection = min(intersections, 
                                     key=lambda p: math.sqrt((p[0] - vp_x)**2 + (p[1] - vp_y)**2))
            cv2.line(vp_image, (vp_x, vp_y), closest_intersection, (0, 0, 255), 2)
    
    # Draw the vanishing point as a red dot
    cv2.circle(vp_image, (vp_x, vp_y), 8, (0, 0, 255), -1)
    cv2.circle(vp_image, (vp_x, vp_y), 12, (0, 0, 255), 2)
    
    # Save the vanishing point only image
    cv2.imwrite(output_path, vp_image)
    return True

def copy_relevant_images(source_dir, vp_labels_dir, target_dir, max_images=50):
    """
    Copy images that have corresponding vanishing point labels.
    """
    copied_count = 0
    
    # Get list of available vanishing point files
    vp_files = list(Path(vp_labels_dir).glob("*.txt"))
    
    for vp_file in vp_files:
        if copied_count >= max_images:
            break
            
        # Get the image ID from the filename
        image_id = vp_file.stem
        
        # Look for corresponding image in source directory
        source_image = Path(source_dir) / f"{image_id}.jpg"
        
        if source_image.exists():
            target_image = Path(target_dir) / f"{image_id}.jpg"
            shutil.copy2(source_image, target_image)
            print(f"Copied: {source_image} -> {target_image}")
            copied_count += 1
        else:
            print(f"Image not found: {source_image}")
    
    print(f"Copied {copied_count} images")
    return copied_count

def process_all_images(images_dir, vp_labels_dir, overlays_dir, vp_only_dir):
    """
    Process all images in the directory.
    """
    processed_count = 0
    
    for image_file in Path(images_dir).glob("*.jpg"):
        image_id = image_file.stem
        vp_file = Path(vp_labels_dir) / f"{image_id}.txt"
        
        if vp_file.exists():
            # Create overlay
            overlay_path = Path(overlays_dir) / f"{image_id}_overlay.jpg"
            if create_overlay_image(str(image_file), str(vp_file), str(overlay_path)):
                print(f"Created overlay: {overlay_path}")
            
            # Create vanishing point only
            vp_only_path = Path(vp_only_dir) / f"{image_id}_vp_only.jpg"
            if create_vanishing_point_only(str(image_file), str(vp_file), str(vp_only_path)):
                print(f"Created VP only: {vp_only_path}")
                processed_count += 1
        else:
            print(f"No vanishing point data for: {image_file}")
    
    print(f"Processed {processed_count} images")
    return processed_count

def main():
    parser = argparse.ArgumentParser(description='Process images with vanishing point data')
    parser.add_argument('--source-dir', default='/Users/Jasper/Downloads/archive (2)/images',
                       help='Source directory containing original images')
    parser.add_argument('--vp-labels-dir', default='/Users/Jasper/Projects/kontext_hack/exp/download_ava/vp-labels/AVA_landscape',
                       help='Directory containing vanishing point label files')
    parser.add_argument('--target-dir', default='/Users/Jasper/Projects/kontext_hack/processed_images',
                       help='Target directory for processed images')
    parser.add_argument('--max-images', type=int, default=50,
                       help='Maximum number of images to process')
    
    args = parser.parse_args()
    
    # Create output directories
    overlays_dir = Path(args.target_dir) / "overlays"
    vp_only_dir = Path(args.target_dir) / "vanishing_points_only"
    images_dir = Path(args.target_dir) / "images"
    
    overlays_dir.mkdir(parents=True, exist_ok=True)
    vp_only_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    
    print("Step 1: Copying relevant images...")
    copied_count = copy_relevant_images(args.source_dir, args.vp_labels_dir, str(images_dir), args.max_images)
    
    if copied_count > 0:
        print("\nStep 2: Processing images with vanishing points...")
        processed_count = process_all_images(str(images_dir), args.vp_labels_dir, str(overlays_dir), str(vp_only_dir))
        
        print(f"\nSummary:")
        print(f"- Copied {copied_count} images")
        print(f"- Processed {processed_count} images with vanishing points")
        print(f"- Overlays saved to: {overlays_dir}")
        print(f"- Vanishing point only images saved to: {vp_only_dir}")
    else:
        print("No images were copied. Please check the source directory and image IDs.")

if __name__ == "__main__":
    main()
