# Dota 2 Helper

Приложение для помощи в выборе героев в Dota 2, основанное на анализе команд противника и синергиях.

## Структура проекта

```
dota2_helper/
├── src/                  # Rust исходный код
│   ├── main.rs          # Entry point приложения с Tauri интеграцией
│   ├── lib.rs           # Модули приложения
│   ├── model.rs         # Структуры данных героев
│   ├── loader.rs        # Загрузка данных из JSON
│   ├── drafter.rs       # Логика драфтинга и рекомендаций
│   ├── scoring.rs       # Система оценки героев
│   └── analysis.rs      # Анализ и объяснение рекомендаций
├── data/                # Данные о героях
│   ├── heroes/          # JSON файлы каждого героя
│   ├── roles.json       # Правила ролей
│   └── synergies.json   # Синергии и контры
├── ui/                  # HTML/CSS/JS интерфейс
│   └── index.html       # Главная страница
├── build.rs             # Build скрипт для Tauri
├── Cargo.toml           # Зависимости Rust
├── tauri.conf.json      # Конфигурация Tauri приложения
└── package.json         # NPM зависимости

```

## Требования

- Rust 1.60+
- Node.js (для Tauri CLI)
- Windows, macOS или Linux

## Установка

### 1. Установка Rust (если не установлен)

```bash
# Windows (PowerShell):
Invoke-WebRequest -Uri https://rustup.rs -OutFile rustup-init.exe
./rustup-init.exe

# macOS/Linux:
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### 2. Установка зависимостей

```bash
# Windows (в PowerShell как администратор):
cargo install tauri-cli --version "^1.5"

# или через npm:
npm install
```

## Запуск разработки

```bash
# Запуск с горячей перезагрузкой
cargo tauri dev

# или через npm:
npm run dev
```

## Сборка

```bash
# Сборка для распространения
cargo tauri build

# или через npm:
npm run build
```

Бинарник будет в `src-tauri/target/release/bundle/`.

## API Команды (Tauri)

### init_drafter
Инициализирует систему драфтинга и загружает все данные о героях.

```javascript
const result = await invoke('init_drafter');
```

### get_recommendations
Получает рекомендации героев на основе команды противника и союзников.

```javascript
const recommendations = await invoke('get_recommendations', {
  enemyTeam: ['Anti-Mage', 'Pudge', 'Axe'],
  allies: ['Shadow Shaman'],
  count: 10
});
```

### get_hero_data
Получает полную информацию о конкретном герое.

```javascript
const heroData = await invoke('get_hero_data', {
  heroName: 'Anti-Mage'
});
```

## Структура данных героя

Каждый герой содержит:
- `name`: Имя героя
- `primary_attribute`: Основной атрибут (STR, AGI, INT)
- `roles`: Список ролей (Carry, Support, Mid и т.д.)
- `tags`: Теги характеристик
- `positions`: Рекомендуемые позиции (1-5) с оценками
- `game_phase`: Сила на разных этапах игры (early, mid, late)
- `explicit_counters`: Прямые контры с оценками
- `explicit_synergies`: Синергии с другими героями

## Разработка

Для добавления новых функций:

1. Добавьте Rust функцию в `src/main.rs`
2. Оберните её с помощью `#[tauri::command]`
3. Добавьте функцию в `invoke_handler`
4. Используйте в UI через `invoke()` из `@tauri-apps/api`

## Лицензия

MIT
