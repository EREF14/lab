# Expérience vision

Question : peut-on retrouver un petit motif dans une image plus grande, avec
une boîte visible et une mesure de temps ? Le programme cherche le meilleur
emplacement par erreur RGB absolue moyenne. Son score n'est pas une probabilité.

```sh
python experiments/vision/match.py --demo
python experiments/vision/match.py --image data/raw/frame.png --template data/templates/player.png --out-dir runs/vision-real
```

Une zone limitée accélère la recherche : ajouter par exemple `--roi 0 0 400 300`
si l'image fait au moins cette taille. Les quatre valeurs sont gauche, haut,
droite, bas en pixels. Les boîtes de sortie restent dans les coordonnées de
l'image complète. Ajuster `--threshold` sur les images de développement seulement.

Inspecter `overlay.png` et `result.json`. Sans détection au-dessus du seuil,
`found` vaut `false` et `bbox` vaut `null`. Le temps concerne la recherche seule.

Cette baseline travaille à taille et apparence fixes, sans gestion des animations,
de la rotation, des transparences ou de plusieurs occurrences. Prendre le motif
dans une capture réelle, avec son fond, et commencer par une petite zone. Une
recherche plein écran avec un grand motif peut être très lente ; la mesurer avant
toute boucle temps réel. Utiliser `data/README.md` pour constituer le jeu d'essai.

Le critère sur données réelles est dans `docs/plan.md`. La démonstration synthétique
ne le remplace pas.
