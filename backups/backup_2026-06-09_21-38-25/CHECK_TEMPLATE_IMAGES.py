#!/usr/bin/env python3
"""
Check Which Button Each Template Is
Display images to see what they contain
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import cv2
from core.vision import imread_unicode

print()
print("=" * 80)
print("CHECK TEMPLATE IMAGES - What does each PNG contain?")
print("=" * 80)
print()

arena_path = Path(r"d:\Program Files\Autoclick_ver_2\tool_click_image\scenarios\Dragoncity\Arena")

files_to_check = [
    ("3.png", "???"),
    ("capture_1.png", "???"),
    ("capture_2.png", "???"),
]

print("Arena PNG Files Found:")
print()

for filename, description in files_to_check:
    filepath = arena_path / filename
    
    if filepath.exists():
        try:
            img = imread_unicode(str(filepath))
            h, w = img.shape[:2]
            
            # Get basic stats
            unique_colors = len(set(img.flatten()))
            min_val = img.min()
            max_val = img.max()
            mean_val = img.mean()
            
            print(f"📄 {filename}")
            print(f"   Size: {w}x{h} pixels")
            print(f"   Colors: {unique_colors} unique")
            print(f"   Brightness: min={min_val}, max={max_val}, avg={mean_val:.0f}")
            
            # Try to guess what it is
            if max_val > 150 and mean_val > 100:
                print(f"   → Likely BRIGHT button (Go to Menu?)")
            elif max_val < 100 and mean_val < 50:
                print(f"   → Likely DARK button (Quản Lý Kịch Bản?)")
            else:
                print(f"   → MEDIUM brightness")
            
            print()
        except Exception as e:
            print(f"   ❌ Error reading: {e}")
            print()
    else:
        print(f"❌ {filename} NOT FOUND")
        print()

print()
print("=" * 80)
print("WHAT YOU SHOULD DO")
print("=" * 80)
print()

print("Option 1: Check Images Visually (Best)")
print("  1. Open File Explorer")
print("  2. Go to: d:\\Program Files\\Autoclick_ver_2\\tool_click_image\\scenarios\\Dragoncity\\Arena")
print("  3. Double-click each PNG to view")
print("  4. Check which one is the BLUE 'Go to Menu' button")
print()

print("Option 2: Check in AutoClick UI")
print("  1. Open AutoClick")
print("  2. Load Arena scenario")
print("  3. Click edit on each image")
print("  4. Check which is which")
print()

print("=" * 80)
print("COMMON ISSUE")
print("=" * 80)
print()

print("If 3.png is DARK instead of BLUE:")
print("  → You captured the WRONG button!")
print("  → This is why it clicks 'Quản Lý Kịch Bản' instead of 'Go to Menu'")
print()

print("If 3.png is BRIGHT/BLUE:")
print("  → Image is correct")
print("  → Problem is CLICK POINT (not in center of button)")
print()

print("=" * 80)
print()
