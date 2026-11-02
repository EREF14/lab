//! Q-learning tabulaire : valider la boucle RL sans jeu, GPU ni bibliothèque ML.
use std::error::Error;
use std::fs::{self, File};
use std::io::{BufWriter, Write};
use std::path::Path;
use std::time::Instant;

const STATES: usize = 7;
const MAX_STEPS: usize = 20;
const EVAL_EPISODES: usize = 256;
const EVAL_SEED: u64 = 100_003;
type Model = [[f64; 2]; STATES];

struct Rng(u64);

impl Rng {
    fn next(&mut self) -> u32 {
        self.0 = self
            .0
            .wrapping_mul(6_364_136_223_846_793_005)
            .wrapping_add(1_442_695_040_888_963_407);
        (self.0 >> 32) as u32
    }

    fn unit(&mut self) -> f64 {
        f64::from(self.next()) / (f64::from(u32::MAX) + 1.0)
    }
}

fn greedy(model: &Model, state: usize) -> usize {
    usize::from(model[state][1] > model[state][0])
}

fn step(state: usize, action: usize) -> (usize, f64, bool) {
    let next = if action == 0 { state - 1 } else { state + 1 };
    match next {
        0 => (next, -1.0, true),
        6 => (next, 1.0, true),
        _ => (next, -0.02, false),
    }
}

fn update(model: &mut Model, state: usize, action: usize, next: usize, reward: f64, done: bool) {
    let future = if done {
        0.0
    } else {
        model[next][0].max(model[next][1])
    };
    model[state][action] += 0.2 * (reward + 0.95 * future - model[state][action]);
}

fn train(seed: u64, episodes: usize, history: &mut impl Write) -> std::io::Result<Model> {
    let mut model = [[0.0; 2]; STATES];
    let mut rng = Rng(seed);
    writeln!(history, "episode,return,steps,goal")?;
    for episode in 0..episodes {
        let mut state = 1 + (rng.next() as usize % 5);
        let mut total = 0.0;
        for count in 1..=MAX_STEPS {
            let action = if rng.unit() < 0.3 {
                rng.next() as usize % 2
            } else {
                greedy(&model, state)
            };
            let (next, reward, terminal) = step(state, action);
            // La limite de temps termine aussi cet environnement miniature.
            let done = terminal || count == MAX_STEPS;
            update(&mut model, state, action, next, reward, done);
            total += reward;
            state = next;
            if done {
                writeln!(history, "{episode},{total},{count},{}", state == 6)?;
                break;
            }
        }
    }
    Ok(model)
}

fn evaluate(model: &Model, seed: u64, random: bool) -> f64 {
    let mut rng = Rng(seed);
    let mut wins = 0;
    for episode in 0..EVAL_EPISODES {
        // Les deux politiques sont évaluées sur les mêmes positions de départ.
        let mut state = 1 + episode % 5;
        for _ in 0..MAX_STEPS {
            let action = if random {
                rng.next() as usize % 2
            } else {
                greedy(model, state)
            };
            let (next, _, done) = step(state, action);
            state = next;
            if done {
                wins += usize::from(state == 6);
                break;
            }
        }
    }
    wins as f64 / EVAL_EPISODES as f64
}

fn save(model: &Model, path: &Path) -> Result<(), Box<dyn Error>> {
    let mut output = BufWriter::new(File::create(path)?);
    writeln!(output, "state,left,right")?;
    for (state, values) in model.iter().enumerate() {
        writeln!(output, "{state},{},{}", values[0], values[1])?;
    }
    output.flush()?;
    Ok(())
}

fn load(path: &Path) -> Result<Model, Box<dyn Error>> {
    let text = fs::read_to_string(path)?;
    let lines: Vec<_> = text.lines().collect();
    if lines.len() != STATES + 1 || lines[0] != "state,left,right" {
        return Err("Format de modèle invalide".into());
    }
    let mut model = [[0.0; 2]; STATES];
    for (state, line) in lines[1..].iter().enumerate() {
        let fields: Vec<_> = line.split(',').collect();
        if fields.len() != 3 || fields[0].parse::<usize>()? != state {
            return Err("Ligne de modèle invalide".into());
        }
        for action in 0..2 {
            let value: f64 = fields[action + 1].parse()?;
            if !value.is_finite() {
                return Err("Valeur non finie dans le modèle".into());
            }
            model[state][action] = value;
        }
    }
    Ok(model)
}

