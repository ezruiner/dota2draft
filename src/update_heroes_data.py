#!/usr/bin/env python3
"""
Парсер для обновления данных героев из dota_heroes_stratz.json
Проходит по каждому герою и обновляет:
- Имя (name)
- Атрибут (primary_attribute)
- Роли (roles)
- Позиции (positions)
- Контрпики (explicit_counters)
- Синергии (explicit_synergies)
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List

DATA_DIR = Path(__file__).parent.parent / "data"
HEROES_DIR = DATA_DIR / "heroes"
STRATZ_FILE = DATA_DIR / "dota_heroes_stratz.json"


def load_stratz_data() -> Dict[str, Any]:
    """Загружает данные из dota_heroes_stratz.json"""
    with open(STRATZ_FILE, 'r', encoding='utf-8') as f:
        heroes_list = json.load(f)
    
    # Создаем словарь по имени героя для быстрого поиска
    heroes_by_name = {}
    # Ассоциативный массив переименованных героев
    name_mappings = {
        'outworld devourer': 'outworld destroyer',
    }
    
    for hero in heroes_list:
        hero_name_lower = hero['name'].lower()
        heroes_by_name[hero_name_lower] = hero
        # Добавляем альтернативные имена
        for local_name, stratz_name in name_mappings.items():
            if stratz_name == hero_name_lower:
                heroes_by_name[local_name] = hero
    
    return heroes_by_name


def normalize_attribute(attr: str) -> str:
    """Нормализует атрибут из stratz формата в локальный"""
    attr_lower = attr.lower()
    if attr_lower == 'universal':
        return 'universal'
    elif attr_lower == 'strength':
        return 'strength'
    elif attr_lower == 'agility':
        return 'agility'
    elif attr_lower == 'intelligence':
        return 'intelligence'
    return attr_lower


def normalize_roles(roles: List[str]) -> List[str]:
    """Нормализует роли из stratz формата"""
    role_mapping = {
        'carry': 'carry',
        'durable': 'durable',
        'support': 'support',
        'disabler': 'disabler',
        'initiator': 'initiator',
        'nuker': 'nuker',
        'escaper': 'escaper',
    }
    
    normalized = []
    for role in roles:
        role_lower = role.lower()
        if role_lower in role_mapping:
            normalized.append(role_mapping[role_lower])
    
    return normalized


def extract_counters(counters_list: List[Dict]) -> Dict[str, float]:
    """Преобразует список контрпиков в словарь"""
    result = {}
    for counter in counters_list[:10]:  # Берем топ 10
        hero_name = counter['hero']
        score = counter['counter_score']
        result[hero_name] = score
    return result


def extract_synergies(synergies_list: List[Dict]) -> Dict[str, float]:
    """Преобразует список синергий в словарь"""
    result = {}
    for synergy in synergies_list[:10]:  # Берем топ 10
        hero_name = synergy['hero']
        score = synergy['synergy_score']
        result[hero_name] = score
    return result


def extract_positions(positions: Dict) -> Dict[str, float]:
    """Извлекает позиции с pick_rate в качестве показателя"""
    result = {}
    for pos, data in positions.items():
        if isinstance(data, dict) and 'pick_rate' in data:
            # Берем pick_rate и нормализуем (убираем %)
            pick_rate_str = data['pick_rate'].rstrip('%')
            try:
                result[pos] = float(pick_rate_str)
            except ValueError:
                result[pos] = 0.0
    return result


def find_hero_file(hero_name: str, verbose=False) -> Path | None:
    """Находит файл героя, пробуя разные форматы имён"""
    # Маппинг имён для специальных случаев
    special_mappings = {
        'outworld destroyer': 'outworld_devourer.json',
    }
    
    hero_name_lower = hero_name.lower()
    if hero_name_lower in special_mappings:
        hero_file = HEROES_DIR / special_mappings[hero_name_lower]
        if hero_file.exists():
            return hero_file

    # Попробуем разные варианты
    variants = [
        hero_name.lower().replace(' ', '_').replace('-', '_') + '.json',  # anti_mage
        hero_name.lower().replace(' ', '_').replace("'", '') + '.json',    # natures_prophet
        hero_name.lower().replace(' ', '_') + '.json',                     # standard
        hero_name.lower().replace(' ', '-') + '.json',                     # anti-mage
    ]
    
    for variant in variants:
        hero_file = HEROES_DIR / variant
        if hero_file.exists():
            return hero_file
    
    return None


def update_hero_file(hero_name: str, stratz_data: Dict[str, Any], verbose=False) -> bool:
    """Обновляет файл героя данными из stratz"""
    hero_file = find_hero_file(hero_name, verbose=verbose)
    
    if not hero_file:
        if verbose:
            print(f"[!] Файл не найден для: {hero_name}")
        return False
    
    # Загружаем текущие данные героя
    with open(hero_file, 'r', encoding='utf-8') as f:
        hero_data = json.load(f)
    
    # Обновляем данные
    hero_data['name'] = stratz_data['name']
    hero_data['primary_attribute'] = normalize_attribute(stratz_data['primary_attr'])
    hero_data['roles'] = normalize_roles(stratz_data['roles'])
    
    # Обновляем позиции (если нет поля, создаем новое)
    if 'positions' not in hero_data:
        hero_data['positions'] = {}
    hero_data['positions'] = extract_positions(stratz_data['positions'])
    
    # Обновляем контрпики
    hero_data['explicit_counters'] = extract_counters(stratz_data['counters'])
    
    # Обновляем синергии
    hero_data['explicit_synergies'] = extract_synergies(stratz_data['synergies'])
    
    # Сохраняем обновленные данные
    with open(hero_file, 'w', encoding='utf-8') as f:
        json.dump(hero_data, f, ensure_ascii=False, indent=2)
    
    return True


def main(verbose=False):
    """Главная функция"""
    if verbose:
        print("[*] Загружаем данные из dota_heroes_stratz.json...")
    stratz_data = load_stratz_data()
    if verbose:
        print(f"[OK] Загружено {len(stratz_data)} героев\n")
        print(f"[*] Сканируем папку {HEROES_DIR}...\n")
    
    updated_count = 0
    failed_count = 0
    
    # Получаем все файлы .json в папке heroes
    hero_files = sorted(HEROES_DIR.glob("*.json"))
    if verbose:
        print(f"Найдено файлов: {len(hero_files)}\n")
    
    for hero_file in hero_files:
        with open(hero_file, 'r', encoding='utf-8') as f:
            hero_local_data = json.load(f)
        
        hero_name = hero_local_data.get('name', '')
        
        if hero_name.lower() in stratz_data:
            if update_hero_file(hero_name, stratz_data[hero_name.lower()], verbose=verbose):
                updated_count += 1
            else:
                failed_count += 1
        else:
            print(f"[!] {hero_name}: не найден в stratz данных")
            failed_count += 1
    
    print(f"\n{'='*50}")
    print(f"Результаты:⤵️")
    print(f"   [✔️] Обновлено: {updated_count}")
    print(f"   [❌] Ошибок: {failed_count}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
