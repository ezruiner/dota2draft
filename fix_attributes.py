import json
from pathlib import Path

heroes_dir = Path("data/heroes")

# Correct attribute mapping based on provided screenshots
attribute_map = {
    # STRENGTH
    "Alchemist": "strength", "Axe": "strength", "Bristleback": "strength", 
    "Centaur Warrunner": "strength", "Chaos Knight": "strength", "Clockwerk": "strength",
    "Dawnbreaker": "strength", "Doom": "strength", "Dragon Knight": "strength", 
    "Earth Spirit": "strength", "Earthshaker": "strength", "Elder Titan": "strength",
    "Huskar": "strength", "Kunkka": "strength", "Largo": "strength", 
    "Legion Commander": "strength", "Lifestealer": "strength", "Lycan": "strength",
    "Mars": "strength", "Night Stalker": "strength", "Ogre Magi": "strength",
    "Omniknight": "strength", "Phoenix": "strength", "Primal Beast": "strength",
    "Pudge": "strength", "Slardar": "strength", "Spirit Breaker": "strength",
    "Sven": "strength", "Tidehunter": "strength", "Timbersaw": "strength",
    "Tiny": "strength", "Treant Protector": "strength", "Tusk": "strength",
    "Underlord": "strength", "Undying": "strength", "Wraith King": "strength",
    
    # AGILITY
    "Anti-Mage": "agility", "Bloodseeker": "agility", "Bounty Hunter": "agility",
    "Broodmother": "agility", "Clinkz": "agility", "Drow Ranger": "agility",
    "Ember Spirit": "agility", "Faceless Void": "agility", "Gyrocopter": "agility",
    "Hoodwink": "agility", "Juggernaut": "agility", "Kez": "agility",
    "Lone Druid": "agility", "Luna": "agility", "Medusa": "agility",
    "Meepo": "agility", "Mirana": "agility", "Monkey King": "agility",
    "Morphling": "agility", "Naga Siren": "agility", "Phantom Assassin": "agility",
    "Phantom Lancer": "agility", "Razor": "agility", "Riki": "agility",
    "Shadow Fiend": "agility", "Slark": "agility", "Sniper": "agility",
    "Spectre": "agility", "Templar Assassin": "agility", "Terrorblade": "agility",
    "Troll Warlord": "agility", "Ursa": "agility", "Vengeful Spirit": "agility",
    "Viper": "agility", "Weaver": "agility",
    
    # INTELLIGENCE
    "Ancient Apparition": "intelligence", "Chen": "intelligence", "Crystal Maiden": "intelligence",
    "Dark Seer": "intelligence", "Dark Willow": "intelligence", "Disruptor": "intelligence",
    "Enchantress": "intelligence", "Grimstroke": "intelligence", "Invoker": "intelligence",
    "Jakiro": "intelligence", "Keeper of the Light": "intelligence", "Leshrac": "intelligence",
    "Lich": "intelligence", "Lina": "intelligence", "Lion": "intelligence",
    "Muerta": "intelligence", "Necrophos": "intelligence", "Oracle": "intelligence",
    "Outworld Devourer": "intelligence", "Puck": "intelligence", "Pugna": "intelligence",
    "Queen of Pain": "intelligence", "Ringmaster": "intelligence", "Rubick": "intelligence", "Shadow Demon": "intelligence",
    "Shadow Shaman": "intelligence", "Silencer": "intelligence", "Skywrath Mage": "intelligence",
    "Storm Spirit": "intelligence", "Tinker": "intelligence", "Warlock": "intelligence",
    "Winter Wyvern": "intelligence", "Witch Doctor": "intelligence", "Zeus": "intelligence",
    
    # UNIVERSAL
    "Abaddon": "universal", "Arc Warden": "universal", "Bane": "universal",
    "Batrider": "universal", "Beastmaster": "universal", "Brewmaster": "universal",
    "Dazzle": "universal", "Death Prophet": "universal", "Enigma": "universal",
    "Io": "universal", "Magnus": "universal", "Marci": "universal",
    "Nature's Prophet": "universal", "Nyx Assassin": "universal", "Pangolier": "universal",
    "Sand King": "universal", "Snapfire": "universal",
    "Techies": "universal", "Venomancer": "universal", "Visage": "universal",
    "Void Spirit": "universal", "Windranger": "universal"
}

# Process all hero JSON files
updated_count = 0
for hero_file in heroes_dir.glob("*.json"):
    with open(hero_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    hero_name = data.get("name", "")
    
    if hero_name in attribute_map:
        new_attribute = attribute_map[hero_name]
        old_attribute = data.get("primary_attribute", "unknown")
        
        if old_attribute != new_attribute:
            data["primary_attribute"] = new_attribute
            with open(hero_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Updated: {hero_file.name} {old_attribute} → {new_attribute}")
            updated_count += 1
        else:
            print(f"OK: {hero_file.name} ({new_attribute})")
    else:
        print(f"WARNING: Unknown hero: {hero_name}")

print(f"\nTotal updated: {updated_count}")
