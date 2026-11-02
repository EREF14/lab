# Expérience d'accès au jeu

Question : peut-on capturer la zone du jeu et lui envoyer une seule direction,
puis vérifier ce qu'il s'est passé ? Commencer sans RL ni vision automatique.

```sh
python experiments/game_io/probe.py
```

Ce mode affiche l'action prévue et ne touche ni au clavier ni à l'écran.
Pour l'essai réel, lancer **Python sous Windows natif**, préparer une vague
manuellement dans Brotato, avec les flèches configurées pour le déplacement :

```sh
python experiments/game_io/probe.py --live --direction right --seconds 0.2 --out-dir runs/game-right-01
```

Pendant le délai de trois secondes, placer la fenêtre Brotato au premier plan et
relâcher les touches. Le script capture sa zone cliente, envoie une impulsion
de 0,2 s puis capture à nouveau. La durée maximale acceptée est 0,5 s.
Répéter avec `left`, `up`, `down` et des dossiers différents. Essayer aussi
une interruption avec Ctrl+C et une perte de focus. La libération est dans un
bloc `finally` ; elle n'est pas garantie en cas de fermeture forcée du processus.

Comparer `before.png` et `after.png`, puis noter le déplacement réellement observé.
Le JSON ne revendique pas cette vérification : `movement_verified` reste `false`
jusqu'à l'examen humain, à consigner dans `docs/results.md`.
`capture_before_ms` et `capture_after_ms` incluent l'encodage et l'écriture PNG.
`elapsed_ms` mesure l'impulsion avec ses contrôles de focus, pas la latence
interne du jeu. Un retour positif de SendInput ne prouve pas que le jeu a bougé.

Si une capture est noire, commencer par un mode fenêtré. Vérifier le focus,
les contrôles du jeu et que les deux programmes ont le même niveau de droits.
Le script ne change pas automatiquement de fenêtre. Aucun essai réel de Brotato
n'a été fait dans l'environnement qui a préparé le dépôt.

## Petit essai de mod, si nécessaire

Pour apprendre le chargement d'un mod, ou si l'entrée externe bloque, limiter le
premier essai à un message dans les logs. Utiliser un dossier `EREF14-Lab` contenant
`manifest.json` et `mod_main.gd`, dont le corps minimal est :

```gdscript
extends Node

func _init():
    print("[EREF14-Lab] mod chargé")
```

Créer le manifeste et l'archive selon la version du ModLoader embarquée dans
le jeu, avec sa documentation. Ne pas recopier une ancienne version de
compatibilité au hasard. Conserver ici uniquement ses propres fichiers ; le
projet du jeu n'est pas à ajouter au dépôt. Le critère de cet essai est le message
visible dans les logs, pas encore un accès aux positions ou une connexion Rust.

Sources : [SendInput (Microsoft)](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-sendinput),
[capture Pillow](https://pillow.readthedocs.io/en/stable/reference/ImageGrab.html),
[fichiers d'un mod](https://wiki.godotmodding.com/guides/modding/mod_files/),
[structure et ZIP du ModLoader](https://wiki.godotmodding.com/guides/modding/mod_structure/).
