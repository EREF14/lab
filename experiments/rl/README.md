# Expérience RL en Rust

Question : peut-on entraîner, comparer, sauvegarder et réutiliser une politique
depuis Rust sans dépendre du jeu ?

Le petit environnement contient sept cases. Les cases 0 et 6 sont terminales,
avec des récompenses respectives de −1 et +1. Un pas coûte 0,02. Le départ varie
entre les cases 1 à 5 ; l'épisode s'arrête au plus tard après 20 actions.
L'agent apprend une table de valeurs état/action par Q-learning :
`Q ← Q + 0,2 × (récompense + 0,95 × max(Q_suivant) − Q)`.
À la fin d'un épisode, le terme futur est nul. L'exploration choisit une action
aléatoire dans 30 % des décisions d'entraînement ; l'évaluation est sans exploration.

Depuis la racine du dépôt :

```sh
cargo run --release --locked -p rl_lab -- train runs/rl-7 7 1000
cargo run --release --locked -p rl_lab -- train runs/rl-17 17 1000
cargo run --release --locked -p rl_lab -- train runs/rl-27 27 1000
cargo run --release --locked -p rl_lab -- evaluate runs/rl-7/model.csv
cargo test --workspace --locked
```

Arguments de `train` : dossier, seed optionnelle (7), épisodes optionnels (1 000).
Chaque entraînement écrit les épisodes dans `training.csv`, la table dans
`model.csv` et la comparaison dans `summary.json`. Un échec du critère provoque
un code de sortie non nul après l'écriture des résultats. La commande `evaluate`
recharge seulement le modèle, sans l'entraîner à nouveau.

L'évaluation utilise 256 nouveaux épisodes et une seed distincte (100 003) pour
la politique aléatoire, avec les mêmes départs pour les deux politiques. Ici les
transitions sont déterministes ; les seeds d'entraînement changent l'exploration.
Le critère est ≥ 90 % de réussite et un gain ≥ 20 points sur l'aléatoire.
Il reste propre à ce jouet et ne mesure aucune performance dans Brotato.

Le temps `training_ms` exclut compilation et évaluation. Le code n'utilise aucune
bibliothèque ML : il ne valide ni autograd, ni GPU, ni intégration d'un framework
de deep RL. L'essai d'un éventuel backend est une décision ultérieure du plan.
Les choix d'achat ne sont pas modélisés ici ; ils restent à apprendre dans le projet.

Référence de l'algorithme : Sutton et Barto,
[Reinforcement Learning, seconde édition, §6.5](https://mitpress.ublish.com/book/reinforcement-learning-an-introduction-2).
