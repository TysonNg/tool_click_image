#!/usr/bin/env python3
"""Verify that rollback was successful"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print()
print("=" * 70)
print("VERIFY ROLLBACK - Check if simplified algorithm is loaded")
print("=" * 70)
print()

try:
    from core import vision
    print("✅ Vision module loaded")
except ImportError as e:
    print(f"❌ Failed to load vision module: {e}")
    sys.exit(1)

# Check threshold
print()
print("Configuration:")
print(f"  DEFAULT_THRESHOLD: {vision.DEFAULT_THRESHOLD}")
print(f"  RECOMMENDED_MIN_THRESHOLD: {vision.RECOMMENDED_MIN_THRESHOLD}")

# Check key changes
print()
print("Algorithm Status:")

# Try simple match
import numpy as np

template = np.array([
    [255, 255, 255],
    [255, 0, 255],
    [255, 255, 255],
], dtype=np.uint8)

screen = np.ones((20, 20), dtype=np.uint8) * 128
screen[8:11, 8:11] = template

# Test preprocessing
print("  Testing preprocessing...", end=" ")
try:
    result = vision.preprocess_to_gray_blur(template)
    print("✅ OK")
except Exception as e:
    print(f"❌ {e}")

# Test matching
print("  Testing match_single...", end=" ")
try:
    score, loc, method = vision.match_single(screen, template)
    print(f"✅ OK (score: {score:.2f}, method: {method})")
except Exception as e:
    print(f"❌ {e}")

# Test find_best_match
print("  Testing find_best_match...", end=" ")
try:
    result = vision.find_best_match(screen, [template], threshold=0.70)
    print(f"✅ OK (found: {result.found})")
except Exception as e:
    print(f"❌ {e}")

# Test find_best_match_hybrid
print("  Testing find_best_match_hybrid...", end=" ")
try:
    result_hybrid = vision.find_best_match_hybrid(screen, [template], threshold=0.70)
    print(f"✅ OK (found: {result_hybrid.found})")
except Exception as e:
    print(f"❌ {e}")

print()
print("=" * 70)
print("Rollback Status:")
print("=" * 70)
print()

# Check if old algorithms are still being used
import inspect

# Check preprocess function
preprocess_source = inspect.getsource(vision.preprocess_to_gray_blur)
has_normalization = "cv2.normalize" in preprocess_source
if has_normalization:
    print("⚠️  Normalization still in preprocessing (might cause issues)")
else:
    print("✅ Normalization removed")

# Check match_single function
match_source = inspect.getsource(vision.match_single)
has_hybrid = "TM_SQDIFF" in match_source or "combined_score" in match_source
if has_hybrid:
    print("⚠️  Hybrid method still in match_single")
else:
    print("✅ Hybrid method removed")

# Check find_best_match_hybrid
hybrid_source = inspect.getsource(vision.find_best_match_hybrid)
has_gradient = "gradient" in hybrid_source.lower() and "Sobel" in hybrid_source
has_clahe_stage4 = hybrid_source.count("STAGE 4") > 0 or hybrid_source.count("enhanced_screen") > 0
if has_gradient:
    print("⚠️  Gradient matching still in algorithm")
else:
    print("✅ Gradient matching removed")

if has_clahe_stage4:
    print("⚠️  CLAHE enhancement still in algorithm")
else:
    print("✅ CLAHE enhancement removed")

print()
print("=" * 70)
print("✅ ROLLBACK VERIFICATION COMPLETE")
print("=" * 70)
print()
print("Next: Restart AutoClick and test scenarios")
print()
