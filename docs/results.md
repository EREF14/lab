# Résultats du laboratoire

## État initial de la structure — 2 novembre 2026

| Élément | État | Portée |
|---|---|---|
| Vision synthétique | Vérifiée localement | Motif retrouvé en `[53, 37, 7, 9]` ; absence et zone de recherche contrôlées. |
| Commande du jeu en simulation | Vérifiée localement | Aucune entrée émise ; durée bornée et libération de touche testées avec des doublures. |
| Structure Win32 et tests Rust | Voir la CI du commit | La CI vérifie Linux/Windows pour Python et compilation/tests pour Rust. |
| Déplacement et captures de Brotato | À réaliser sur le PC cible | Aucun test réel du jeu effectué lors de la mise en place. |
| Vision sur captures de Brotato | À réaliser | Aucune capture du jeu fournie ; le test synthétique n'est pas ce critère. |
| Bibliothèque de deep RL, mod et boucle complète | À étudier | Aucune intégration ni performance revendiquée. |

## Fiche à dupliquer après chaque essai utile

```text
Date et expérience :
Question testée :
Commit / commande exacte / seed :
OS, matériel, versions Python et Rust :
Version du jeu, résolution, mode d'affichage, touches :
Données et séparation développement/évaluation :
Dossier runs/ conservé :
Mesures (durée, réussite, erreurs, relance) :
Critère du plan atteint : oui / non / non mesuré
Ce que le résultat démontre et ce qu'il ne démontre pas :
Décision : continuer / modifier / abandonner cette approche
Prochain essai limité dans le temps :
```

Les fichiers de `runs/` restent locaux. Reporter ici quelques mesures et leurs
conditions, puis conserver les sorties utiles séparément si elles servent de preuve.
Ne pas marquer une étape réelle validée sur la seule réussite des tests automatiques.
