# 📦 Synergy.OS - Dota 2 Draft Analyzer

**Intelligent draft recommendation system for Dota 2** | Built with Rust + Tauri + React

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows-0078d4)

## 🚀 Quick Start (for Users)

### Download & Install

**Option 1: MSI Installer (Recommended)**
1. Download the latest `Synergy.OS_X.X.X_x64.msi` from [Releases](https://github.com/ezruiner/dota2draft/releases)
2. Run the installer
3. Follow the setup wizard
4. Done! Launch from Start Menu

**Option 2: Portable EXE**
1. Download `Synergy.OS_X.X.X_x64.exe`
2. Run directly (no installation required)

### Requirements
- Windows 7 or later (64-bit)
- ~100 MB disk space
- Internet connection (for first-time data loading)

## 📖 Usage

1. **Select Heroes**
   - Drag heroes to RADIANT (green) or DIRE (red) slots
   - Supports searching and filtering by attribute

2. **Analyze Draft**
   - Click "ANALYZE DRAFT" button
   - Get recommendations for best counters & synergies

3. **View Recommendations**
   - Left column: RADIANT recommendations
   - Right column: DIRE recommendations
   - Each hero shows score and reasons

## 🎮 Features

- ✅ **130+ Dota 2 Heroes** - All heroes with complete stats
- ✅ **Smart Analysis** - Considers counters, synergies, and positions
- ✅ **Fast & Responsive** - Native Rust backend
- ✅ **Dark Theme UI** - Professional gaming interface
- ✅ **Offline Ready** - Works without internet after first load
- ✅ **Auto-Update** - Keeps hero data fresh from Stratz API

## 💻 For Developers

### Requirements
- Rust 1.70+ ([install](https://rustup.rs/))
- Node.js 18+ (for frontend)
- Git

### Setup

```bash
# Clone repository
git clone https://github.com/ezruiner/dota2draft.git
cd dota2draft

# Install dependencies
npm install

# Run in development mode
cargo tauri dev

# The app will open with hot-reload enabled
```

### Build Release

#### Option 1: Using Python Script (Recommended)
```bash
python build-release.py 0.2.0
# Follow prompts to create GitHub Release
```

#### Option 2: Using Batch Script (Windows)
```powershell
build-release.bat 0.2.0
```

#### Option 3: Manual
```bash
cargo tauri build
# Artifacts will be in: src-tauri/target/release/bundle/msi/
```

### Project Structure

```
dota2draft/
├── src-tauri/              # Rust backend (Tauri)
│   ├── src/main.rs         # Tauri commands
│   ├── src/drafter.rs      # Analysis logic
│   └── src/scoring.rs      # Hero scoring
├── ui/                     # Frontend
│   └── index.html          # Main interface
├── data/                   # Hero data
│   └── heroes/             # 130+ JSON files
├── scripts/                # Python utilities
└── rules/                  # Documentation
```

### Key Commands

```bash
# Development
cargo tauri dev              # Run with hot-reload

# Building
cargo check                  # Check for errors
cargo tauri build            # Build production binary
cargo test                   # Run tests

# Cleanup
cargo clean                  # Remove build artifacts
```

### Creating a Release

1. **Update version in:**
   - `Cargo.toml`
   - `src-tauri/Cargo.toml`
   - `src-tauri/tauri.conf.json`
   - `package.json`

2. **Build and push:**
   ```bash
   python build-release.py 0.2.0
   ```

3. **GitHub Actions automatically:**
   - Builds Windows MSI/EXE
   - Creates Release
   - Uploads artifacts

4. **Users can download** from [Releases](https://github.com/ezruiner/dota2draft/releases)

## 🔧 Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Rust + Tauri |
| **Frontend** | HTML/CSS/JavaScript |
| **Data** | JSON (Dota 2 Stratz API) |
| **Build** | Cargo + Tauri CLI |
| **CI/CD** | GitHub Actions |

## 📚 Documentation

- [Tauri Setup Guide](./rules/TAURI_SETUP.md) - Dev server & architecture
- [Project Structure](./rules/PROJECT_SETUP.md) - Code organization
- [Quick Start](./rules/README_QUICK_START.md) - 2-minute guide
- [Release Guide](./RELEASE_GUIDE.md) - How to create releases
- [Hero Data Guide](./HERO_DATA_GUIDE.md) - Data format explanation

## 🐛 Troubleshooting

### "Tauri API not found"
- Clear browser cache: `Ctrl+Shift+Delete`
- Restart app with `Ctrl+R`

### Build fails
```bash
cargo clean
cargo tauri build
```

### Data not loading
- Check `data/` folder exists
- Ensure `data/heroes/*.json` files are present
- Try "Update Heroes Data" button in Settings

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push branch: `git push origin feature/amazing`
5. Open Pull Request

## 📋 Roadmap

- [ ] macOS support
- [ ] Linux support
- [ ] Web version
- [ ] Mobile app
- [ ] Match recommendations
- [ ] Team composition analyzer
- [ ] In-game integration

## 📜 License

MIT License - see [LICENSE](LICENSE) file

## 🔗 Links

- **GitHub**: https://github.com/ezruiner/dota2draft
- **Releases**: https://github.com/ezruiner/dota2draft/releases
- **Issues**: https://github.com/ezruiner/dota2draft/issues
- **Tauri**: https://tauri.app/
- **Dota 2 API**: https://stratz.com/

## 📞 Support

- Check [FAQ](./RELEASE_GUIDE.md)
- Create an [Issue](https://github.com/ezruiner/dota2draft/issues)
- Check [Discussions](https://github.com/ezruiner/dota2draft/discussions)

---

**Made with ❤️ for Dota 2 players**

Have fun analyzing drafts! 🎮
