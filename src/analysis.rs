use crate::model::Hero;
use std::collections::HashMap;

pub fn explain(hero: &Hero, enemy_team: &[String], all_heroes: &HashMap<String, Hero>) -> Vec<String> {
    let mut reasons = Vec::new();

    for enemy in enemy_team {
        // 1. Direct counters (defined in our file)
        if let Some(&val) = hero.explicit_counters.get(enemy) {
            if val < -2.0 {
                reasons.push(format!("Weak against {}", enemy));
            } else if val > 2.0 {
                reasons.push(format!("counters {}", enemy));
            }
        }

        // 2. Reverse counters (defined in enemy file)
        if let Some(enemy_hero) = all_heroes.get(enemy) {
            if let Some(&val) = enemy_hero.explicit_counters.get(&hero.name) {
                // If enemy says "Hero: -5", they are weak to us.
                if val < -2.0 {
                    reasons.push(format!("Counters {}", enemy));
                } else if val > 2.0 {
                     reasons.push(format!("Weak against {}", enemy));
                }
            }
        }
    }
    
    // Check phase
    if hero.game_phase.early >= 8 {
        reasons.push("Strong early game".to_string());
    } else if hero.game_phase.late >= 8 {
        reasons.push("Strong late game".to_string());
    }

    reasons.dedup(); // Remove duplicates if data overlaps
    reasons
}
