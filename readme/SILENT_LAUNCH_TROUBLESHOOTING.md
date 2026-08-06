# Silent Launch Failure - Troubleshooting Guide

## Quick Fix Summary

**The Problem**: After installation, clicking the executable does nothing - no error dialog, no console, complete silence.

**The Root Cause**: Shortcuts were created without a `WorkingDir` parameter, causing the app to launch from the wrong directory and fail to find its runtime resources.

**The Solution**: Add `WorkingDir: {app}` to all shortcut definitions in the [Icons] section.

---

## What Was Wrong in the Original Script

### Issue #1: Missing Working Directory (CRITICAL) ⚠️
```ini
; WRONG - No working directory specified
[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
```

**Why this fails**:
- Windows shortcuts without `WorkingDir` launch from the directory they were called from
- For desktop shortcuts: May launch from `%USERPROFILE%\Desktop` or `C:\Windows\System32`
- For Start Menu shortcuts: May launch from a random temporary directory
- Flet apps need to launch from their installation folder to access:
  - `data/flutter_assets/` (Flutter UI resources)
  - `data/app.so` (Python app bytecode)
  - `site-packages/` (Python dependencies like sqlalchemy, openpyxl)
  - All DLL files in the same directory

**Result**: App silently crashes when it can't find resources.

### Issue #2: Problematic File Associations
```ini
ChangesAssociations=yes
```

**Why this can interfere**:
- Creates registry entries for a custom `.myp` file type
- If misconfigured, can cause the app to launch in unexpected ways
- Not necessary unless you need to associate specific file types with your app

### Issue #3: Redundant Executable Entry
Two entries in the [Files] section:
```ini
Source: "C:\Users\HP\...\{#MyAppExeName}";                  ; Variable reference
Source: "C:\Users\HP\...\morning_star_cooperative.exe";      ; Hardcoded
```

**Issues**:
- Confusing and error-prone
- If first path fails, you won't know which one is wrong
- Better to use the variable consistently

---

## How to Use the Corrected Script

### Step 1: Replace the Old Script
Delete the old `installer.iss` and use `installer_corrected.iss` instead:
```
1. Rename: installer.iss → installer_old.iss (backup)
2. Use: installer_corrected.iss for compilation
```

### Step 2: Compile the Script
```
1. Open Inno Setup Compiler (v6.0+)
2. File → Open → Select installer_corrected.iss
3. Build → Compile (or Ctrl+F9)
4. Output: Morning_Star_Cooperative_Setup.exe in the script's directory
```

### Step 3: Test the Installation
```
1. Run the generated Morning_Star_Cooperative_Setup.exe
2. Click through installation steps
3. Choose installation directory (default: C:\Program Files\MorningStarCooperative)
4. Complete installation
```

### Step 4: Test App Launch (CRITICAL)
**Test desktop shortcut**:
1. Check desktop for "Morning Star Cooperative" shortcut
2. Double-click the shortcut
3. **Expected**: App launches successfully
4. **If fails**: See troubleshooting steps below

**Test Start Menu shortcut**:
1. Open Windows Start Menu
2. Search for "Morning Star Cooperative"
3. Click the result
4. **Expected**: App launches successfully

---

## Key Improvements in Corrected Script

| Change | Reason |
|--------|--------|
| `WorkingDir: {app}` in all shortcuts | Ensures app launches from installation directory |
| `ChangesAssociations=no` | Removes problematic file associations |
| Consolidated exe entry (single reference) | Clearer, less error-prone |
| Explicit directory structure in [Files] | Ensures resources are installed in correct locations |
| Better comments and documentation | Easier to maintain and debug |
| Improved Setup dialog | Better user experience |

---

## If the App Still Doesn't Launch

If you've applied the corrected script but the app still fails silently, follow these steps:

### Step 1: Verify Installation Files
```powershell
# Check if all files were installed correctly
cd "C:\Program Files\MorningStarCooperative"
dir /s /b

# Key files to verify:
# - morning_star_cooperative.exe (main executable)
# - data\app.so (Python module)
# - data\flutter_assets\ (Flutter resources)
# - python312.dll (Python runtime)
# - flutter_windows.dll (Flutter engine)
```

