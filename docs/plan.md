# Ordre de réalisation et critères de passage

Budget indicatif : **5 à 7 heures de manipulation**, hors installation longue et
calcul supplémentaire. Ces durées sont des limites d'exploration, pas une garantie
de réussite. Si ce travail compte dans les 45 heures scolaires, le déduire du budget
de faisabilité et réviser le planning avant de poursuivre.

| Ordre | Expérience | Budget | Critère de passage | Preuve à conserver |
|---|---|---:|---|---|
| 0 | Préparer l'environnement | 30 min | Démonstrations accessibles ; tests Python et Rust réussis. | Versions de Python/Rust, OS, commit. |
| 1 | Accéder au jeu | 1–1,5 h | Sur une vague préparée manuellement : images avant/après lisibles, chaque direction testée, cinq impulsions consécutives correctes, aucune touche maintenue après arrêt. | PNG, JSON, vérification manuelle et versions du jeu/affichage. |
| 2 | Apprendre en Rust | 1,5–2 h | Pour les seeds 7, 17 et 27 : ≥ 90 % de réussite et ≥ 20 points de mieux que la politique aléatoire, sur 256 épisodes séparés de l'entraînement. Le modèle rechargé donne le même résultat. | CSV, modèle, JSON et durée par seed. |
| 3 | Détecter sur des images | 1,5–2 h | Sur des captures réservées à l'évaluation : précision et rappel ≥ 80 %, boîte correcte si IoU ≥ 0,5. Inclure au moins 20 positifs et 5 négatifs. | Annotations, résultats et surimpressions, durée médiane et maximale. |
| 4 | Faire le bilan | 30–60 min | Chaque étape est marquée validée, bloquée ou à revoir, avec une preuve et une décision. Le coût d'un entraînement réel est estimé. | `docs/results.md` rempli. |

On teste l'accès au jeu en premier car il conditionne la suite. Le RL vient ensuite
sur un environnement minuscule pour apprendre le cycle état → action → récompense
sans attendre des vagues. La vision exploite enfin les captures obtenues à l'étape 1.
Un blocage d'accès au jeu n'empêche pas de travailler sur les démonstrations hors jeu.

## Ce que chaque succès permet de conclure

**Accès au jeu.** Le prototype externe fonctionne pour la configuration testée.
Consigner la résolution, le mode fenêtré, les touches et les temps de capture/commande.
Tester aussi l'arrêt pendant une impulsion. Si l'entrée externe ne fonctionne pas
dans le budget, essayer un mod minimal qui écrit un message dans les logs, avant
toute commande ou lecture de données du jeu. Suivre les liens du README `game_io`.
Le chargement de ce mod ne valide pas encore un pont avec Rust.

**RL.** Un vrai apprentissage et sa persistance fonctionnent en Rust sur ce jouet.
Cela n'établit pas qu'un réseau neuronal sera nécessaire ou performant. Si l'étude
retient un réseau, prévoir ensuite un essai borné de la bibliothèque choisie :
installation, une mise à jour de paramètres, sauvegarde/rechargement et mesure du
temps sur la machine cible. Consigner version, backend CPU/GPU et difficulté rencontrée
avant de l'utiliser dans le projet. Ce choix n'est pas tranché par le présent dépôt.

**Vision.** La recherche d'un motif convient, ou montre ses limites, pour un seul
objet à l'affichage fixé. Choisir le motif sur les images de développement, puis
figer motif et seuil avant l'évaluation. Une détection mal placée compte comme un
faux positif et un faux négatif. Si le seuil échoue, conserver les échecs : animations,
occlusions et changements d'échelle permettront de choisir la méthode suivante.
Ne pas multiplier immédiatement les classes d'ennemis.

## Avant de brancher les expériences

Mesurer sur le vrai jeu au moins cinq essais courts : durée jouée, capture,
décision, commande, durée de relance manuelle, fin d'essai observable et signal de
récompense accessible. La capture enregistrée inclut son encodage PNG ; elle ne
représente donc pas directement le coût d'une future capture en mémoire.

Estimer le temps réel avec `nombre d'épisodes × (durée moyenne + relance)`.
Exemple hypothétique : 1 000 essais de 60 s avec 5 s de relance représentent
environ **18 h**, même si l'algorithme Rust est rapide. Sans accélération du jeu
mesurée, conserver la vitesse réelle dans l'estimation.

Seulement ensuite, essayer une boucle observation → règle simple → action pendant
30 secondes, avec journal des actions et arrêt fiable. Fixer sa cadence d'après les
mesures. Cette boucle doit utiliser l'image pour les informations spatiales de combat.
Les informations structurées d'un éventuel mod pourront aider pour les achats,
récompenses ou relances, sans remplacer la perception visuelle du combat.

L'apprentissage des achats et l'influence des préférences configurables demandent
ensuite leurs propres essais ; ils restent des objectifs distincts du projet final.
