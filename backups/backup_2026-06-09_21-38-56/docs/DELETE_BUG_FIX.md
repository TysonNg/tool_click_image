# Delete Not Persisting Bug - Fixed

## Problem
When user deleted a template from editor and saved:
- Editor showed "Saved 7 templates" ✓
- File on disk said "7 templates" in verification ✓
- But when reloading, it showed 8 templates again ❌

**Root Cause**: File was not being properly flushed to disk before reload. Windows file caching meant old data was being read from cache.

## Investigation
Discovered there were 3 JSON files in the stage directory:
- `High_Fighter_Dragon.json` (8 templates - old file)
- `High_Risen_Star_Dragon.json` (should be 7, but showed 8 - not flushed)
- `Positive_Dragon.json` (7 templates)

The `get_stage_json()` function was correctly returning the right file, but the file hadn't actually been written to disk yet.

## Solution Implemented

In `scenario/io.py`, modified `save_scenario_to_stage()` with:

### 1. Delete Old File First
```python
if os.path.exists(json_path):
    gc.collect()
    time.sleep(0.1)  # Release file handles
    os.remove(json_path)
```
This ensures Windows closes all file handles before we write new data.

### 2. Explicit Flush and Sync
```python
with open(json_path, "w", encoding="utf-8") as file_obj:
    json.dump(payload, file_obj, ensure_ascii=False, indent=2)
    file_obj.flush()
    os.fsync(file_obj.fileno())  # Force sync to disk
```
Forces the OS to write data to physical disk immediately, not cache.

### 3. Garbage Collection Before Verify
```python
gc.collect()
time.sleep(0.2)
# Then verify by reading back
```
Ensures old file handles are completely released before verification read.

## Enhanced Debug Output
Added detailed logging to track:
- When file is deleted
- When flush/fsync is called
- File size verification
- Payload count vs disk count comparison
- Warnings if counts don't match

## Testing
Created `TEST_SAVE_LOAD.py` which verified:
1. Load 8 templates from disk ✓
2. Delete 1 template in memory (7 remain) ✓
3. Save to disk ✓
4. Verify file on disk has 7 templates ✓
5. Reload from disk and get 7 templates ✓
6. All three counts match ✓

## Why This Works
- **Windows File Locking**: Deleting old file before writing prevents access conflicts
- **Disk Sync**: `fsync()` bypasses OS cache and writes directly to physical disk
- **Garbage Collection**: Ensures file handles are truly released
- **Verification**: Reading back immediately confirms write succeeded

## Impact
- Fixes: Delete + Save + Reload cycle now works correctly
- No breaking changes: Same API, just more robust file I/O
- Benefit: More reliable file operations across all save scenarios

## Files Modified
- `scenario/io.py` - Enhanced `save_scenario_to_stage()` function
- `scenario/library.py` - Added debug logging to `get_stage_json()`

## Status
✅ **FIXED** - Tested and verified working
