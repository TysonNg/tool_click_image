# 🔧 Permission Error Fix - PermissionError: [WinError 5] Access is denied

## Problem
When renaming, copying, or deleting game/stage folders, you get error:
```
PermissionError: [WinError 5] Access is denied: 'd:\...\maple' -> 'd:\...\MapleStory'
```

## Root Cause
Windows locks folders when they're in use by:
- AutoClick still running
- Game window still open
- Explorer viewing the folder
- File handles not released immediately

## Solution Implemented ✅

### 1. **Automatic Retry Logic** (3 attempts)
- All folder operations (rename, delete, copy) now retry up to 3 times
- 500ms delay between retries
- Forced garbage collection to release file handles

### 2. **Better Error Messages**
Instead of cryptic Windows error, you now see:
```
❌ Không thể đổi tên game:
Không thể đổi tên thư mục 'maple' sang 'MapleStory'. 
Có thể thư mục đang được sử dụng. 
Hãy đóng AutoClick hoặc game window và thử lại. 
Lỗi: [WinError 5] Access is denied
```

### 3. **Fallback Copy + Delete Method**
If retry fails, system tries:
1. Copy folder to temp location
2. Delete original folder
3. Rename temp to final name

## Files Changed

**scenario/library.py**
- `rename_game()` - Added retry logic with gc.collect() + time.sleep()
- `delete_game()` - Added retry logic
- `delete_stage()` - Added retry logic
- `copy_stage()` - Added retry logic
- All functions now raise user-friendly PermissionError messages

**ui/library_panel.py**
- `rename_game_action()` - Added try-except with error dialog
- `delete_game_action()` - Added try-except with error dialog
- `copy_stage_action()` - Added try-except with error dialog
- `delete_stage_action()` - Added try-except with error dialog

## What to Do If You Still Get Error

**Option 1: Close game and retry**
1. Close the game window
2. Restart AutoClick
3. Try renaming/deleting again

**Option 2: Close Explorer**
1. Close any File Explorer windows viewing scenarios folder
2. Restart AutoClick
3. Try again

**Option 3: Restart Windows**
1. Sometimes Windows locks are stubborn
2. Full restart usually fixes it

## How Retry Works

When you try to rename 'maple' → 'MapleStory':

```
Attempt 1: Try direct os.rename()
├─ Success → Done! ✅
└─ PermissionError → Wait 500ms, retry

Attempt 2: Try direct os.rename() again
├─ Success → Done! ✅
└─ PermissionError → Wait 500ms, retry

Attempt 3: Try copy + delete method
├─ Success → Done! ✅
└─ PermissionError → Show user-friendly error message ❌
```

## Technical Details

**Forces file handle release:**
```python
gc.collect()          # Force garbage collection
time.sleep(0.1)       # Brief pause for system cleanup
os.rename(old, new)   # Try operation
```

**Fallback approach:**
```python
shutil.copytree(old_path, temp_path)  # Copy to temp
shutil.rmtree(old_path)                # Delete original
os.rename(temp_path, new_path)         # Rename temp to final
```

## Error Handling Flow

```
User clicks "Đổi tên game"
  ↓
Input new name "MapleStory"
  ↓
rename_game_action() → try block
  ↓
rename_game() with retry logic (3x)
  ├─ Success → Update UI, show status ✅
  └─ Failure → Raise PermissionError with message
  ↓
except PermissionError:
  ├─ Show dialog: "❌ Không thể đổi tên game..."
  ├─ Update status bar: "❌ Lỗi đổi tên game: maple"
  └─ User can retry or close game and try again
```

## Status Messages

After attempting to rename 'maple' → 'MapleStory':

| Scenario | Status Message |
|----------|----------------|
| Success | ✅ Da doi ten game: maple -> MapleStory |
| Fails due to lock | ❌ Lỗi đổi tên game: maple |
| Game deleted | ✅ Da xoa game: MapleStory |
| Delete fails | ❌ Lỗi xóa game: MapleStory |

## Testing the Fix

1. Start AutoClick
2. Try to rename a game folder while game is open
   - Should retry automatically (you won't see it)
   - If successful, shows: `✅ Da doi ten game: ...`
3. Close game window
4. Try to delete game folder
   - Should succeed with: `✅ Da xoa game: ...`

## Version Information
- **Fixed**: June 7, 2026
- **Affects**: Game/Stage rename, delete, copy operations
- **Retry attempts**: 3
- **Retry delay**: 500ms
- **Total max wait time**: ~1.5 seconds

---

**Status**: ✅ Fixed and ready to use

If you still encounter issues after closing everything, please restart AutoClick and try again.
