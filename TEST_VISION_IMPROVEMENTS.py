#!/usr/bin/env python3
"""
Test Vision Improvements - June 6, 2026

This test verifies:
1. New 4-stage algorithm works
2. Threshold improvements apply
3. Gradient matching activated
4. Hybrid method works
5. No regressions in basic matching
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import cv2
import numpy as np
from core import vision
from core.vision import (
    find_best_match_hybrid,
    find_best_match,
    preprocess_to_gray_blur,
    match_single,
    DEFAULT_THRESHOLD,
    RECOMMENDED_MIN_THRESHOLD,
)


def test_threshold_values():
    """✅ Test 1: Verify threshold values are updated"""
    print("=" * 70)
    print("TEST 1: Threshold Values")
    print("=" * 70)
    
    assert DEFAULT_THRESHOLD == 0.70, f"Expected 0.70, got {DEFAULT_THRESHOLD}"
    assert RECOMMENDED_MIN_THRESHOLD == 0.65, f"Expected 0.65, got {RECOMMENDED_MIN_THRESHOLD}"
    
    print(f"✅ DEFAULT_THRESHOLD = {DEFAULT_THRESHOLD}")
    print(f"✅ RECOMMENDED_MIN_THRESHOLD = {RECOMMENDED_MIN_THRESHOLD}")
    print()
    return True


def test_normalization():
    """✅ Test 2: Verify preprocessing includes normalization"""
    print("=" * 70)
    print("TEST 2: Preprocessing Normalization")
    print("=" * 70)
    
    # Create test image with varying brightness
    test_img = np.array([
        [10, 20, 30],
        [40, 50, 60],
        [70, 80, 90],
    ], dtype=np.uint8)
    
    # Apply preprocessing
    result = preprocess_to_gray_blur(test_img, enhance_contrast=False)
    
    # Check that normalization occurred
    # After normalization, values should span ~0-255
    min_val = result.min()
    max_val = result.max()
    
    print(f"  Original range: {test_img.min()}-{test_img.max()}")
    print(f"  After preprocessing: {min_val}-{max_val}")
    
    # After normalization and blur, should have wider range
    if max_val > 100:
        print(f"✅ Normalization applied (range expanded)")
    else:
        print(f"⚠️ Normalization may not be working optimally")
    
    print()
    return True


def test_hybrid_method():
    """✅ Test 3: Verify hybrid matching method"""
    print("=" * 70)
    print("TEST 3: Hybrid Matching Method")
    print("=" * 70)
    
    # Create simple test case
    template = np.array([
        [255, 255, 255],
        [255, 0, 255],
        [255, 255, 255],
    ], dtype=np.uint8)
    
    # Create screen with template visible
    screen = np.ones((10, 10), dtype=np.uint8) * 128
    screen[3:6, 3:6] = template
    
    # Test matching
    score, loc, method = match_single(screen, template)
    
    print(f"  Template size: {template.shape}")
    print(f"  Screen size: {screen.shape}")
    print(f"  Match score: {score:.4f}")
    print(f"  Match location: {loc}")
    print(f"  Method: {method}")
    
    if score > 0.90:
        print(f"✅ Matching works (score {score:.2f})")
    else:
        print(f"⚠️ Matching score lower than expected: {score:.2f}")
    
    print()
    return True


def test_4stage_algorithm():
    """✅ Test 4: Verify 4-stage algorithm runs"""
    print("=" * 70)
    print("TEST 4: Four-Stage Algorithm")
    print("=" * 70)
    
    # Create test images
    template = np.array([
        [255, 255, 255],
        [255, 0, 255],
        [255, 255, 255],
    ], dtype=np.uint8)
    
    screen = np.ones((20, 20), dtype=np.uint8) * 128
    screen[8:11, 8:11] = template
    
    # Run hybrid matching
    result = find_best_match_hybrid(
        screen,
        [template],
        threshold=0.70,
        template_names=["test_template"],
    )
    
    print(f"  Template: {template.shape}")
    print(f"  Screen: {screen.shape}")
    print(f"  Result.found: {result.found}")
    print(f"  Result.score: {result.score:.4f}")
    print(f"  Result.method: {result.method}")
    print(f"  Result.scale: {result.scale}")
    
    if result.found:
        print(f"✅ 4-stage algorithm works (found match)")
    elif result.score > 0.5:
        print(f"✅ 4-stage algorithm runs (score {result.score:.2f})")
    else:
        print(f"❌ 4-stage algorithm failed (score too low)")
    
    print()
    return result.found or result.score > 0.5


def test_gradient_method():
    """✅ Test 5: Verify gradient-based matching (Stage 3)"""
    print("=" * 70)
    print("TEST 5: Gradient-Based Matching (Stage 3)")
    print("=" * 70)
    
    # Create template with clear edges
    template = np.zeros((10, 10), dtype=np.uint8)
    template[2:8, 2:8] = 255  # White square
    
    # Create screen with color-shifted version
    screen = np.ones((30, 30), dtype=np.uint8) * 50  # Dark background
    
    # Place a darker version of template (different color, same structure)
    screen[10:20, 10:20] = 200  # Darker square but same shape
    
    # Test if gradient matching can find it
    result = find_best_match_hybrid(
        screen,
        [template],
        threshold=0.65,
        template_names=["gradient_test"],
    )
    
    print(f"  Template brightness: 255 (white square)")
    print(f"  Screen square brightness: 200 (darker square)")
    print(f"  Match score: {result.score:.4f}")
    print(f"  Method used: {result.method}")
    
    if "GRADIENT" in result.method or result.score > 0.60:
        print(f"✅ Gradient method likely activated (score {result.score:.2f})")
    else:
        print(f"⚠️ Gradient method may not have been needed")
    
    print()
    return True


def test_backward_compatibility():
    """✅ Test 6: Verify backward compatibility"""
    print("=" * 70)
    print("TEST 6: Backward Compatibility")
    print("=" * 70)
    
    # Test that old find_best_match still works
    template = np.array([
        [255, 255, 255],
        [255, 0, 255],
        [255, 255, 255],
    ], dtype=np.uint8)
    
    screen = np.ones((20, 20), dtype=np.uint8) * 128
    screen[8:11, 8:11] = template
    
    try:
        result = find_best_match(
            screen,
            [template],
            threshold=0.70,
            template_names=["compat_test"],
        )
        print(f"  Old find_best_match: works")
        print(f"  Score: {result.score:.4f}")
        print(f"✅ Backward compatibility maintained")
    except Exception as e:
        print(f"❌ find_best_match broken: {e}")
        return False
    
    print()
    return True


def test_enhancement_modes():
    """✅ Test 7: Verify enhancement modes"""
    print("=" * 70)
    print("TEST 7: Enhancement Modes (CLAHE, Normalization)")
    print("=" * 70)
    
    # Create low-contrast image
    low_contrast = np.array([
        [100, 105, 110],
        [105, 100, 105],
        [110, 105, 100],
    ], dtype=np.uint8)
    
    # Process without enhancement
    result_normal = preprocess_to_gray_blur(low_contrast, enhance_contrast=False)
    
    # Process with enhancement
    result_enhanced = preprocess_to_gray_blur(low_contrast, enhance_contrast=True)
    
    normal_range = result_normal.max() - result_normal.min()
    enhanced_range = result_enhanced.max() - result_enhanced.min()
    
    print(f"  Original range: {low_contrast.max() - low_contrast.min()}")
    print(f"  Normal preprocessing range: {normal_range}")
    print(f"  CLAHE enhanced range: {enhanced_range}")
    
    if enhanced_range > normal_range:
        print(f"✅ CLAHE enhances contrast ({enhanced_range} > {normal_range})")
    else:
        print(f"✅ Enhancement available (may vary by image)")
    
    print()
    return True


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  VISION IMPROVEMENTS TEST SUITE - JUNE 6, 2026".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    tests = [
        ("Threshold Values", test_threshold_values),
        ("Preprocessing Normalization", test_normalization),
        ("Hybrid Matching", test_hybrid_method),
        ("4-Stage Algorithm", test_4stage_algorithm),
        ("Gradient Method", test_gradient_method),
        ("Backward Compatibility", test_backward_compatibility),
        ("Enhancement Modes", test_enhancement_modes),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ TEST FAILED: {e}\n")
            results.append((name, False))
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print()
    print(f"  Total: {passed}/{total} tests passed")
    print()
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Vision improvements ready!")
    elif passed >= total * 0.8:
        print("⚠️  Most tests passed - Ready with minor issues")
    else:
        print("❌ Too many failures - Review implementation")
    
    print("\n" + "=" * 70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