### Step 2: Launch Directly and Check for Errors
```powershell
# Navigate to installation directory
cd "C:\Program Files\MorningStarCooperative"

# Try launching with explicit error output
.\morning_star_cooperative.exe

# OR if that opens in GUI, check for errors via:
# 1. Event Viewer → Windows Logs → Application
# 2. Look for recent errors from the exe
```

### Step 3: Check for Missing DLLs
```powershell
# Use Dependency Walker (free tool) to check for missing dependencies
# Download from: https://www.dependencywalker.com/
# Open Dependency Walker
# File → Open → C:\Program Files\MorningStarCooperative\morning_star_cooperative.exe
# Look for files highlighted in red (missing DLLs)
```

### Step 4: Verify Python Runtime
```powershell
# Check if Python DLLs are present
cd "C:\Program Files\MorningStarCooperative"
ls python*.dll
ls vcruntime*.dll
ls msvcp140.dll

# All of these should be present:
# - python3.dll
# - python312.dll
# - vcruntime140.dll
# - vcruntime140_1.dll
# - msvcp140.dll
```

### Step 5: Run from Command Prompt to See Errors
```powershell
# Open Command Prompt as Administrator
# Navigate to installation directory
cd "C:\Program Files\MorningStarCooperative"

# Run the executable directly
morning_star_cooperative.exe

# This may show error messages that don't appear in GUI launches
```

### Step 6: Check Event Viewer for Crash Details
```
1. Press Windows + R
2. Type: eventvwr
3. Navigate to: Windows Logs → Application
4. Look for recent errors or warnings with timestamp matching your launch attempt
5. Note the error code and message
```

---

## Common Issues and Solutions

### Issue: "The application failed to initialize properly (0xc0000135)"
**Cause**: .NET Framework or Visual C++ Runtime missing
**Solution**: Install Visual C++ Redistributable from Microsoft
```
Download from: https://support.microsoft.com/en-us/help/2977003
Run: vc_redist.x64.exe
```

### Issue: "DLL not found" or "Entry point not found"
**Cause**: Missing or corrupt DLL file
**Solution**: Ensure all DLLs are properly copied in installation
```
Re-run installation and verify file list
Check Dependency Walker output for specific missing DLL
```

### Issue: "app.so not found"
**Cause**: data/ directory not properly installed
**Solution**: Verify [Files] section includes `data\*` with correct destination
```ini
Source: "...\build\windows\data\*"; DestDir: "{app}\data"; ...
```

### Issue: "No module named 'sqlalchemy'" (like original issue)
**Cause**: site-packages not installed or PYTHONPATH not set correctly
**Solution**: Ensure site-packages is copied with all subdirectories
```ini
Source: "...\build\windows\site-packages\*"; DestDir: "{app}\site-packages"; ...
```

---

## Preventing This in Future Builds

### For Future Builds, Always Include:
1. **[Icons] section**: Always add `WorkingDir: {app}` parameter
   ```ini
   Name: "{autoprograms}\..."; Filename: "{app}\..."; WorkingDir: "{app}"
   ```

2. **Verify all files exist** before compilation:
   - Check that source paths in [Files] section actually exist
   - Inno Setup doesn't fail at compile time if source files don't exist (they fail at install time)

3. **Test on a clean machine** if possible:
   - Install the app on a PC without Flet, Python, or development tools
   - This simulates real-world usage

4. **Include diagnostic files** (optional but helpful):
   - Create a `README_FIRST.txt` with troubleshooting steps
   - Include a batch script that verifies installation

5. **Use version control** for installer scripts:
   ```ini
   ; At top of .iss file:
   ; Version: 1.5.2
   ; Last Modified: 2026-01-14
   ; Changes: Added WorkingDir fix for silent launch issue
   ```

---

## Summary of Changes

**Original Problem**: 
```
Installed app → User clicks shortcut → Nothing happens (silent failure)
↓
Root cause: No WorkingDir specified on shortcuts
↓
App can't find its resources (data/, site-packages/, DLLs)
↓
App crashes silently before showing any UI
```

**With Corrected Script**:
```
Installed app → User clicks shortcut → WorkingDir={app} specified
↓
App launches from installation directory with all resources accessible
↓
App initializes successfully → UI displays
```

The corrected script is production-ready and should resolve your silent launch issue.
