# Hero Data Structure Guide

## JSON Format for Heroes

Each hero file in `data/heroes/` should follow this structure:

```json
{
  "name": "Hero Name",
  "primary_attribute": "strength",
  "roles": ["role1", "role2"],
  "tags": ["tag1", "tag2", "tag3"],
  "positions": {
    "pos_1": 0.0,
    "pos_2": 0.0,
    "pos_3": 0.0,
    "pos_4": 0.0,
    "pos_5": 0.0
  },
  "game_phase": {
    "early": 0,
    "mid": 0,
    "late": 0
  },
  "explicit_counters": {
    "Enemy Hero Name": -10
  },
  "explicit_synergies": {
    "Ally Hero Name": 10
  }
}
```

## Field Descriptions

### `primary_attribute`
Основной атрибут героя (для фильтрации):
- `strength` - Сила (красные герои, танки и бойцы ближнего боя)
- `agility` - Ловкость (зелёные герои, физический урон и атакеры)
- `intelligence` - Интеллект (синие герои, маги и саппорты)
- `universal` - Универсальный (получает бонусы от всех атрибутов)

**Примеры:**
- Abaddon, Axe, Pudge → `"strength"`
- Anti-Mage, Juggernaut, Sniper → `"agility"`
- Crystal Maiden, Lina, Invoker → `"intelligence"`
- Marci, Kez, Ringmaster → `"universal"`

### `positions` (NEW)
Процент игр на каждой позиции - конкретная роль в команде (данные со Stratz):
- `pos_1`: **Carry** - легкая линия (safe lane), основной урон в лейте, высокий приоритет фарма
- `pos_2`: **Mid** - центральная линия, соло-опыт, обычно магический урон или ганкер
- `pos_3`: **Offlane** - сложная линия, танк/инициатор, меньше фарма чем керри
- `pos_4`: **Semi-support** - частичная поддержка, роумер, не самый бедный саппорт
- `pos_5`: **Full support** - полная поддержка, покупает варды/смоки, самый бедный

**Пример:**
```json
"positions": {
  "pos_1": 82.5,  // Играют керри в 82.5% случаев
  "pos_2": 5.2,   // Мид в 5.2%
  "pos_3": 8.1,   // Оффлейн в 8.1%
  "pos_4": 3.0,   // Роумер в 3%
  "pos_5": 1.2    // Хард саппорт в 1.2%
}
```

### `roles`
Широкие игровые роли - описывают функции героя в команде (используются в `roles.json` для синергий/конфликтов):
- `core` - нуждается в фарме и опыте (carry/mid/offlane)
- `support` - поддержка команды, не требует много золота
- `initiator` - инициация боев
- `disable` - контроль врагов (стан, сайленс, хекс)
- `durable` - выносливый, танкует урон
- `nuker` - магический взрывной урон
- `pusher` - разрушение строений
- `escape` - механики побега
- `jungler` - может фармить лес

**Важно:** Эти роли влияют на скоринг через `data/roles.json`:
```json
"role_synergies": {
  "core+support": 12,  // кор хорошо с саппортом
  "core+disable": 10,  // кору нужен контроль
  "initiator+nuker": 8  // инициация + урон
},
"role_conflicts": {
  "core+core": -8  // много коров = мало места для фарма
}
```

### `tags`
Механики и стиль игры (используются в `synergies.json`):

**Основные теги (общие):**
- `melee` / `ranged` - дальность атаки
- `physical_damage` / `magical_damage` / `pure_damage` - тип урона
- `aoe` - массовый урон/эффекты
- `burst_damage` - взрывной урон
- `tank` - высокая живучесть
- `mobile` - высокая мобильность
- `late_scaler` / `hard_carry` - сила в лейте
- `sustain` - исцеление/регенерация
- `lockdown` - жесткий контроль (стан)
- `disable_heavy` - много разных видов контроля
- `dispel` - снятие эффектов
- `save` - спасение союзников
- `push` - пуш линий/строений
- `splitpush` - разделение карты
- `vision` - обеспечение обзора

**Специфичные теги (уникальные механики):**
- `invis` / `stealth` - невидимость
- `summoner` - призывает юнитов
- `illusion` - создает иллюзии
- `mana_dependent` - сильно зависим от маны
- `manaburn` / `mana_drain` - сжигание/выкачивание маны
- `anti_heal` - блокирует исцеление
- `anti_tank` - эффективен против танков
- `spell_immunity` - невосприимчивость к магии
- `bkb_disable` - контроль сквозь BKB
- `armor_reduction` - снижение брони
- `percent_damage` - урон от % здоровья
- `repositioning` - перемещение юнитов
- `buff_specialist` - дает сильные баффы
- `elusive` - сложно поймать
- `glass_cannon` - высокий урон, низкая живучесть
- `early_bully` - доминирует на линии
- `roaming` - эффективный гангер
- `micro` - требует контроля нескольких юнитов
- `transform` - может менять форму
- `rebirth_mechanic` - возрождение после смерти
- `fear` / `hex` / `silence` / `slow` / `root` - специфичные виды контроля

