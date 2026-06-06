#!/usr/bin/env python3
"""
Diagnose Why Click Goes to Wrong Button

Symptoms: 
  - You capture "Go to Menu" button
  - But it clicks "Quản Lý Kịch Bản" instead
  - Two buttons look completely different

Root Causes to Check:
  1. Template image file is wrong (has the other button)
  2. Click point is outside the "Go to Menu" button
  3. Template matching found the wrong button
  4. Search region excludes the right button
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import cv2
import numpy as np
from core.vision import imread_unicode

print()
print("=" * 80)
print("DIAGNOSE WRONG CLICK - Go to Menu vs Quản Lý Kịch Bản")
print("=" * 80)
print()

# Find the Go to Menu template
scenario_path = Path(r"d:\Program Files\Autoclick_ver_2\tool_click_image\scenarios")

print("Looking for template files...")
print()

# Search for "Go to Menu" or similar
go_to_menu_paths = list(scenario_path.rglob("*go*menu*"))
print(f"Found {len(go_to_menu_paths)} files with 'go' and 'menu': {go_to_menu_paths}")

# Search for capture files
capture_paths = list(scenario_path.rglob("*capture*"))
print(f"Found {len(capture_paths)} capture files")

# Search for Arena scenario
arena_paths = list(scenario_path.glob("**/Arena/*.png"))
print(f"Found {len(arena_paths)} Arena PNG files:")
for p in sorted(arena_paths):
    print(f"  - {p.name}")

print()
print("=" * 80)
print("ANALYSIS")
print("=" * 80)
print()

# Load Arena images
if arena_paths:
    arena_images = {}
    for img_path in sorted(arena_paths):
        try:
            img = imread_unicode(str(img_path))
            arena_images[img_path.name] = (img, img_path)
            print(f"Loaded: {img_path.name} ({img.shape})")
        except Exception as e:
            print(f"Failed to load {img_path.name}: {e}")
    
    print()
    print("=" * 80)
    print("CHECKLIST")
    print("=" * 80)
    print()
    
    # Check each image
    for name, (img, path) in arena_images.items():
        print(f"File: {name}")
        print(f"  Size: {img.shape}")
        print(f"  Location: {path}")
        
        # Try to detect if it's a button
        if img.size > 100:  # Not too small
            print(f"  ✅ Non-trivial size")
        else:
            print(f"  ⚠️ Very small image")
        
        # Check if it looks like a button (has repeated pixels)
        if len(np.unique(img)) < img.size * 0.5:
            print(f"  ✅ Has color/structure (not noise)")
        else:
            print(f"  ⚠️ High variation (noise?)")
        
        print()

print()
print("=" * 80)
print("DIAGNOSIS QUESTIONS - Answer These")
print("=" * 80)
print()

print("1️⃣ When you captured 'Go to Menu':")
print("   - Did you see the button clearly on screen?")
print("   - Did you crop ONLY the button area?")
print("   - Or did you crop a larger area around it?")
print()

print("2️⃣ Where is the click point?")
print("   - Center of the button?")
print("   - Top-left corner?")
print("   - Bottom-right?")
print()

print("3️⃣ Are the two buttons on screen?")
print("   - 'Go to Menu' (blue button, top area)")
print("   - 'Quản Lý Kịch Bản' (yellow text, bottom area)")
print("   - Are they next to each other?")
print("   - Are they far apart?")
print()

print("4️⃣ When you edit the image config:")
print("   - Is the search region correct?")
print("   - Does it cover the 'Go to Menu' button?")
print("   - Or could it miss it?")
print()

print()
print("=" * 80)
print("MOST LIKELY CAUSES (In Order)")
print("=" * 80)
print()

print("🔴 CAUSE 1: Template Image Is Wrong")
print("   Symptom: You see 'Go to Menu' but file has 'Quản Lý Kịch Bản'")
print("   Fix: Re-capture 'Go to Menu' carefully")
print()

print("🟡 CAUSE 2: Click Point Outside Button")
print("   Symptom: Template matches but click is off-target")
print("   Fix: Edit click point to be in center of button")
print()

print("🟠 CAUSE 3: Template Too Small/Generic")
print("   Symptom: Matches multiple buttons instead of just one")
print("   Fix: Recapture with more context/detail")
print()

print("🟢 CAUSE 4: Search Region Wrong")
print("   Symptom: Algorithm looks in wrong area")
print("   Fix: Adjust search region bounds")
print()

print()
print("=" * 80)
print("QUICK FIX STEPS")
print("=" * 80)
print()

print("Step 1: Visual Inspection")
print("  1. Open Arena scenario")
print("  2. Open this file: scenarios/Dragoncity/Arena/*.png")
print("  3. Check if it shows 'Go to Menu' or something else")
print("  4. If wrong, go to Step 2")
print()

print("Step 2: Re-capture 'Go to Menu'")
print("  1. Close AutoClick")
print("  2. Open Dragon City game")
print("  3. Get to the Arena screen")
print("  4. Click 'Add Image' in AutoClick")
print("  5. Carefully crop ONLY the 'Go to Menu' button")
print("  6. Make sure to get the whole button")
print("  7. Save as new image")
print()

print("Step 3: Fix Click Point")
print("  1. Edit the image config")
print("  2. Set click point to: CENTER (50%, 50%)")
print("  3. If button is on left, use (25%, 50%)")
print("  4. If button is on right, use (75%, 50%)")
print()

print("Step 4: Test")
print("  1. Close and open AutoClick")
print("  2. Test the scenario")
print("  3. Verify it clicks the right button")
print()

print()
print("=" * 80)
print("ADVANCED DEBUGGING")
print("=" * 80)
print()

print("Enable Debug Logging:")
print("  1. Open core/runner.py")
print("  2. Find: _resolve_click_point()")
print("  3. Add prints before click:")
print("    print(f'Matched at: ({top_left_x}, {top_left_y})')")
print("    print(f'Matched size: {matched_w}x{matched_h}')")
print("    print(f'Click point: ({click_x}, {click_y})')")
print()

print("Check Template Matching:")
print("  1. Use: test_image_matching() button in UI")
print("  2. See which image actually matched")
print("  3. See the score and location")
print()

print()
print("=" * 80)
print("TIP: Different Buttons?")
print("=" * 80)
print()

print("The two buttons look completely different:")
print("  🔵 'Go to Menu' = Blue background + white text (top)")
print("  🟡 'Quản Lý Kịch Bản' = Dark background + yellow text (bottom)")
print()

print("This means:")
print("  ✅ If template is 'Go to Menu', it should ONLY match that button")
print("  ✅ If it matches 'Quản Lý Kịch Bản' instead, template is WRONG")
print()

print("Solution:")
print("  1. Check the PNG file you captured")
print("  2. If it's not the blue button, DELETE IT")
print("  3. Re-capture the BLUE 'Go to Menu' button carefully")
print("  4. Verify before saving")
print()

print()
print("=" * 80)

print()
print("✅ Now go check your template images!")
print()
