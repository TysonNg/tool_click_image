#!/usr/bin/env python3
"""
Create full backup of entire tool_click_image
Remove old backups (keep only latest 3)
"""

import os
import shutil
import time
from datetime import datetime

TOOL_ROOT = os.path.dirname(__file__)
BACKUP_DIR = os.path.join(TOOL_ROOT, "backups")
EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", "backups"}
EXCLUDE_FILES = {".pyc", ".pyo"}

def create_backup():
    """Create new full backup with timestamp"""
    
    # Ensure backup directory exists
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Create backup folder with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_name = f"backup_{timestamp}"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    
    print(f"📦 Creating full backup: {backup_name}")
    os.makedirs(backup_path, exist_ok=True)
    
    # Backup entire tool
    total_files = 0
    total_size = 0
    
    for root, dirs, files in os.walk(TOOL_ROOT):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        # Get relative path
        rel_path = os.path.relpath(root, TOOL_ROOT)
        backup_subdir = os.path.join(backup_path, rel_path) if rel_path != "." else backup_path
        
        # Create directory in backup
        os.makedirs(backup_subdir, exist_ok=True)
        
        # Copy files
        for file in files:
            # Skip excluded files
            if any(file.endswith(ext) for ext in EXCLUDE_FILES):
                continue
            
            src_file = os.path.join(root, file)
            dst_file = os.path.join(backup_subdir, file)
            
            try:
                shutil.copy2(src_file, dst_file)
                total_files += 1
                total_size += os.path.getsize(src_file)
            except Exception as e:
                print(f"⚠️ Failed to copy {file}: {e}")
    
    size_mb = total_size / (1024 * 1024)
    print(f"✅ Backed up {total_files} files ({size_mb:.2f} MB)")
    print(f"✅ Backup path: {backup_path}\n")
    
    return backup_path

def cleanup_old_backups(keep_count=3):
    """Remove old backups, keep only latest N"""
    
    if not os.path.exists(BACKUP_DIR):
        return
    
    # Get all backup folders
    backups = []
    for item in os.listdir(BACKUP_DIR):
        path = os.path.join(BACKUP_DIR, item)
        if os.path.isdir(path) and item.startswith("backup_"):
            mtime = os.path.getmtime(path)
            backups.append((path, mtime, item))
    
    # Sort by modification time (newest first)
    backups.sort(key=lambda x: x[1], reverse=True)
    
    # Remove old backups
    if len(backups) > keep_count:
        print(f"🧹 Cleaning up old backups (keeping latest {keep_count}):\n")
        for path, mtime, name in backups[keep_count:]:
            try:
                size_mb = sum(
                    os.path.getsize(os.path.join(dirpath, filename))
                    for dirpath, dirnames, filenames in os.walk(path)
                    for filename in filenames
                ) / (1024 * 1024)
                
                shutil.rmtree(path)
                print(f"❌ Deleted: {name} ({size_mb:.2f} MB)")
            except Exception as e:
                print(f"⚠️ Failed to delete {name}: {e}")
        print()

if __name__ == "__main__":
    print("=" * 60)
    print("  🔄 FULL TOOL BACKUP SYSTEM")
    print("=" * 60)
    print()
    
    # Create new backup
    backup_path = create_backup()
    
    # Cleanup old backups
    cleanup_old_backups(keep_count=3)
    
    print("=" * 60)
    print("✅ Full backup completed successfully!")
    print(f"📁 Backup folder: {BACKUP_DIR}")
    print("=" * 60)
