# 📋 DEPLOYMENT & BUILD GUIDE

## 🔨 Сборка приложения

### Локальная разработка

```powershell
# Запуск с горячей перезагрузкой
cargo tauri dev
./run.ps1 -Command dev
```

### Релиз сборка

```powershell
# Собрать для текущей платформы
cargo tauri build
./run.ps1 -Command build

# Результат будет в:
# src-tauri/target/release/bundle/
```

## 📦 Выходные файлы

После `cargo tauri build` вы получите:

### Windows
```
src-tauri/target/release/bundle/
├── msi/                    # NSIS Installer
│   └── Dota_2_Helper_0.1.0_x64_en-US.msi
├── nsis/                   # NSIS Setup
│   └── Dota_2_Helper_0.1.0_x64-setup.exe
└── exe/                    # Portable EXE
    └── Dota 2 Helper.exe
```

### macOS
```
src-tauri/target/release/bundle/
├── dmg/                    # Disk Image
│   └── Dota_2_Helper_0.1.0_x64.dmg
└── macos/                  # App Bundle
    └── Dota 2 Helper.app/
```

### Linux
```
src-tauri/target/release/bundle/
├── deb/                    # Debian Package
│   └── dota2-helper_0.1.0_amd64.deb
└── AppImage/               # AppImage
    └── dota2-helper_0.1.0_amd64.AppImage
```

## ⚙️ Конфигурация сборки

Все настройки в `tauri.conf.json`:

```json
{
  "build": {
    "beforeBuildCommand": "",      // Команда перед сборкой
    "beforeDevCommand": "",         // Команда перед разработкой
    "devPath": "../ui",             // Путь к UI в разработке
    "frontendDist": "../ui",        // Путь к собранному UI
    "withGlobalTauri": true         // Глобальный Tauri объект
  },
  "package": {
    "productName": "Dota 2 Helper", // Название приложения
    "version": "0.1.0"              // Версия
  },
  "tauri": {
    "windows": [
      {
        "title": "Dota 2 Helper",    // Заголовок окна
        "width": 1200,               // Ширина
        "height": 900,               // Высота
        "resizable": true,           // Можно ли менять размер
        "fullscreen": false          // Полный экран
      }
    ]
  }
}
```

## 🔐 Подпись приложений

### Windows

```powershell
# Генерировать сертификат самоподписи
certutil -genkey -exponent 65537 -notSeparable .\key.priv 2048
pvk2pfx -pvk .\key.priv -spc .\cert.cer -pfx .\cert.pfx -po password

# Использовать в Cargo.toml
[target.x86_64-pc-windows-msvc]
rustflags = ["-C", "embed-bitcode=yes"]
```

### macOS

```bash
# Использовать Developer ID для подписи
codesign -s "Developer ID Application: Name" app.app

# Нотарайзация для Big Sur+
xcrun notarytool submit app.dmg --apple-id email --password --team-id TEAMID
```

## 📊 Оптимизация сборки

### Уменьшить размер бинарника

```toml
# Cargo.toml
[profile.release]
opt-level = 3
lto = true
codegen-units = 1
strip = true
```

### Компрессия на Windows

```powershell
# UPX компрессия (опционально)
upx --best --lzma dota2_helper.exe
```

## 🔄 CI/CD интеграция

### GitHub Actions пример

```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
      - run: cargo tauri build
      - uses: softprops/action-gh-release@v1
        with:
          files: src-tauri/target/release/bundle/**/*

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
      - run: cargo tauri build
      - uses: softprops/action-gh-release@v1
        with:
          files: src-tauri/target/release/bundle/**/*

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
      - run: sudo apt-get install libwebkit2gtk-4.0-dev
      - run: cargo tauri build
      - uses: softprops/action-gh-release@v1
        with:
          files: src-tauri/target/release/bundle/**/*
```

## 🐛 Отладка сборки

```powershell
# Подробный вывод сборки
cargo tauri build -vv
cargo build -vv

# Посмотреть все шаги сборки
cargo build --verbose

# Очистить и пересобрать
cargo clean
cargo tauri build
```

## 📝 Обновление версии

### Обновить версию для релиза

```toml
# Cargo.toml
[package]
version = "0.2.0"

# tauri.conf.json
"package": {
  "version": "0.2.0"
}
```

```powershell
# Git тег
git tag v0.2.0
git push origin v0.2.0
```

## 🚀 Распределение

### Установка локально

```powershell
# Windows
msiexec /i "Dota_2_Helper_0.1.0_x64_en-US.msi"

# или запустить EXE напрямую
.\Dota\ 2\ Helper.exe
```

### Размещение на сервере

1. Загрузить в relеаз GitHub
2. Разместить на своем сервере
3. Использовать Tauri Updater для обновлений

## 📦 Упаковка для распределения

```powershell
# Zip архив всех бинариков
Compress-Archive -Path "src-tauri/target/release/bundle/*" -DestinationPath "release-v0.1.0.zip"

# Или для отдельных платформ
Compress-Archive -Path "src-tauri/target/release/bundle/exe/*" -DestinationPath "Dota2Helper-Windows.zip"
```

## ✅ Checklist перед релизом

- [ ] Обновить версию в Cargo.toml и tauri.conf.json
- [ ] Обновить README с новыми функциями
- [ ] Запустить `cargo test` для проверки
- [ ] Локально протестировать `cargo tauri dev`
- [ ] Сделать `cargo clean && cargo tauri build`
- [ ] Проверить что все файлы в bundle/ есть
- [ ] Создать Git tag
- [ ] Загрузить в relеаз
- [ ] Обновить документацию

## 🔗 Полезные ссылки

- [Tauri Build Guide](https://tauri.app/v1/guides/building/)
- [Cargo Release Profile](https://doc.rust-lang.org/cargo/reference/profiles.html)
- [Tauri Updater](https://tauri.app/v1/guides/distribution/updater/)

## 📞 Поддержка

Если возникают проблемы с сборкой:

```powershell
# Очистить всё
cargo clean

# Переустановить Tauri
cargo install tauri-cli@latest

# Пересобрать
cargo tauri build -vv
```
