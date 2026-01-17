import cloudscraper
import json
import time
import sys
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==========================================
# Default values (can be overridden by command line arguments)
STRATZ_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJTdWJqZWN0IjoiNWUyNWJkZWYtYzM0Ni00YzQzLWI3NWItOWY4ZGVlN2M1ZmE4IiwiU3RlYW1JZCI6IjM2MTczOTA4MCIsIkFQSVVzZXIiOiJ0cnVlIiwibmJmIjoxNzY2NDMzMjE4LCJleHAiOjE3OTc5NjkyMTgsImlhdCI6MTc2NjQzMzIxOCwiaXNzIjoiaHR0cHM6Ly9hcGkuc3RyYXR6LmNvbSJ9.FoawYjtPFL2XY4_VBogd2PDEf7LBHx9x2cSgWCSop3Y"
MAX_WORKERS = 5
MAX_WAIT_TIME = 60

# Parse command line arguments
if len(sys.argv) > 1:
    STRATZ_TOKEN = sys.argv[1]
if len(sys.argv) > 2:
    try:
        MAX_WORKERS = int(sys.argv[2])
    except ValueError:
        pass

print(f"⚙️ Config: MAX_WORKERS={MAX_WORKERS}")
# ==========================================

API_URL = "https://api.stratz.com/graphql"
scraper = cloudscraper.create_scraper()

ATTR_MAP = {"str": "Strength", "agi": "Agility", "int": "Intelligence", "all": "Universal"}

# --- ЗАПРОСЫ ---

QUERY_HEROES = """
query {
  constants {
    heroes {
      id
      displayName
      stats { primaryAttribute }
      roles { roleId } 
    }
  }
}
"""

QUERY_POSITIONS = """
query GetPosStats($pos: [MatchPlayerPositionType]) {
  heroStats {
    winWeek(positionIds: $pos) {
      heroId
      matchCount
      winCount
    }
  }
}
"""

QUERY_MATCHUP = """
query GetMatchup($hid: Short!) {
  heroStats {
    matchUp(heroId: $hid, take: 150) {
      heroId
      vs { heroId2 matchCount winCount }
      with { heroId2 matchCount winCount synergy }
    }
  }
}
"""

def make_request(query, variables=None, context=""):
    """
    Умная функция запроса с защитой от 429 и таймаутом.
    """
    headers = {
        "Authorization": f"Bearer {STRATZ_TOKEN}",
        "Content-Type": "application/json"
    }
    
    total_slept = 0
    current_sleep = 1 # Начальная пауза
    
    while total_slept < MAX_WAIT_TIME:
        try:
            resp = scraper.post(API_URL, json={'query': query, 'variables': variables}, headers=headers)
            
            # 1. УСПЕХ
            if resp.status_code == 200:
                data = resp.json()
                if 'errors' in data:
                    print(f"\n❌ API Error [{context}]: {data['errors'][0]['message']}")
                    return None
                return data['data']
            
            # 2. ЛИМИТ ЗАПРОСОВ (429)
            elif resp.status_code == 429:
                # Пытаемся узнать, сколько ждать, из заголовков
                retry_after = int(resp.headers.get("Retry-After", current_sleep))
                
                time.sleep(retry_after)
                total_slept += retry_after
                current_sleep *= 2 # Увеличиваем паузу для следующего раза
                continue
            
            # 3. ОШИБКИ СЕРВЕРА (502, 500)
            elif resp.status_code >= 500:
                print(f"\n⚠️ Ошибка сервера {resp.status_code}. Ждем 5 сек...", end="\r")
                time.sleep(5)
                total_slept += 5
                continue
                
            else:
                print(f"\n❌ HTTP Ошибка {resp.status_code} [{context}]")
                return None
                
        except Exception as e:
            print(f"\n❌ Exception: {e}")
            time.sleep(2)
            total_slept += 2
            
    print(f"\n⛔ ПРЕВЫШЕН ЛИМИТ ОЖИДАНИЯ ({MAX_WAIT_TIME} сек). Пропускаем запрос.")
    return None

