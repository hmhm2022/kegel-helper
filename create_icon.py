#!/usr/bin/env python3
"""
Create a simple icon file for Tauri
"""
from PIL import Image, ImageDraw
import os

def create_icon():
    # Create a simple 512x512 image
    size = 512
    img = Image.new('RGBA', (size, size), (76, 175, 80, 255))  # Green background

    # Draw a simple "TG" text
    draw = ImageDraw.Draw(img)

    # Draw a circle
    margin = 50
    draw.ellipse([margin, margin, size-margin, size-margin], fill=(255, 255, 255, 255))

    # Save as PNG first
    img.save('app-icon.png')
    print("Created app-icon.png")

    # Create different sizes for Tauri
    sizes = [32, 128, 256, 512]

    # Create icons directory if it doesn't exist
    os.makedirs('src-tauri/icons', exist_ok=True)
    print("Created src-tauri/icons directory")

    # Generate all required icon sizes
    for s in sizes:
        resized = img.resize((s, s), Image.Resampling.LANCZOS)

        # Save standard sizes
        resized.save(f'src-tauri/icons/{s}x{s}.png')
        print(f"Created {s}x{s}.png")

        # Save specific required files
        if s == 32:
            resized.save('src-tauri/icons/32x32.png')
        elif s == 128:
            resized.save('src-tauri/icons/128x128.png')
            resized.save('src-tauri/icons/128x128@2x.png')
            print("Created 128x128@2x.png")

    # Save as ICO for Windows
    try:
        img.save('src-tauri/icons/icon.ico', format='ICO', sizes=[(32, 32), (64, 64), (128, 128), (256, 256)])
        print("Created icon.ico")
    except Exception as e:
        print(f"Warning: Could not create ICO file: {e}")

    # For macOS (ICNS) - only try if supported
    try:
        img.save('src-tauri/icons/icon.icns', format='ICNS')
        print("Created icon.icns")
    except Exception as e:
        print(f"Warning: Could not create ICNS file: {e}")

    print("Icons created successfully!")

if __name__ == "__main__":
    create_icon()
