================================================================================
  ⚡ POKÉCLICK PRO - WINDOW HANDLE FIX - READ ME FIRST! 📖
================================================================================

🎯 PROBLEM YOU FACED:
  "Window handle 1051690 is no longer valid, clearing..."
  "đã nhập cửa sổ đích r vẫn ko chạy được?"
  
✅ NOW FIXED! Your script will:
  ✓ Auto-validate window before starting
  ✓ Auto-restore if minimized
  ✓ Auto-protect during execution
  ✓ Warn you intelligently
  ✓ Stop safely if something goes wrong

================================================================================
  🚀 QUICK START - 5 STEPS
================================================================================

1. Open your game (MapleStory, etc.)
   → Keep window VISIBLE (don't minimize)

2. Click: "🎯 Xác Định Cửa Sổ Đích" (Set Target Window)
   → Enter game name: "MapleStory"
   → Status should show: ✅ Green

3. Add what you want: Images, Coordinates, or Keyboard keys
   → Make sure window stays visible

4. Check: Status bar is GREEN before starting
   → ✅ Should say: "Window validated and protected"

5. Click: "⚡ TUNG POKÉBALL!" to start
   → System auto-protects your window
   → Script runs safely ✅

================================================================================
  📚 FULL DOCUMENTATION
================================================================================

Choose your language:

🇻🇳 VIETNAMESE (Recommended):
  → docs/QUICK_START_FIXED.md (Start here!)
  → docs/WINDOW_HANDLE_FIX.md (Detailed guide)
  → docs/IMPROVEMENTS_SUMMARY.md (Technical)

🇬🇧 ENGLISH:
  → docs/README_WINDOW_FIX.md (Start here!)

🔍 INDEX:
  → docs/WINDOW_FIX_INDEX.md (All documentation)

================================================================================
  🧪 VERIFY SYSTEM WORKS
================================================================================

Run test to verify:
  python TEST_WINDOW_GUARD.py

Expected result:
  ✅ ALL TESTS PASSED!
  Window Guard is working correctly! 🎉

================================================================================
  🆘 COMMON ISSUES
================================================================================

❓ "Script won't run"
  → Check: Window is not minimized
  → Check: Status bar shows ✅
  → Try: Click "🎯 Set Target Window" again

❓ "Window keeps minimizing"
  → Don't Alt-Tab while script runs
  → Don't click minimize button
  → Close unnecessary apps
  → Keep window in visible area

❓ "Still getting errors"
  → Run: python TEST_WINDOW_GUARD.py
  → Check: docs/QUICK_START_FIXED.md Troubleshooting
  → Restart application

================================================================================
  ✨ WHAT'S NEW
================================================================================

NEW FILE: core/window_guard.py
  • Protects your game window
  • Auto-restores if minimized
  • Smart warning system

UPDATED: core/runner.py
  • Pre-flight checks
  • Continuous monitoring
  • Safety stops

UPDATED: core/relative_capture.py
  • Bug fixes
  • Better validation

NEW TESTS: TEST_WINDOW_GUARD.py
  • Verify system works
  • Unit tests for WindowGuard

================================================================================
  🎓 FEATURES
================================================================================

✅ PRE-FLIGHT CHECKS
  → Validates window before running
  → Warns if minimized/hidden
  → Lets you restore or select new

✅ AUTO-RESTORE
  → If minimized → auto shows
  → If hidden → auto shows
  → If lost focus → auto brings to foreground

✅ CONTINUOUS PROTECTION
  → Checks every action
  → Restores as needed
  → Monitors throughout

✅ SMART WARNINGS
  → Clear error messages
  → Helpful suggestions
  → Lets you choose action

✅ SAFETY STOPS
  → Stops safely if window lost
  → Releases resources
  → Shows clear error

================================================================================
  📋 BEST PRACTICES
================================================================================

✅ DO THIS:
  • Keep game window visible
  • Don't minimize during script
  • Don't Alt-Tab away
  • Check status bar is ✅ green
  • Re-select window if game restarts

❌ DON'T DO THIS:
  • Minimize game window
  • Alt-Tab to other apps
  • Close game window
  • Click other windows
  • Resize window during run
  • Run multiple game instances

================================================================================
  🔧 TECHNICAL DETAILS
================================================================================

WindowGuard does:
  validate_window()         - Check if handle valid
  protect_window()          - Validate + restore + foreground
  restore_window_safe()     - Auto-show if minimized/hidden
  bring_to_foreground_safe() - Bring to front
  check_and_warn()          - Check status + warn if issues

Used by:
  → find_and_click() - Before starting
  → Template loop - Every action
  → smart_start() - Pre-flight checks

================================================================================
  📞 GETTING HELP
================================================================================

1. Read docs/QUICK_START_FIXED.md (Vietnamese)
2. Read docs/README_WINDOW_FIX.md (English)
3. Run TEST_WINDOW_GUARD.py
4. Check troubleshooting in your guide
5. Review error logs in console

================================================================================
  ✅ YOU'RE READY!
================================================================================

Everything is set up. Just:

1. Open game
2. Click "🎯 Set Target Window"
3. Add actions
4. Click "⚡ Start"
5. Watch it work! ✨

Have fun automating! 🖱️✨

================================================================================
  📝 VERSION INFO
================================================================================

Version: 2.0 - WindowGuard System
Date: June 9, 2026
Status: ✅ Production Ready
Python: 3.7+
OS: Windows 10/11

================================================================================
END OF README
For full details, see: docs/WINDOW_FIX_INDEX.md
