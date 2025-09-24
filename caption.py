#!/usr/bin/env python3
"""
Script to generate captions for vanishing point images using Anthropic's Claude API.
Creates N_caption.txt files for each N_start.jpg image.
"""

import os
import base64
from pathlib import Path
import argparse
import time
from dotenv import load_dotenv
import anthropic
from tqdm import tqdm

# Load environment variables from .env file
load_dotenv()

def encode_image(image_path):
    """
    Encode image to base64 for Anthropic API.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_caption(image_path, api_key, max_retries=3):
    """
    Generate caption for an image using Anthropic's Claude API.
    """
    base64_image = encode_image(image_path)
    
    client = anthropic.Anthropic(api_key=api_key)
    
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=300,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Describe this image in two sentences."
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": base64_image
                                }
                            }
                        ]
                    }
                ]
            )
            
            caption = response.content[0].text
            return caption.strip()
            
        except Exception as e:
            print(f"API Error (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
    
    return None

def process_images(train_dir, api_key, start_from=1, max_images=None):
    """
    Process all vanishing point images and generate captions.
    """
    train_path = Path(train_dir)
    
    # Find all start images
    start_images = list(train_path.glob("*_end.jpg"))
    start_images.sort(key=lambda x: int(x.stem.split('_')[0]))
    
    if max_images:
        start_images = start_images[:max_images]
    
    # Filter to start from specific number
    start_images = [img for img in start_images if int(img.stem.split('_')[0]) >= start_from]
    
    print(f"Found {len(start_images)} images to process")
    
    processed = 0
    failed = 0
    
    # Create progress bar
    pbar = tqdm(start_images, desc="Generating captions", unit="image")
    
    for image_path in pbar:
        image_id = image_path.stem.split('_')[0]
        caption_path = train_path / f"{image_id}_caption.txt"
        
        # Skip if caption already exists
        if caption_path.exists():
            pbar.set_postfix({"Status": f"Skipped {image_id}"})
            continue
        
        pbar.set_postfix({"Status": f"Processing {image_id}"})
        
        caption = generate_caption(image_path, api_key)
        
        if caption:
            # Save caption to file
            with open(caption_path, 'w', encoding='utf-8') as f:
                f.write(caption)
            pbar.set_postfix({"Status": f"✓ {image_id}", "Processed": processed + 1, "Failed": failed})
            processed += 1
        else:
            pbar.set_postfix({"Status": f"✗ {image_id}", "Processed": processed, "Failed": failed + 1})
            failed += 1
        
        # Rate limiting - wait between requests
        time.sleep(1)
    
    print(f"\nProcessing complete!")
    print(f"Successfully processed: {processed}")
    print(f"Failed: {failed}")

def main():
    parser = argparse.ArgumentParser(description='Generate captions for vanishing point images using Anthropic Claude')
    parser.add_argument('--train-dir', default='/Users/Jasper/Projects/kontext_hack/train',
                       help='Directory containing the train images')
    parser.add_argument('--api-key', 
                       help='Anthropic API key (or set ANTHROPIC_API_KEY environment variable)')
    parser.add_argument('--start-from', type=int, default=1,
                       help='Start processing from image number N')
    parser.add_argument('--max-images', type=int,
                       help='Maximum number of images to process')
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: Anthropic API key not provided.")
        print("Set it as an environment variable: export ANTHROPIC_API_KEY='your-key-here'")
        print("Or pass it as an argument: --api-key your-key-here")
        return
    
    # Check if train directory exists
    if not Path(args.train_dir).exists():
        print(f"Error: Train directory {args.train_dir} does not exist")
        return
    
    process_images(args.train_dir, api_key, args.start_from, args.max_images)

if __name__ == "__main__":
    main()
