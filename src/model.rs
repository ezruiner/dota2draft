use std::collections::HashMap;
use serde::Deserialize;

#[derive(Debug, Deserialize)]
pub struct Hero {
    pub name: String,
    pub primary_attribute: String,
    pub roles: Vec<String>,
    pub tags: Vec<String>,
    pub positions: HashMap<String, f32>,
    pub game_phase: GamePhase,
    pub explicit_counters: HashMap<String, f32>,
    pub explicit_synergies: HashMap<String, f32>,
}

#[derive(Debug, Deserialize)]
pub struct GamePhase {
    pub early: i32,
    pub mid: i32,
    pub late: i32,
}

#[derive(Debug, Deserialize)]
pub struct RoleRules {
    pub role_conflicts: HashMap<String, i32>,
    pub role_synergies: HashMap<String, i32>,
}

#[derive(Debug, Deserialize)]
pub struct SynergyRules {
    pub tag_synergies: HashMap<String, i32>,
    pub tag_counters: HashMap<String, i32>,
    #[serde(default)]
    pub phase_bias: HashMap<String, HashMap<String, i32>>,
}
