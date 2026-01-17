use dota2draft::Drafter;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Инициализируем Drafter с загрузкой всех данных
    let drafter = Drafter::new("data/heroes", "data/roles.json", "data/synergies.json")?;

    // Определяем врагов и союзников
    let enemy_team = vec![
        "Anti-Mage".to_string(),
        "Pudge".to_string(),
        "Axe".to_string(),
    ];

    let allies = vec!["Shadow Shaman".to_string()];

    // Получаем рекомендации
    let recommendations = drafter.recommend(enemy_team.clone(), allies.clone(), 10);

    println!("Top picks for your team (Allies: {:?}) vs Enemies {:?}:", allies, enemy_team);
    for rec in recommendations {
        println!("{} (score {})", rec.hero_name, rec.score);
        for reason in rec.reasons {
            println!("  - {}", reason);
        }
    }

    Ok(())
}
