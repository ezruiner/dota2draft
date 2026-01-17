use crate::model::{Hero, RoleRules, SynergyRules, GamePhase};
use std::collections::HashMap;

fn primary_position(hero: &Hero) -> Option<(&str, f32, f32)> {
    let mut best_key: Option<&str> = None;
    let mut best_val: f32 = -1.0;
    let mut second_val: f32 = -1.0;

    for (k, v) in &hero.positions {
        if *v > best_val {
            second_val = best_val;
            best_val = *v;
            best_key = Some(k.as_str());
        } else if *v > second_val {
            second_val = *v;
        }
    }

    best_key.map(|k| (k, best_val.max(0.0), second_val.max(0.0)))
}

fn position_base_penalty(pos: &str) -> i32 {
    match pos {
        "pos_1" => 120,
        "pos_2" => 110,
        "pos_3" => 90,
        "pos_4" => 70,
        "pos_5" => 60,
        _ => 60,
    }
}

pub fn score_hero(
    hero: &Hero,
    allies: &[String],
    enemies: &[String],
    heroes: &HashMap<String, Hero>,
    roles: &RoleRules,
    synergies: &SynergyRules,
    enemy_team_phase: &GamePhase,
) -> i32 {
    let mut score = 0;

    // --- Team Balance Check ---
    let mut role_counts: HashMap<&String, i32> = HashMap::new();
    for ally in allies {
        if let Some(h) = heroes.get(ally) {
            for r in &h.roles {
                *role_counts.entry(r).or_insert(0) += 1;
            }
        }
    }

    // --- Position Balance (from pick_rate) ---
    let mut pos_counts: HashMap<&str, i32> = HashMap::new();
    for ally in allies {
        if let Some(h) = heroes.get(ally) {
            if let Some((pos, _, _)) = primary_position(h) {
                *pos_counts.entry(pos).or_insert(0) += 1;
            }
        }
    }

    if let Some((pos, top, second)) = primary_position(hero) {
        let count = *pos_counts.get(pos).unwrap_or(&0);
        let allowed = if pos == "pos_4" || pos == "pos_5" { 2 } else { 1 };

        // Flexibility: if hero is not strongly tied to one position, penalize less.
        let mut flex_factor = 1.0_f32;
        if top < 40.0 {
            flex_factor = 0.55;
        } else if top - second < 15.0 {
            flex_factor = 0.75;
        }

        if count >= allowed {
            let base = position_base_penalty(pos) as f32;
            let weight = (top / 100.0).clamp(0.0, 1.0);
            score -= (base * flex_factor * weight).round() as i32;
        }
    }

    // Penalize if core roles are taken
    for r in &hero.roles {
        let count = *role_counts.get(r).unwrap_or(&0);
        if r == "carry" && count >= 1 { score -= 100; }
        if r == "support" && count >= 2 { score -= 50; }
    }

    // --- Dynamic Game Phase ---
    // Calculate total enemy power
    let total_enemy_power = (enemy_team_phase.early + enemy_team_phase.mid + enemy_team_phase.late) as f32;
    if total_enemy_power > 0.0 {
        // Weights: Where is the enemy strongest? We need to match that.
        // Actually, if enemy is strong early, we want early defense.
        let w_early = enemy_team_phase.early as f32 / total_enemy_power;
        let w_mid = enemy_team_phase.mid as f32 / total_enemy_power;
        let w_late = enemy_team_phase.late as f32 / total_enemy_power;
        
        // Add weighted score based on hero's strength in those phases
        score += (hero.game_phase.early as f32 * w_early * 10.0) as i32;
        score += (hero.game_phase.mid as f32 * w_mid * 10.0) as i32;
        score += (hero.game_phase.late as f32 * w_late * 10.0) as i32;

        // Phase bias from tags (data-driven)
        if let Some(m) = synergies.phase_bias.get("early") {
            for t in &hero.tags {
                if let Some(v) = m.get(t) {
                    score += (*v as f32 * w_early).round() as i32;
                }
            }
        }
        if let Some(m) = synergies.phase_bias.get("mid") {
            for t in &hero.tags {
                if let Some(v) = m.get(t) {
                    score += (*v as f32 * w_mid).round() as i32;
                }
            }
        }
        if let Some(m) = synergies.phase_bias.get("late") {
            for t in &hero.tags {
                if let Some(v) = m.get(t) {
                    score += (*v as f32 * w_late).round() as i32;
                }
            }
        }
    } else {
        // Fallback
        score += hero.game_phase.late; 
    }

    // РЇР’РќР«Р• РљРћРќРўР Р«
    for enemy in enemies {
        // 1. Check if WE define the enemy as a counter/target
        if let Some(v) = hero.explicit_counters.get(enemy) {
            score += (*v * 2.0) as i32;  // РЈРјРЅРѕР¶Р°РµРј РЅР° 2 РґР»СЏ РІРµСЃР°
        }

        // 2. Check if the ENEMY defines US as a counter/target
        // If enemy has "Us": -10.0, it means we counter them -> Good for us (+10).
        // If enemy has "Us": 10.0, it means they counter us -> Bad for us (-10).
        if let Some(enemy_hero) = heroes.get(enemy) {
            if let Some(v) = enemy_hero.explicit_counters.get(&hero.name) {
                score -= (*v * 2.0) as i32; // Subtract to reverse the perspective
            }
        }
    }

    // РЇР’РќР«Р• РЎРРќР•Р Р“РР
    for ally in allies {
        if let Some(v) = hero.explicit_synergies.get(ally) {
            score += (*v * 2.0) as i32;  // РЈРјРЅРѕР¶Р°РµРј РЅР° 2 РґР»СЏ РІРµСЃР°
        }
    }

    // Р РћР›Р
    for ally in allies {
        if let Some(ally_hero) = heroes.get(ally) {
            for r1 in &hero.roles {
                for r2 in &ally_hero.roles {
                    let key1 = format!("{}+{}", r1, r2);
                    let key2 = format!("{}+{}", r2, r1);

                    if let Some(v) = roles.role_synergies.get(&key1).or_else(|| roles.role_synergies.get(&key2)) {
                        score += v;
                    }
                    if let Some(v) = roles.role_conflicts.get(&key1).or_else(|| roles.role_conflicts.get(&key2)) {
                        score += v;
                    }
                }
            }
        }
    }

    // РўР•Р“Р (СЃРѕСЋР·)
    for ally in allies {
        if let Some(ally_hero) = heroes.get(ally) {
            for t1 in &hero.tags {
                for t2 in &ally_hero.tags {
                    let key1 = format!("{}+{}", t1, t2);
                    let key2 = format!("{}+{}", t2, t1);
                    if let Some(v) = synergies.tag_synergies.get(&key1).or_else(|| synergies.tag_synergies.get(&key2)) {
                        score += v;
                    }
                }
            }
        }
    }

    // РўР•Р“Р (РІСЂР°РіРё)
    for enemy in enemies {
        if let Some(enemy_hero) = heroes.get(enemy) {
            for t1 in &hero.tags {
                for t2 in &enemy_hero.tags {
                    let key = format!("{}+{}", t2, t1);
                    if let Some(v) = synergies.tag_counters.get(&key) {
                        score += v;
                    }
                }
            }
        }
    }

    // Р¤РђР—Рђ РР“Р Р« (СѓРїСЂРѕС‰С‘РЅРЅРѕ вЂ” late)
    // score += hero.game_phase.late; // Removed in favor of dynamic calculation above

    score / 10
}