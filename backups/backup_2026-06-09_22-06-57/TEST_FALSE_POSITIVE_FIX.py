"""
TEST: False Positive Fix in Hybrid Mode

This test verifies that the hybrid matching doesn't accept poor matches
(i.e., it now correctly rejects images with score < threshold).

Previously, the code was accepting matches at (threshold - 0.15), which
caused false positives where completely different images would be matched.

Example: threshold=0.7, but score=0.55 images would still match (wrong!)
"""

import cv2
import numpy as np
from core.vision import find_best_match_hybrid

def test_false_positive_scenario():
    """
    Test case: Match a template against a COMPLETELY DIFFERENT image
    
    Expected: Should NOT match (score should be very low)
    Previously: Would incorrectly match due to (threshold - 0.15) issue
    """
    
    print("\n" + "="*70)
    print("TEST: False Positive Detection")
    print("="*70)
    
    # Create a test template (e.g., a blue button)
    blue_button = np.zeros((100, 150, 3), dtype=np.uint8)
    blue_button[:, :] = [0, 0, 255]  # Blue color
    cv2.rectangle(blue_button, (20, 20), (130, 80), (255, 255, 255), -1)  # White button
    cv2.putText(blue_button, "GO", (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
    
    blue_button_gray = cv2.cvtColor(blue_button, cv2.COLOR_BGR2GRAY)
    
    # Create a completely different image (e.g., dark background)
    dark_background = np.zeros((1080, 1920, 3), dtype=np.uint8)
    dark_background[:, :] = [50, 50, 50]  # Dark gray background
    # Add some random noise to make it realistic
    noise = np.random.randint(0, 20, dark_background.shape, dtype=np.uint8)
    dark_background = cv2.add(dark_background, noise)
    
    dark_background_gray = cv2.cvtColor(dark_background, cv2.COLOR_BGR2GRAY)
    
    print("\n📊 TEST SCENARIO:")
    print(f"  Template (blue button): {blue_button_gray.shape}")
    print(f"  Screen (dark background): {dark_background_gray.shape}")
    print(f"  Threshold: 0.70 (or 0.75)")
    print(f"  Expected: NO MATCH (score should be ~0.3-0.5)")
    print(f"  Bug symptom: Would match anyway (false positive)")
    
    # Test with threshold 0.70
    print("\n🧪 Test 1: threshold=0.70")
    result_70 = find_best_match_hybrid(
        dark_background_gray,
        [blue_button_gray],
        threshold=0.70,
        template_names=["blue_button"],
    )
    
    print(f"  ✓ Result:")
    print(f"    - Found: {result_70.found}")
    print(f"    - Score: {result_70.score:.4f}")
    print(f"    - Threshold: 0.70")
    print(f"    - Method: {result_70.method}")
    
    if not result_70.found:
        print(f"    ✅ CORRECT: Rejected poor match (score {result_70.score:.4f} < 0.70)")
    else:
        print(f"    ❌ FALSE POSITIVE: Accepted poor match (score {result_70.score:.4f} >= 0.70)")
    
    # Test with threshold 0.75
    print("\n🧪 Test 2: threshold=0.75")
    result_75 = find_best_match_hybrid(
        dark_background_gray,
        [blue_button_gray],
        threshold=0.75,
        template_names=["blue_button"],
    )
    
    print(f"  ✓ Result:")
    print(f"    - Found: {result_75.found}")
    print(f"    - Score: {result_75.score:.4f}")
    print(f"    - Threshold: 0.75")
    print(f"    - Method: {result_75.method}")
    
    if not result_75.found:
        print(f"    ✅ CORRECT: Rejected poor match (score {result_75.score:.4f} < 0.75)")
    else:
        print(f"    ❌ FALSE POSITIVE: Accepted poor match (score {result_75.score:.4f} >= 0.75)")
    
    # Test with threshold 0.60 (should accept if score is around 0.65+)
    print("\n🧪 Test 3: threshold=0.60 (permissive)")
    result_60 = find_best_match_hybrid(
        dark_background_gray,
        [blue_button_gray],
        threshold=0.60,
        template_names=["blue_button"],
    )
    
    print(f"  ✓ Result:")
    print(f"    - Found: {result_60.found}")
    print(f"    - Score: {result_60.score:.4f}")
    print(f"    - Threshold: 0.60")
    print(f"    - Method: {result_60.method}")
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    tests_passed = 0
    if not result_70.found:
        print("✅ Test 1 (threshold=0.70): PASSED")
        tests_passed += 1
    else:
        print("❌ Test 1 (threshold=0.70): FAILED")
    
    if not result_75.found:
        print("✅ Test 2 (threshold=0.75): PASSED")
        tests_passed += 1
    else:
        print("❌ Test 2 (threshold=0.75): FAILED")
    
    print(f"\n📊 Results: {tests_passed}/2 critical tests passed")
    
    if tests_passed == 2:
        print("\n🎉 FALSE POSITIVE FIX VERIFIED!")
        print("   The hybrid mode now correctly rejects poor matches.")
    else:
        print("\n⚠️  ISSUE REMAINS: False positives are still occurring.")
        print("   Please review the matching logic.")
    
    return tests_passed == 2


if __name__ == "__main__":
    success = test_false_positive_scenario()
    exit(0 if success else 1)
