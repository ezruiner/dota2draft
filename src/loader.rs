use std::fs;
use std::collections::HashMap;
use std::error::Error;
use crate::model::{Hero, RoleRules, SynergyRules};

pub fn load_heroes(path: &str) -> Result<HashMap<String, Hero>, Box<dyn Error>> {
    let mut heroes = HashMap::new();

    let entries = fs::read_dir(path)?;

    for entry in entries {
        let entry = entry?;
        let file_path = entry.path();
        let data = fs::read_to_string(&file_path)?;
        
        // Добавляем информацию о файле в случае ошибки
        let hero: Hero = serde_json::from_str(&data)
            .map_err(|e| format!("Failed to parse {:?}: {}", file_path, e))?;
        
        heroes.insert(hero.name.clone(), hero);
    }

    Ok(heroes)
}

pub fn load_roles(path: &str) -> Result<RoleRules, Box<dyn Error>> {
    let data = fs::read_to_string(path)?;
    let rules: RoleRules = serde_json::from_str(&data)?;
    Ok(rules)
}

pub fn load_synergies(path: &str) -> Result<SynergyRules, Box<dyn Error>> {
    let data = fs::read_to_string(path)?;
    let rules: SynergyRules = serde_json::from_str(&data)?;
    Ok(rules)
}
