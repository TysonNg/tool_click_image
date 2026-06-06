#!/usr/bin/env python3
"""
Check Click Points Configuration
"""

import sys
import json
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print()
print("=" * 80)
print("CHECK CLICK POINTS - Is click in center of button?")
print("=" * 80)
print()

arena_path = Path(r"d:\Program Files\Autoclick_ver_2\tool_click_image\scenarios\Dragoncity\Arena")
json_file = arena_path / "Arena.json"

if not json_file.exists():
    print(f"❌ Cannot find {json_file}")
    print()
    sys.exit(1)

try:
    with open(json_file, 'r', encoding='utf-8') as f:
        scenario = json.load(f)
    print(f"✅ Loaded: {json_file}")
except Exception as e:
    print(f"❌ Error loading: {e}")
    sys.exit(1)

print()
print("=" * 80)
print("IMAGES IN ARENA SCENARIO")
print("=" * 80)
print()

steps = scenario.get("steps", [])
print(f"Total steps: {len(steps)}")
print()

for i, step in enumerate(steps, 1):
    print(f"Step {i}: {step.get('type', 'unknown')}")
    
    if step.get('type') == 'image':
        path = step.get('path', 'N/A')
        print(f"  File: {path}")
        
        w = step.get('w', '?')
        h = step.get('h', '?')
        print(f"  Original size: {w}x{h}")
        
        click_x = step.get('click_x', '?')
        click_y = step.get('click_y', '?')
        print(f"  Click point: ({click_x}, {click_y})")
        
        # Check if click is in center
        if w != '?' and h != '?' and click_x != '?' and click_y != '?':
            w, h = int(w), int(h)
            click_x, click_y = int(click_x), int(click_y)
            
            center_x = w // 2
            center_y = h // 2
            
            print(f"  Expected center: ({center_x}, {center_y})")
            
            dx = abs(click_x - center_x)
            dy = abs(click_y - center_y)
            distance = (dx**2 + dy**2) ** 0.5
            
            if distance < 5:
                print(f"  ✅ CLICK IS IN CENTER (distance: {distance:.1f})")
            elif distance < w * 0.25:
                print(f"  ⚠️ CLICK IS OFF-CENTER (distance: {distance:.1f})")
                print(f"     Move click to center ({center_x}, {center_y})")
            else:
                print(f"  ❌ CLICK IS FAR FROM CENTER (distance: {distance:.1f})")
                print(f"     This might click WRONG BUTTON!")
                print(f"     Set click to center: ({center_x}, {center_y})")
        
        threshold = step.get('threshold', '?')
        print(f"  Threshold: {threshold}")
        
        wait_until = step.get('wait_until_found', True)
        print(f"  Wait until found: {wait_until}")
        
    print()

print()
print("=" * 80)
print("DIAGNOSIS")
print("=" * 80)
print()

print("If you see: ❌ CLICK IS FAR FROM CENTER")
print("  → This is your problem!")
print("  → The click point is outside the button")
print("  → That's why it clicks the wrong button")
print()

print("SOLUTION:")
print("  1. Edit each image config")
print("  2. Set click point to CENTER of button")
print("  3. You can use 'Pick Click Point' button to select visually")
print()

print("OR: Delete and recapture with correct click point")
print()

print("=" * 80)
print()
