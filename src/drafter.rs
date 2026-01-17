use std::collections::HashMap;
use crate::model::{Hero, RoleRules, SynergyRules, GamePhase};
use crate::loader::{load_heroes, load_roles, load_synergies};
use crate::scoring::score_hero;
use crate::analysis;

/// Рекомендация героя с объяснениями
#[derive(Debug, Clone)]
pub struct Recommendation {
    pub hero_name: String,
    pub score: i32,
    pub reasons: Vec<String>,
}

/// Основная структура для работы с драфтингом
pub struct Drafter {
    heroes: HashMap<String, Hero>,
    roles: RoleRules,
    synergies: SynergyRules,
}

impl Drafter {
    /// Создаёт новый Drafter, загружая все данные
    pub fn new(heroes_path: &str, roles_path: &str, synergies_path: &str) 
        -> Result<Self, Box<dyn std::error::Error>> 
    {
        let heroes = load_heroes(heroes_path)?;
        let roles = load_roles(roles_path)?;
        let synergies = load_synergies(synergies_path)?;

        Ok(Drafter {
            heroes,
            roles,
            synergies,
        })
    }

    /// Вычисляет профиль игровой фазы для команды
    fn calculate_team_phase(&self, team: &[String]) -> GamePhase {
        let mut phase = GamePhase { early: 0, mid: 0, late: 0 };
        for hero_name in team {
            if let Some(hero) = self.heroes.get(hero_name) {
                phase.early += hero.game_phase.early;
                phase.mid += hero.game_phase.mid;
                phase.late += hero.game_phase.late;
            }
        }
        phase
    }

    /// Возвращает список рекомендуемых героев для противодействия врагам
    /// 
    /// # Arguments
    /// * `enemies` - Список имён враждебных героев
    /// * `allies` - Список имён уже выбранных союзников
    /// * `limit` - Количество рекомендаций (по умолчанию 5)
    pub fn recommend(&self, enemies: Vec<String>, allies: Vec<String>, limit: usize) 
        -> Vec<Recommendation> 
    {
        let enemy_phase = self.calculate_team_phase(&enemies);

        let mut results: Vec<(String, i32, Vec<String>)> = Vec::new();

        for hero in self.heroes.values() {
            // Пропускаем уже выбранных
            if allies.contains(&hero.name) || enemies.contains(&hero.name) {
                continue;
            }

            let score = score_hero(
                hero,
                &allies,
                &enemies,
                &self.heroes,
                &self.roles,
                &self.synergies,
                &enemy_phase,
            );

            let reasons = analysis::explain(hero, &enemies, &self.heroes);
            results.push((hero.name.clone(), score, reasons));
        }

        // Сортируем по убыванию скора
        results.sort_by(|a, b| b.1.cmp(&a.1));

        // Конвертируем в Recommendation и ограничиваем результат
        results
            .into_iter()
            .take(limit)
            .map(|(name, score, reasons)| Recommendation {
                hero_name: name,
                score,
                reasons,
            })
            .collect()
    }

    /// Возвращает список всех доступных героев
    pub fn available_heroes(&self) -> Vec<String> {
        self.heroes.keys().cloned().collect()
    }

    /// Получает информацию о герое по имени
    pub fn get_hero(&self, name: &str) -> Option<&Hero> {
        self.heroes.get(name)
    }

    /// Возвращает список всех героев со всеми данными
    pub fn get_all_heroes(&self) -> Vec<&Hero> {
        self.heroes.values().collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_drafter_creation() {
        let drafter = Drafter::new("data/heroes", "data/roles.json", "data/synergies.json");
        assert!(drafter.is_ok());
    }
}