**Важно:** Теги влияют на скоринг через `data/synergies.json`:
```json
"tag_synergies": {
  "lockdown+burst_damage": 18,  // контроль + урон = отлично
  "armor_reduction+physical_damage": 16,  // -броня для физ. урона
  "tank+save": 14  // танк с сейвом = защита команды
},
"tag_counters": {
  "illusion+aoe": 18,  // АОЕ контрит иллюзии
  "mana_dependent+manaburn": -18,  // манаберн против мана-зависимых
  "heal_based+anti_heal": -20  // анти-хил против хил-героев
}
```

### `game_phase`
Сила героя в разные фазы игры (значения -10 до +10):
- `early`: 0-15 минут
- `mid`: 15-35 минут  
- `late`: 35+ минут

**Примеры:**
- Anti-Mage: `{"early": -8, "mid": 2, "late": 10}` - слаб рано, силён поздно
- Venomancer: `{"early": 8, "mid": 6, "late": 2}` - силён рано, слабеет в лейте

### `explicit_counters`
Явные контрпики из Stratz — герои, которые *контрят* этого героя (только отрицательные значения):
- Значения = разница винрейта в % (всегда отрицательные)
- Берём топ-10 худших матчапов из https://stratz.com/heroes/X/matchups
- Положительные матчапы (кого герой контрит) НЕ добавляем — это упрощает логику

**Пример:**
```json
"explicit_counters": {
  "Anti-Mage": -5.0,    // -5.0% винрейт, АМ контрит этого героя
  "Axe": -4.0,          // -4.0% винрейт, Акс контрит
  "Silencer": -3.0      // -3.0% винрейт
}
```

### `explicit_synergies`  
Явные синергии из Stratz — союзники, с которыми герой хорошо играет (только положительные значения):
- Значения = разница винрейта в % (всегда положительные)
- Берём топ-10 лучших союзников из https://stratz.com/heroes/X/matchups в секции "С" или "Рекомендуемые партнеры"
- Плохие синергии (анти-синергии) НЕ добавляем — учитываются через role_conflicts

**Пример:**
```json
"explicit_synergies": {
  "Necrophos": 5.0,      // +5.0% винрейт в одной команде
  "Sniper": 4.0,         // +4.0% винрейт синергия
  "Huskar": 3.5          // +3.5% винрейт
}
```

## Data Sources

### Stratz Pages
1. **Hero Overview**: `https://stratz.com/heroes/{id}-{name}`
   - Частота выбора на каждую позицию (для `positions`)
   
2. **Matchups**: `https://stratz.com/heroes/{id}-{name}/matchups`
   - Топ-10 лучших матчапов → `explicit_synergies`
   - Топ-10 худших матчапов → `explicit_counters`

### Scaling Guidelines
- Очки = Винрейт разница в % (1:1 соответствие, без ограничения на ±10)
- Примеры:
  - Винрейт +5.0% → 5 очков
  - Винрейт -3.2% → -3.2 очка (или -3 округлённо)
  - Винрейт +12.5% → 12.5 очков (может быть > 10)

## Example: Abaddon

```json
{
  "name": "Abaddon",
  "primary_attribute": "universal",
  "roles": ["support", "durable"],
  "tags": ["sustain", "dispel", "save"],
  "positions": {
    "pos_1": 0.0,    // Никогда не играют керри
    "pos_2": 1.4,    // Редко мид
    "pos_3": 14.9,   // Иногда оффлейн
    "pos_4": 23.1,   // Часто роумер (4-ка)
    "pos_5": 37.7    // Чаще всего хард саппорт (5-ка)
  },
  "game_phase": {
    "early": 6,
    "mid": 7,
    "late": 8
  },
  "explicit_counters": {
    "Io": -5.0,
    "Dark Seer": -4.5,
    "Anti-Mage": -4.0
  },
  "explicit_synergies": {
    "Necrophos": 5.0,
    "Sniper": 4.5,
    "Lina": 4.0
  }
}
```

## Adding New Roles/Tags

При добавлении новых значений в `roles` или `tags`:

1. **Для roles**: обновить `data/roles.json`:
```json
{
  "role_synergies": {
    "new_role+support": 8
  },
  "role_conflicts": {
    "new_role+new_role": -10
  }
}
```

2. **Для tags**: обновить `data/synergies.json`:
```json
{
  "tag_synergies": {
    "new_tag+another_tag": 10
  },
  "tag_counters": {
    "new_tag+counter_tag": -10
  }
}
```

Система автоматически учтёт новые роли/теги при анализе драфта через `src/scoring.rs`.
