# 📖 READ ME FIRST - Window Handle Fix

## 🎯 You Had This Problem:

```
Window handle 1051690 is no longer valid, clearing...
🖱️ Double-clicked coordinate (512,451)
đã nhập cửa sổ đích r vẫn ko chạy được?

(Translation: "I selected target window but still can't run?")
```

## ✅ IT'S FIXED NOW!

A new **WindowGuard** system automatically protects your game window:

- ✅ **Before running:** Validates window is ready
- ✅ **During running:** Keeps window safe & focused
- ✅ **If minimized:** Auto-restores
- ✅ **If hidden:** Auto-shows
- ✅ **If lost:** Stops safely with clear message

---

## 🚀 5-Step Quick Start

```
1. 🎮 Open game → Keep window VISIBLE
2. 🎯 Click "🎯 Xác Định Cửa Sổ Đích" → Enter game name
3. ➕ Add images/coordinates/keys
4. ✅ Check: Status bar shows ✅ green
5. ⚡ Click "⚡ TUNG POKÉBALL!" → Done!

System auto-protects your window during execution ✅
```

---

## 📚 Documentation (Choose Your Language)

### 🇻🇳 **Vietnamese** (Recommended):

1. **[QUICK_START_FIXED.md](QUICK_START_FIXED.md)** ⭐ START HERE
   - Easy-to-follow 5-step guide
   - Real-world examples
   - Troubleshooting tips
   - ~15 minutes to read

2. **[WINDOW_HANDLE_FIX.md](WINDOW_HANDLE_FIX.md)** - Full Details
   - Root cause analysis
   - Complete troubleshooting
   - Best practices
   - Advanced topics

3. **[IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md)** - Technical
   - What was changed
   - Files modified/created
   - Before/after comparison
   - For developers

### 🇬🇧 **English**:

1. **[README_WINDOW_FIX.md](README_WINDOW_FIX.md)** ⭐ START HERE
   - Problem & solution
   - Quick start guide
   - All features explained
   - Troubleshooting

### 🔍 **Navigation**:

- **[WINDOW_FIX_INDEX.md](WINDOW_FIX_INDEX.md)** - Complete index of all docs

---

## ✨ What's New

### New Protection System:
- `core/window_guard.py` - Automatically protects your game window
- Validates before running
- Restores if minimized
- Monitors during execution
- Warns intelligently

### Updated:
- `core/runner.py` - Pre-flight checks + continuous monitoring
- `core/relative_capture.py` - Bug fixes

### New Tests:
- `TEST_WINDOW_GUARD.py` - Verify everything works

---

## 🔍 Quick Navigation

**I want to...**

- **Get started NOW** → [QUICK_START_FIXED.md](QUICK_START_FIXED.md)
- **Understand the issue** → [WINDOW_HANDLE_FIX.md](WINDOW_HANDLE_FIX.md)
- **See technical details** → [IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md)
- **Read in English** → [README_WINDOW_FIX.md](README_WINDOW_FIX.md)
- **Find specific help** → [WINDOW_FIX_INDEX.md](WINDOW_FIX_INDEX.md)

---

## 🆘 Common Issues (Quick Answers)

### "Script won't run"
- ✅ Solution: Keep window VISIBLE (don't minimize)
- ✅ Check: Status bar shows ✅ green
- ✅ Try: Click "🎯 Set Target Window" again
- 📖 Full help: See QUICK_START_FIXED.md → Troubleshooting

### "Window keeps minimizing"
- ✅ Solution: Don't minimize during script
- ✅ Don't Alt-Tab while running
- ✅ Close unnecessary apps
- 📖 Full help: See WINDOW_HANDLE_FIX.md → Best Practices

### "Still getting errors"
- ✅ Run: `python TEST_WINDOW_GUARD.py`
- ✅ Check console for error messages
- 📖 Full help: See your language's guide → Troubleshooting

---

## 🧪 Verify It Works

```bash
python TEST_WINDOW_GUARD.py
```

**You should see:**
```
✅ ALL TESTS PASSED!
Window Guard is working correctly! 🎉
```

---

## 🎯 Next Step

Choose your language and **start reading:**

- 🇻🇳 Vietnamese: [QUICK_START_FIXED.md](QUICK_START_FIXED.md)
- 🇬🇧 English: [README_WINDOW_FIX.md](README_WINDOW_FIX.md)
- 🔧 Technical: [IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md)

---

## ✅ Summary

| Before | After |
|--------|-------|
| ❌ Window handle crashes | ✅ Auto-protected |
| ❌ No restore | ✅ Auto-restore from minimize |
| ❌ Minimal warnings | ✅ Smart warnings |
| ❌ Simple validation | ✅ Continuous monitoring |
| ❌ Hard to debug | ✅ Detailed logs |

---

**You're all set! Pick a guide and start clicking! 🚀**

---

**Questions?** Check the troubleshooting section in your chosen guide.

**Want details?** See [WINDOW_FIX_INDEX.md](WINDOW_FIX_INDEX.md) for complete documentation map.

**Happy automating!** 🖱️✨
