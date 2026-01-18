# 🚀 Release Process Guide

## For Users: How to Install

### Windows

1. **Download Installer**
   - Go to [GitHub Releases](https://github.com/ezruiner/dota2draft/releases)
   - Download latest `.msi` or `.exe` file

2. **Install**
   - Double-click the `.msi` file
   - Follow installer wizard
   - Grant administrator permissions when prompted

3. **Launch**
   - Find "Synergy.OS" in Start Menu
   - Or open the installed folder and run `.exe`

4. **First Run**
   - App will load all hero data (~10-20 seconds)
   - Data is cached locally
   - Subsequent launches are instant

### What's Included

✅ All 130+ Dota 2 heroes  
✅ Complete synergy database  
✅ Role classifications  
✅ Dark UI theme  
✅ All dependencies bundled  

**No additional software needed!**

---

## For Developers: How to Create Releases

### Step 1: Prepare Changes

```bash
# Make your changes
git add .
git commit -m "Add feature description"

# Make sure everything is pushed
git push origin main
```

### Step 2: Update Version

Version should follow [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`

Examples:
- `0.1.0` - Initial release
- `0.2.0` - New feature
- `0.2.1` - Bug fix

### Step 3: Build Release

#### Option A: Python Script (Recommended)

```bash
python scripts/build-release.py 0.2.0
```

The script will:
1. ✓ Update version in all files
2. ✓ Build the application
3. ✓ Create git tag
4. ✓ Push to GitHub
5. ✓ GitHub Actions creates Release automatically

#### Option B: Batch Script (Windows)

```powershell
scripts\build-release.bat 0.2.0
```

Then manually push:
```bash
git push origin v0.2.0
```

#### Option C: Manual Process

```bash
# 1. Update version in files
# src-tauri/tauri.conf.json -> version: "0.2.0"
# Cargo.toml (both root and src-tauri/)
# package.json

# 2. Build
cargo tauri build

# 3. Create tag and push
git add .
git commit -m "Release v0.2.0"
git tag v0.2.0
git push origin v0.2.0

# GitHub Actions will automatically create the Release
```

### Step 4: Verify Release

1. Go to [GitHub Releases](https://github.com/ezruiner/dota2draft/releases)
2. Check that new release appears
3. Verify `.msi` and `.exe` files are uploaded
4. Download and test one file locally

### Build Artifacts

After `cargo tauri build`, you'll find:

```
src-tauri/target/release/bundle/
├── msi/
│   ├── Synergy.OS_0.2.0_x64.exe           # Portable executable
│   ├── Synergy.OS_0.2.0_x64.exe.zip       # Zipped executable
│   ├── Synergy.OS_0.2.0_x64.msi           # Installer (recommended)
│   └── Synergy.OS_0.2.0_x64.msi.zip       # Zipped installer
```

**MSI is recommended** because it:
- ✓ Handles Windows registry properly
- ✓ Adds to Start Menu
- ✓ Supports uninstall
- ✓ Updates automatically detected

---

## GitHub Actions Workflow

When you push a tag like `v0.2.0`, GitHub Actions automatically:

1. **Checks out code** from the tag
2. **Installs Rust** and Node.js
3. **Builds** for Windows
4. **Creates Release** with tag name
5. **Uploads artifacts** (MSI + EXE)

You can monitor in: https://github.com/ezruiner/dota2draft/actions

---

## Version File Locations

Must update in **all** these files for consistent versioning:

1. **Cargo.toml** (root)
   ```toml
   [package]
   version = "0.2.0"
   ```

2. **src-tauri/Cargo.toml**
   ```toml
   [package]
   version = "0.2.0"
   ```

3. **src-tauri/tauri.conf.json**
   ```json
   {
     "version": "0.2.0"
   }
   ```

4. **package.json**
   ```json
   {
     "version": "0.2.0"
   }
   ```

The build scripts do this automatically.

---

## Troubleshooting

### Build fails with "Tauri not found"
```bash
cargo install tauri-cli
npm install
```

### "git tag already exists"
```bash
git tag -d v0.2.0        # Delete local tag
git push origin :v0.2.0  # Delete remote tag
# Then try again
```

### Build takes too long
First build takes 5-10 minutes. Subsequent builds are faster due to caching.

### GitHub Actions hasn't started
Wait 1-2 minutes after pushing tag, check:
https://github.com/ezruiner/dota2draft/actions

---

## Release Notes Template

When creating a release manually on GitHub, use:

```markdown
## Release v0.2.0

### ✨ New Features
- Feature 1 description
- Feature 2 description

### 🐛 Bug Fixes
- Bug 1 fixed
- Bug 2 fixed

### 📦 Changes
- Data updated for patch X.X
- Performance improvements

### 📥 Installation

Download `Synergy.OS_0.2.0_x64.msi` and run installer.

No additional dependencies needed!

### 🔗 Links
- [GitHub](https://github.com/ezruiner/dota2draft)
- [Report Issues](https://github.com/ezruiner/dota2draft/issues)
```

---

## Deployment Checklist

Before releasing:

- [ ] All tests pass: `cargo test`
- [ ] Code compiles: `cargo check`
- [ ] No warnings: `cargo build`
- [ ] UI works locally: `cargo tauri dev`
- [ ] Data loads correctly
- [ ] Version updated in all 4 files
- [ ] Git commits are clear
- [ ] CHANGELOG.md updated (optional)

---

## Auto-Update Setup (Optional)

For future versions, you can add auto-updater:

```bash
cargo add tauri-plugin-updater
```

This enables automatic updates from GitHub releases.

---

## FAQ

**Q: How often should I release?**
A: When you have meaningful changes (features, fixes, or fresh data).

**Q: Can I have pre-releases?**
A: Yes, check "This is a pre-release" when creating Release.

**Q: How do users update?**
A: Download new version and run installer (old version is replaced).

**Q: Can I publish to other platforms?**
A: Yes, update GitHub Actions workflow matrix to include `macos-latest` and `ubuntu-latest`.

---

## Next Steps

1. ✅ Run `python scripts/build-release.py 0.2.0`
2. ✅ Check https://github.com/ezruiner/dota2draft/releases
3. ✅ Download and test the MSI installer
4. ✅ Share the link with users!

---

**That's it! Your app is now distributed!** 🎉
