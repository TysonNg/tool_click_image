#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test imports"""

try:
    print("Testing imports...")
    
    print("1. Importing core.vision...")
    from core import vision
    print("   ✅ core.vision OK")
    
    print("2. Importing core.runner...")
    from core import runner
    print("   ✅ core.runner OK")
    
    print("3. Importing core.state...")
    from core import state
    print("   ✅ core.state OK")
    
    print("\n✅ ALL IMPORTS SUCCESSFUL!")
    print(f"DEFAULT_THRESHOLD = {vision.DEFAULT_THRESHOLD}")
    print(f"RECOMMENDED_MIN_THRESHOLD = {vision.RECOMMENDED_MIN_THRESHOLD}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