fn main() -> Result<(), Box<dyn Error>> {
    let args: Vec<String> = std::env::args().skip(1).collect();
    match args.first().map(String::as_str) {
        Some("train") if (2..=4).contains(&args.len()) => {
            let output = Path::new(&args[1]);
            let seed = args.get(2).map_or(Ok(7), |value| value.parse::<u64>())?;
            let episodes = args
                .get(3)
                .map_or(Ok(1000), |value| value.parse::<usize>())?;
            if episodes == 0 {
                return Err("Le nombre d'épisodes doit être positif".into());
            }
            fs::create_dir_all(output)?;
            let mut history = BufWriter::new(File::create(output.join("training.csv"))?);
            let started = Instant::now();
            let model = train(seed, episodes, &mut history)?;
            history.flush()?;
            let training_ms = started.elapsed().as_secs_f64() * 1000.0;
            save(&model, &output.join("model.csv"))?;
            let restored = load(&output.join("model.csv"))?;
            let baseline = evaluate(&restored, EVAL_SEED, true);
            let learned = evaluate(&restored, EVAL_SEED, false);
            let passed = learned >= 0.9 && learned - baseline >= 0.2 && restored == model;
            let summary = format!(
                "{{\n  \"seed\": {seed},\n  \"episodes\": {episodes},\n  \"training_ms\": {training_ms},\n  \"eval_seed\": {EVAL_SEED},\n  \"eval_episodes\": {EVAL_EPISODES},\n  \"random_success\": {baseline},\n  \"learned_success\": {learned},\n  \"passed\": {passed}\n}}\n"
            );
            fs::write(output.join("summary.json"), &summary)?;
            print!("{summary}");
            if !passed {
                return Err(
                    "Le seuil de validation du petit environnement n'est pas atteint".into(),
                );
            }
        }
        Some("evaluate") if args.len() == 2 => {
            let model = load(Path::new(&args[1]))?;
            println!("success={}", evaluate(&model, EVAL_SEED, false));
        }
        _ => {
            return Err(
                "Usage : rl_lab train DOSSIER [SEED] [EPISODES] | evaluate MODELE.csv".into(),
            );
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn terminal_reward_does_not_bootstrap() {
        let mut model = [[99.0; 2]; STATES];
        model[5][1] = 0.0;
        update(&mut model, 5, 1, 6, 1.0, true);
        assert!((model[5][1] - 0.2).abs() < 1e-12);
    }

    #[test]
    fn learning_beats_random_and_is_reproducible() {
        for seed in [7, 17, 27] {
            let model = train(seed, 1000, &mut Vec::new()).unwrap();
            assert_eq!(model, train(seed, 1000, &mut Vec::new()).unwrap());
            let learned = evaluate(&model, EVAL_SEED, false);
            assert!(learned >= 0.9);
            assert!(learned - evaluate(&model, EVAL_SEED, true) >= 0.2);
        }
    }

    #[test]
    fn persistence_keeps_values_and_decisions() {
        let path = std::env::temp_dir().join(format!("rl-lab-{}.csv", std::process::id()));
        let model = train(7, 1000, &mut Vec::new()).unwrap();
        save(&model, &path).unwrap();
        let restored = load(&path).unwrap();
        assert_eq!(model, restored);
        assert_eq!(
            evaluate(&model, EVAL_SEED, false),
            evaluate(&restored, EVAL_SEED, false)
        );
        let corrupt = fs::read_to_string(&path)
            .unwrap()
            .replacen("0,0,0", "0,NaN,0", 1);
        fs::write(&path, corrupt).unwrap();
        assert!(load(&path).is_err());
        fs::remove_file(path).unwrap();
    }
}
