# Captures et annotations

`raw/` et `templates/` sont créés localement et ignorés par Git. Ne pas ajouter
les fichiers du jeu au dépôt. Aucun asset Brotato n'est fourni avec ce laboratoire.

Pour la première expérience, viser un seul objet visible, par exemple le joueur
ou un élément d'interface. Fixer résolution et échelle. Préparer quelques images
de développement, puis **20 autres images positives et 5 négatives** pour l'évaluation.
Les négatives doivent effectivement ne pas contenir l'objet recherché.
Découper le motif dans une image de développement, jamais dans celles d'évaluation.

Conserver un CSV local `data/raw/labels.csv` avec les colonnes :

```csv
image,split,present,x,y,width,height
dev-01.png,dev,true,53,37,7,9
eval-negative-01.png,eval,false,,,,
```

Ces lignes sont des exemples de format, pas des annotations de Brotato.
Les coordonnées partent du coin supérieur gauche de l'image, en pixels.
`split` vaut `dev` ou `eval`. Comparer les boîtes prédites à ces annotations
avec le protocole de `docs/plan.md` ; l'évaluation du jeu n'est pas automatisée ici.
