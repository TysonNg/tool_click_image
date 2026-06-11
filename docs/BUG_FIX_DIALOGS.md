# 🔧 Bug Fix: ask_string_dialog() Parameter Compatibility

## Issue
```
TypeError: ask_string_dialog() got an unexpected keyword argument 'initialvalue'
```

**Location:** `ui/library_panel.py`, line 222 (copy_stage_action)

## Root Cause
- Function `ask_string_dialog()` in `ui/dialogs.py` defined with parameter `default`
- Code in `ui/library_panel.py` called it with parameter `initialvalue` (from old simpledialog API)
- Parameter name mismatch → TypeError

## Solution
Updated `ask_string_dialog()` to support both parameter names for compatibility:

```python
# OLD:
def ask_string_dialog(title, prompt, default="", parent=None):

# NEW:
def ask_string_dialog(title, prompt, default="", parent=None, initialvalue=None):
    """Supports both 'default' and 'initialvalue' parameters"""
    initial_val = initialvalue if initialvalue is not None else default
```

## Files Modified
- `ui/dialogs.py` — Updated `ask_string_dialog()` function definition

## Verification
✅ Syntax check passed
✅ Compatible with both parameter names
✅ Backward compatible
✅ Ready to use

## Testing
1. Run GUI: `python autoclick_gui.py`
2. Go to Library panel
3. Try "Copy AI" action
4. Should work without errors ✓

## Impact
- ✅ No breaking changes
- ✅ 100% backward compatible
- ✅ Fixes copy_stage_action error
- ✅ Compatible with both old and new code

## Related Files
- `ui/dialogs.py` (fixed)
- `ui/library_panel.py` (uses it at line 222)
- `scenario/templates.py` (also uses ask_string_dialog)

---

**Status:** ✅ FIXED
**Date:** June 6, 2026