def process_hero_matchups(hid, hero_name, id_name_map):
    data = make_request(QUERY_MATCHUP, variables={"hid": hid}, context=hero_name)
    
    counters = []
    synergies = []
    
    if data and data.get('heroStats') and data['heroStats'].get('matchUp'):
        matchups = data['heroStats']['matchUp']
        
        vs_agg = {}
        with_agg = {}
        
        for m in matchups:
            # VS
            if m.get('vs'):
                for item in m['vs']:
                    eid = item.get('heroId2')
                    if not eid or eid == hid: continue
                    if eid not in vs_agg: vs_agg[eid] = {"w": 0, "m": 0}
                    vs_agg[eid]["w"] += item.get('winCount', 0)
                    vs_agg[eid]["m"] += item.get('matchCount', 0)
            
            # WITH
            if m.get('with'):
                for item in m['with']:
                    aid = item.get('heroId2')
                    if not aid or aid == hid: continue
                    if aid not in with_agg: with_agg[aid] = {"syn": 0, "cnt": 0}
                    if item.get('synergy') is not None:
                        with_agg[aid]["syn"] += item['synergy']
                        with_agg[aid]["cnt"] += 1

        # Контрпики (Score < 0)
        list_vs = []
        for eid, s in vs_agg.items():
            if s["m"] > 30: 
                win_rate = (s["w"] / s["m"]) * 100
                score = win_rate - 50.0 
                list_vs.append({"hero": id_name_map.get(eid, str(eid)), "score": score})
        
        list_vs.sort(key=lambda x: x['score'])
        counters = [{"hero": x['hero'], "counter_score": round(x['score'], 2)} for x in list_vs[:10]]

        # Связки
        list_with = []
        for aid, s in with_agg.items():
            if s["cnt"] > 0:
                list_with.append({"hero": id_name_map.get(aid, str(aid)), "syn": s["syn"] / s["cnt"]})
        
        list_with.sort(key=lambda x: x['syn'], reverse=True)
        synergies = [{"hero": x['hero'], "synergy_score": round(x['syn'], 2)} for x in list_with[:10]]
        
    return hid, counters, synergies

def main():
    print(f"=== ЗАПУСК СКРИПТА (MAX WAIT: {MAX_WAIT_TIME}s) ===")

    # 1. ГЕРОИ
    print("1. Скачиваем список героев...", end=" ")
    data_const = make_request(QUERY_HEROES, context="Constants")
    if not data_const: return
    print("OK")

    heroes = {}
    id_name_map = {}

    for h in data_const['constants']['heroes']:
        hid = h['id']
        id_name_map[hid] = h['displayName']
        
        raw_attr = h.get('stats', {}).get('primaryAttribute', 'str')
        h_roles = [str(r['roleId']).title() for r in h.get('roles', [])]

        heroes[hid] = {
            "id": hid,
            "name": h['displayName'],
            "primary_attr": ATTR_MAP.get(raw_attr, raw_attr.capitalize()),
            "roles": h_roles,
            "positions": {},
            "counters": [],
            "synergies": [],
            "_pos_stats": {} # Инициализируем сразу, чтобы не было ошибок
        }

    # 2. ПОЗИЦИИ
    print("2. Скачиваем статистику позиций (All Ranks)...")
    positions = [("POSITION_1", 1), ("POSITION_2", 2), ("POSITION_3", 3), ("POSITION_4", 4), ("POSITION_5", 5)]
    
    for pos_code, pos_num in positions:
        print(f"   -> Загрузка Pos {pos_num}...")
        p_data = make_request(QUERY_POSITIONS, variables={"pos": [pos_code]}, context=f"Pos {pos_num}")
        
        if p_data and p_data.get('heroStats'):
            for s in p_data['heroStats'].get('winWeek', []):
                hid = s['heroId']
                if hid in heroes:
                    # Просто добавляем данные, не проверяя ключи (так как _pos_stats уже создан)
                    heroes[hid]["_pos_stats"][f"pos_{pos_num}"] = {
                        "matches": s['matchCount'],
                        "wins": s['winCount']
                    }
    
    # Расчет процентов
    print("\n   -> Рассчитываем проценты пиков...")
    for hid, h_data in heroes.items():
        stats = h_data.get("_pos_stats", {})
        total_matches = sum(item['matches'] for item in stats.values())
        
        if total_matches > 0:
            for pos_key, item in stats.items():
                m = item['matches']
                # Pick Rate = % от общего числа игр героя
                pick_rate = (m / total_matches) * 100
                win_rate = (item['wins'] / m) * 100
                
                h_data["positions"][pos_key] = {
                    "pick_count": m,
                    "pick_rate": f"{round(pick_rate, 1)}%",
                    "win_rate": f"{round(win_rate, 1)}%"
                }
        del h_data["_pos_stats"]

    # 3. МАТЧАПЫ
    print(f"3. Скачиваем матчапы ({MAX_WORKERS} потоков)...")
    hero_ids = list(heroes.keys())
    completed = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_hero_matchups, hid, heroes[hid]['name'], id_name_map): hid for hid in hero_ids}
        
        for future in as_completed(futures):
            try:
                hid, counters, synergies = future.result()
                heroes[hid]["counters"] = counters
                heroes[hid]["synergies"] = synergies
            except Exception as e:
                print(f"\n❌ Ошибка в потоке: {e}")
            
            completed += 1
            if completed % 5 == 0 or completed == len(hero_ids):
                 print(f"   [{completed}/{len(hero_ids)}] {heroes[hid]['name']}")

    # 4. СОХРАНЕНИЕ
    print("\n\n4. Сохранение файла...")
    final_list = sorted(list(heroes.values()), key=lambda x: x['name'])
    
    if not os.path.exists('data'):
        os.makedirs('data')

    filename = "data/dota_heroes_stratz.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)

    # 5. ОБНОВЛЕНИЕ ФАЙЛОВ ГЕРОЕВ
    print(f"5. Обновление данных о героях...")
    result = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "update_heroes_data.py")], capture_output=True, text=True, encoding='utf-8')
    print(result.stdout)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⛔ Скрипт остановлен пользователем.")