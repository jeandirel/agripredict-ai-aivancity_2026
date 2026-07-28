# AgriPredict AI — Benchmark initial

> Généré le `2026-07-28T00:01:12.440176+00:00`.

## Comparaison des horizons

- Parcelles-années communes : **1363**
- Cibles différentes : **0**

## Résultats temporels

| Horizon | Année test | Modèle | MAE | RMSE | R² | ±5 jours | ±7 jours | CV groupé MAE |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| may31 | 2024 | ridge | 8.508 | 10.639 | 0.056 | 36.2% | 47.9% | 6.050 |
| june15 | 2024 | extra_trees | 8.464 | 10.321 | 0.112 | 25.2% | 49.1% | 5.932 |

## Règle de lecture

Ces résultats utilisent un filtre conservateur qui exclut les variables de pic, de jour de l’année et les agrégats AMJ tant que leur disponibilité à la date de coupure et leur indépendance vis-à-vis de la cible ne sont pas démontrées.
