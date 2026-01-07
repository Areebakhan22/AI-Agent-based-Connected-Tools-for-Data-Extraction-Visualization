#!/usr/bin/env python3
"""
Copy existing generated images and metadata to frontend.
This script ensures all images are available in the frontend/public/generated_images folder.
"""

import shutil
import json
from pathlib import Path

def main():
    print("=" * 70)
    print("📦 Copying Images and Metadata to Frontend")
    print("=" * 70)
    print()
    
    # Source and destination paths
    source_images = Path("generated_images")
    source_metadata = Path("relationship_images_metadata.json")
    source_json = Path("pipeline_output.json")
    
    dest_public = Path("frontend/public")
    dest_images = dest_public / "generated_images"
    
    # Create destination directories
    dest_public.mkdir(parents=True, exist_ok=True)
    dest_images.mkdir(parents=True, exist_ok=True)
    
    files_copied = []
    
    # Copy JSON file
    if source_json.exists():
        shutil.copy(source_json, dest_public / "pipeline_output.json")
        files_copied.append("✓ pipeline_output.json")
    
    # Copy metadata
    if source_metadata.exists():
        shutil.copy(source_metadata, dest_public / "relationship_images_metadata.json")
        files_copied.append("✓ relationship_images_metadata.json")
    
    # Copy all PNG images
    if source_images.exists():
        image_count = 0
        for img_file in source_images.glob("*.png"):
            # Skip prompt files
            if img_file.name.endswith(".prompt.txt"):
                continue
            shutil.copy(img_file, dest_images / img_file.name)
            image_count += 1
        
        if image_count > 0:
            files_copied.append(f"✓ {image_count} images")
    
    print("Files copied:")
    for f in files_copied:
        print(f"  {f}")
    
    print()
    print("=" * 70)
    print("✅ Files copied to frontend!")
    print("=" * 70)
    print()
    print("📋 Next steps:")
    print("   cd frontend && npm run dev")
    print()

if __name__ == '__main__':
    main()

