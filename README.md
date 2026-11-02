# lab — Pré-POC Brotato

Trois expériences indépendantes pour vérifier les bases avant de construire
l'agent du projet scolaire : agir sur le jeu, apprendre en Rust, lire une image.
Chaque expérience peut être lancée sans les deux autres.

## Structure

| Chemin | Rôle |
|---|---|
| `experiments/game_io/` | Capture et courte impulsion clavier sous Windows ; simulation par défaut. |
| `experiments/rl/` | Petit environnement et Q-learning tabulaire en Rust, avec sauvegarde. |
| `experiments/vision/` | Recherche d'un motif dans une image ; démonstration synthétique incluse. |
| `data/` | Consignes pour préparer les captures et annotations réelles. |
| `runs/` | Sorties locales générées, ignorées par Git. |
| `docs/plan.md` | Ordre de réalisation, budgets et critères de passage. |
| `docs/results.md` | État des validations et fiche courte pour les essais. |
| `tests/` et `.github/workflows/ci.yml` | Contrôles Python sous Linux/Windows et contrôles Rust. |

## Démarrage

Prérequis : Python **3.11 ou plus récent** et Rust via [rustup](https://rustup.rs/).
Depuis la racine du dépôt, créer un environnement Python :

```sh
python -m venv .venv
```

Dans PowerShell, activer avec `.\.venv\Scripts\Activate.ps1` ; sous Linux,
avec `source .venv/bin/activate`. Sans activation, remplacer `python` par
`.\.venv\Scripts\python.exe` sous Windows ou `.venv/bin/python` sous Linux.

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
cargo test --workspace --locked
```

Les démonstrations suivantes fonctionnent **sans Brotato** :

```sh
python experiments/game_io/probe.py
cargo run --release --locked -p rl_lab -- train runs/rl-7 7 1000
cargo run --release --locked -p rl_lab -- evaluate runs/rl-7/model.csv
python experiments/vision/match.py --demo
```

Le premier appel affiche une simulation sans toucher au clavier. Le second
écrit `training.csv`, `model.csv` et `summary.json`. La vision écrit
`result.json` et `overlay.png`. Utiliser des dossiers de sortie distincts pour
conserver plusieurs essais : une relance dans le même dossier remplace ses sorties.

Pour les vrais essais, suivre les README de [game_io](experiments/game_io/README.md),
[rl](experiments/rl/README.md) et [vision](experiments/vision/README.md), dans cet ordre.
L'envoi de touches et la capture du jeu s'exécutent dans **Windows natif**,
hors WSL et Docker. Les autres expériences peuvent rester dans l'environnement habituel.

## Limites volontaires

- La vision commence avec un seul motif à taille fixe ; sa réussite synthétique
  ne valide pas la détection du personnage animé ou des ennemis de Brotato.
- Le RL utilise une table de valeurs sans dépendance ML. Il vérifie apprentissage,
  évaluation et sauvegarde, pas une bibliothèque de deep RL ni le temps d'entraînement du jeu.
- Le contrôle du jeu n'est pas relié au RL. La boucle complète vient après
  les validations séparées.

Le choix d'un mod, d'une bibliothèque ML et de la représentation visuelle reste ouvert.
Le futur apprentissage des achats et les préférences configurables restent dans le
périmètre du projet ; ce laboratoire ne les considère pas comme réalisés.
