use dota2draft::Drafter;
use serde::{Deserialize, Serialize};
use std::process::Command;
use std::path::Path;
use std::sync::Mutex;
use std::time::SystemTime;
use tauri::{Emitter, Manager, Window};
use std::io::{BufRead, BufReader};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct HeroRecommendation {
    pub hero_name: String,
    pub score: i32,
    pub reasons: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RecommendationResult {
    pub radiant: Vec<HeroRecommendation>,
    pub dire: Vec<HeroRecommendation>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct HeroEntry {
    pub name: String,
    pub primary_attr: String,
    pub positions: std::collections::HashMap<String, f32>,
}

pub struct AppState {
    pub drafter: Option<Drafter>,
}

#[tauri::command]
fn cmd_get_heroes(state: tauri::State<Mutex<AppState>>) -> Result<Vec<HeroEntry>, String> {
    let state = state.lock().map_err(|e| e.to_string())?;
    if let Some(drafter) = &state.drafter {
        let heroes = drafter.get_all_heroes();
        let mut result = heroes.into_iter().map(|h| HeroEntry {
            name: h.name.clone(),
            primary_attr: h.primary_attribute.clone(),
            positions: h.positions.clone(),
        }).collect::<Vec<_>>();
        result.sort_by(|a, b| a.name.cmp(&b.name));
        Ok(result)
    } else {
        Err("Drafter not initialized".to_string())
    }
}

#[tauri::command]
fn cmd_recommend(
    radiant: Vec<String>,
    dire: Vec<String>,
    state: tauri::State<Mutex<AppState>>,
) -> Result<RecommendationResult, String> {
    let state = state.lock().map_err(|e| e.to_string())?;
    
    if let Some(drafter) = &state.drafter {
        // Recommendations for Radiant: Enemies = Dire, Allies = Radiant
        let recs_for_radiant = drafter.recommend(dire.clone(), radiant.clone(), 10);
        
        // Recommendations for Dire: Enemies = Radiant, Allies = Dire
        let recs_for_dire = drafter.recommend(radiant.clone(), dire.clone(), 10);
        
        let result = RecommendationResult {
            radiant: recs_for_radiant
                .into_iter()
                .map(|rec| HeroRecommendation {
                    hero_name: rec.hero_name,
                    score: rec.score,
                    reasons: rec.reasons,
                })
                .collect(),
            dire: recs_for_dire
                .into_iter()
                .map(|rec| HeroRecommendation {
                    hero_name: rec.hero_name,
                    score: rec.score,
                    reasons: rec.reasons,
                })
                .collect(),
        };
        Ok(result)
    } else {
        Err("Drafter not initialized".to_string())
    }
}

#[tauri::command]
fn cmd_check_data_freshness() -> Result<bool, String> {
    let path = Path::new("../data/dota_heroes_stratz.json");
    if !path.exists() {
        return Ok(false);
    }

    let metadata = std::fs::metadata(path).map_err(|e| e.to_string())?;
    let modified = metadata.modified().map_err(|e| e.to_string())?;
    
    let now = SystemTime::now();
    let duration = now.duration_since(modified).map_err(|e| e.to_string())?;

    // 7 days in seconds = 7 * 24 * 60 * 60 = 604800
    Ok(duration.as_secs() < 604800)
}

#[tauri::command]
async fn cmd_update_data(window: Window, api_key: String, max_workers: i32) -> Result<(), String> {
    // Determine the path to Cargo.toml relative to execution
    // Running from src-tauri usually, so root Cargo.toml is ../Cargo.toml
    
    // Using simple std::process::Command to stream output
    // Note: In production this will require the binary to be bundled, 
    // but for this dev environment "cargo run" is fine.
    
    window.emit("update-log", "🚀 Initializing Update Process...").unwrap();
    
    let cwd = std::env::current_dir().unwrap_or_default();
    window.emit("update-log", format!("📂 Working Directory: {:?}", cwd)).unwrap();

    let venv_path = "../.venv/Scripts/python.exe";
    let python_cmd = if Path::new(venv_path).exists() {
        window.emit("update-log", "🐍 Found venv python").unwrap();
        std::fs::canonicalize(venv_path).unwrap_or(std::path::PathBuf::from(venv_path))
    } else {
        window.emit("update-log", "🐍 Using system python").unwrap();
        std::path::PathBuf::from("python")
    };
    
    window.emit("update-log", format!("🔧 Python Path: {:?}", python_cmd)).unwrap();

    let mut child = Command::new(python_cmd)
        .current_dir("../")
        .env("PYTHONIOENCODING", "utf-8")
        .arg("-u") // Unbuffered output
        .args(&["src/stratz_hero_requests.py"])
        .arg(&api_key)
        .arg(max_workers.to_string())
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to start process: {}", e))?;

    let stdout = child.stdout.take().ok_or("Failed to capture stdout")?;
    let stderr = child.stderr.take().ok_or("Failed to capture stderr")?;

    // We need to read streams asynchronously or in separate threads to not block
    // Since we are in async fn, we can spawn threads
    let window_clone = window.clone();
    std::thread::spawn(move || {
        let reader = BufReader::new(stdout);
        for line in reader.lines() {
            if let Ok(l) = line {
                let _ = window_clone.emit("update-log", l);
            }
        }
    });

    let window_clone2 = window.clone();
    std::thread::spawn(move || {
        let reader = BufReader::new(stderr);
        for line in reader.lines() {
            if let Ok(l) = line {
                // Cargo build output usually goes to stderr
                let _ = window_clone2.emit("update-log", l);
            }
        }
    });

    // Wait for completion
    let status = child.wait().map_err(|e| e.to_string())?;
    
    if status.success() {
        window.emit("update-log", "✅ Data Updated Successfully!").unwrap();
        Ok(())
    } else {
        window.emit("update-log", "❌ Update Failed.").unwrap();
        Err("Process exited with error code".into())
    }
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(Mutex::new(AppState { drafter: None }))
        .setup(|app| {
            let mut resource_path = app.path().resolve("data", tauri::path::BaseDirectory::Resource)
                .unwrap_or_else(|_| std::path::PathBuf::from("data"));

            if !resource_path.exists() {
                // Fallback 1: Try ../data (parent dir)
                if let Ok(cwd) = std::env::current_dir() {
                     let candidate = cwd.join("../data");
                     if candidate.exists() {
                         resource_path = candidate;
                     } else {
                         // Fallback 2: Try ./data
                         let candidate_local = cwd.join("data");
                         if candidate_local.exists() {
                             resource_path = candidate_local;
                         }
                     }
                }
            }

            println!("Loading data from: {:?}", resource_path);

            let heroes_path = resource_path.join("heroes");
            let roles_path = resource_path.join("roles.json");
            let synergies_path = resource_path.join("synergies.json");

            let drafter = match Drafter::new(
                heroes_path.to_str().unwrap(),
                roles_path.to_str().unwrap(),
                synergies_path.to_str().unwrap(),
            ) {
                Ok(d) => Some(d),
                Err(e) => {
                    eprintln!("Failed to load Drafter: {}", e);
                    None
                }
            };

            let state = app.state::<Mutex<AppState>>();
            let mut state_guard = state.lock().unwrap();
            state_guard.drafter = drafter;

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![cmd_get_heroes, cmd_recommend, cmd_check_data_freshness, cmd_update_data])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
