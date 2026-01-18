# Build & Release Helper

Скрипты для сборки и публикации релизов.

## Локальная сборка

### Windows (PowerShell)

```powershell
# 1. Убедитесь что вы в корне проекта
cd D:\ITspace\dota2draft

# 2. Обновите версию в Cargo.toml и src-tauri/tauri.conf.json
# Например: version = "0.2.0"

# 3. Создайте git tag
git tag v0.2.0
git push origin v0.2.0

# 4. Соберите финальный exe
cargo tauri build

# Результат будет в:
# src-tauri/target/release/bundle/msi/Synergy.OS_0.2.0_x64.msi
# src-tauri/target/release/bundle/msi/Synergy.OS_0.2.0_x64.exe.zip
```

## GitHub Actions (автоматическая сборка)

При push тага `vX.X.X` автоматически:
1. Собирается приложение для Windows
2. Создается GitHub Release
3. Загружаются MSI и EXE файлы

### Как использовать:

```bash
git tag v0.2.0
git push origin v0.2.0
```

Релиз автоматически создастся в GitHub: https://github.com/ezruiner/dota2draft/releases

## Версионирование

1. **Обновите версию везде:**
   - `Cargo.toml` (root)
   - `src-tauri/Cargo.toml`
   - `src-tauri/tauri.conf.json`
   - `package.json`

2. **Создайте tag и push:**
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

3. **GitHub Actions создаст Release с установщиком**

## Структура артефактов

После сборки `cargo tauri build` появятся:

```
src-tauri/target/release/bundle/
├── msi/
│   ├── Synergy.OS_0.2.0_x64.exe
│   ├── Synergy.OS_0.2.0_x64.exe.zip
│   ├── Synergy.OS_0.2.0_x64.msi
│   └── Synergy.OS_0.2.0_x64.msi.zip
```

## Что bundled в установщике

- ✅ Весь Rust backend (скомпилированный exe)
- ✅ Весь UI (index.html, ассеты)
- ✅ Все данные героев (data/heroes/*.json)
- ✅ Roles и synergies файлы
- ✅ Все зависимости

## Как пользователи устанавливают

1. Скачивают `.exe` или `.msi` из GitHub Releases
2. Запускают установщик
3. Приложение автоматически устанавливается с правами администратора
4. Можно запустить через Start Menu

## Дальнейшее

- Для macOS добавьте в matrix `platform: 'macos-latest'`
- Для Linux добавьте `platform: 'ubuntu-latest'`
- GitHub Actions автоматически создаст соответствующие артефакты
