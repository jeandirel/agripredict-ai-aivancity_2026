# AgriPredict AI — Rapport scientifique final

> **Clinique IA d’aivancity — Promotion 2026**  
> **Responsable : Jean Direl NZE**  
> **Version : 1.0.0 — générée le 2026-07-28T11:00:32.780702+00:00**

## Résumé exécutif

AgriPredict AI étudie la prévision de la date de récolte du blé à l’échelle parcellaire en Centre-Val de Loire à partir de données de sol, Sentinel-1, Sentinel-2 et NASA POWER. Deux horizons sont comparés : le 31 mai et le 15 juin. Le protocole final sépare les années de développement, une année de calibration et la dernière année comme test intouché. La sélection des modèles est réalisée uniquement par validation groupée sur les parcelles des années de développement.

## Résultats principaux

| Horizon | Modèle sélectionné | Année test | MAE | IC95 MAE | RMSE | R² | ±5 j | ±7 j | Couverture 90 % | Largeur intervalle |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| may31 | random_forest | 2024 | 8.504 j | [7.608; 9.368] | 10.343 | 0.108 | 24.5% | 50.3% | 85.9% | 30.92 j |
| june15 | random_forest | 2024 | 8.337 j | [7.475; 9.250] | 10.226 | 0.128 | 30.1% | 46.6% | 85.3% | 29.71 j |

## Comparaison appariée des horizons

- Différence moyenne d’erreur absolue, 15 juin moins 31 mai : **-0.166 jour**.
- Intervalle bootstrap à 95 % : **[-0.401; 0.076]**.
- Probabilité bootstrap que le 15 juin ait une erreur plus faible : **91.2%**.
- Conclusion statistique : **inconclusive**.

## Protocole anti-fuite

- La dernière année est réservée au test final.
- L’avant-dernière année sert uniquement à la calibration des intervalles.
- La sélection du modèle utilise GroupKFold par `parcelle_uid` sur les années antérieures.
- Les identifiants de parcelle, variables de pic, variables DOY et agrégats AMJ non prouvés sont exclus.
- Une analyse séparée mesure l’effet des variables à risque, sans les rendre déployables.

## Fusion multimodale et ablations

### Horizon may31

| Configuration | Variables | MAE | RMSE | R² |
|---|---:|---:|---:|---:|
| all_modalities | 67 | 8.816 | 10.967 | -0.003 |
| satellite_weather | 37 | 8.865 | 10.836 | 0.021 |
| soil_weather | 41 | 8.897 | 11.526 | -0.108 |
| soil | 33 | 9.315 | 11.991 | -0.199 |
| satellite_soil | 59 | 9.392 | 11.784 | -0.158 |
| satellite | 29 | 9.468 | 11.696 | -0.141 |
| sentinel1 | 20 | 9.548 | 12.050 | -0.211 |
| weather | 11 | 9.653 | 11.962 | -0.193 |
| sentinel2 | 12 | 9.706 | 12.020 | -0.205 |
| context_only | 3 | 10.821 | 13.618 | -0.547 |

### Horizon june15

| Configuration | Variables | MAE | RMSE | R² |
|---|---:|---:|---:|---:|
| satellite_weather | 42 | 8.400 | 10.333 | 0.109 |
| all_modalities | 72 | 8.455 | 10.384 | 0.101 |
| soil_weather | 46 | 8.611 | 10.667 | 0.051 |
| weather | 16 | 9.307 | 11.140 | -0.035 |
| soil | 33 | 9.315 | 11.991 | -0.199 |
| satellite_soil | 59 | 9.392 | 11.784 | -0.158 |
| satellite | 29 | 9.468 | 11.696 | -0.141 |
| sentinel1 | 20 | 9.548 | 12.050 | -0.211 |
| sentinel2 | 12 | 9.706 | 12.020 | -0.205 |
| context_only | 3 | 10.821 | 13.618 | -0.547 |

## Incertitude

Les intervalles sont produits par split-conformal prediction. La largeur et la couverture réelles sont rapportées pour le test final. Une couverture proche de 90 % est souhaitée, mais ne garantit pas automatiquement une validité sur une autre région ou un autre régime climatique.

## Robustesse

### Horizon may31

| Scénario | MAE | Δ MAE | Variation relative |
|---|---:|---:|---:|
| baseline | 8.504 | 0.000 | 0.0% |
| numeric_missing_10pct | 8.580 | 0.076 | 0.9% |
| numeric_noise_5pct_std | 8.498 | -0.005 | -0.1% |
| missing_soil | 8.903 | 0.400 | 4.7% |
| missing_sentinel1 | 8.489 | -0.015 | -0.2% |
| missing_sentinel2 | 8.598 | 0.094 | 1.1% |
| missing_weather | 8.808 | 0.304 | 3.6% |

### Horizon june15

| Scénario | MAE | Δ MAE | Variation relative |
|---|---:|---:|---:|
| baseline | 8.337 | 0.000 | 0.0% |
| numeric_missing_10pct | 8.419 | 0.082 | 1.0% |
| numeric_noise_5pct_std | 8.355 | 0.018 | 0.2% |
| missing_soil | 8.586 | 0.249 | 3.0% |
| missing_sentinel1 | 8.407 | 0.070 | 0.8% |
| missing_sentinel2 | 8.425 | 0.088 | 1.1% |
| missing_weather | 8.861 | 0.524 | 6.3% |

## Explicabilité

Les importances par permutation mesurent une association prédictive sur le test chronologique. Elles ne prouvent aucune causalité agronomique. Les métadonnées de chaque horizon contiennent les 25 variables principales et leur variabilité.

## Gouvernance et éthique

- Le modèle est une aide à la planification, pas une prescription autonome.
- Le domaine de validité est limité au blé du Centre-Val de Loire.
- La cible `harvest_doy_derived` est explicitement présentée comme dérivée.
- Les licences et conditions des sources originales doivent rester jointes au registre de données.
- Les prédictions hors domaine doivent être signalées.
- La décision finale de récolte reste humaine et dépend du terrain, de la météo et de contraintes opérationnelles absentes du modèle.

## Limites

1. absence de vérité terrain parcellaire directe confirmée pour la cible dérivée ;
2. région unique ;
3. nombre d’années limité ;
4. variables déjà agrégées, ne permettant pas d’exploiter directement CNN ou Vision Transformers ;
5. performance susceptible de dériver lors d’années climatiques atypiques ;
6. bénéfice métier du délai d’anticipation à valider avec un agronome ou une coopérative.

## Conclusion

Le projet livre une chaîne reproductible allant des données à l’API, avec validation temporelle, séparation des parcelles, comparaison d’horizons, incertitude, ablations, robustesse, explicabilité, détection hors domaine et documentation de gouvernance. Les scores doivent être lus comme ceux d’un prototype de recherche responsable, et non comme une validation agronomique définitive.
