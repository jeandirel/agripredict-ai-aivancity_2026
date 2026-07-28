# AgriPredict AI — Rapport scientifique final

> **Clinique IA d’aivancity — Promotion 2026**  
> **Responsable : Jean Direl NZE**  
> **Version : 1.0.0 — générée le 2026-07-28T00:32:35.240861+00:00**

## Résumé exécutif

AgriPredict AI étudie la prévision de la date de récolte du blé à l’échelle parcellaire en Centre-Val de Loire à partir de données de sol, Sentinel-1, Sentinel-2 et NASA POWER. Deux horizons sont comparés : le 31 mai et le 15 juin. Le protocole final sépare les années de développement, une année de calibration et la dernière année comme test intouché. La sélection des modèles est réalisée uniquement par validation groupée sur les parcelles des années de développement.

## Résultats principaux

| Horizon | Modèle sélectionné | Année test | MAE | IC95 MAE | RMSE | R² | ±5 j | ±7 j | Couverture 90 % | Largeur intervalle |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| may31 | random_forest | 2024 | 8.493 j | [7.609; 9.363] | 10.356 | 0.105 | 25.2% | 52.8% | 85.9% | 31.17 j |
| june15 | random_forest | 2024 | 8.294 j | [7.410; 9.205] | 10.212 | 0.130 | 32.5% | 44.2% | 85.3% | 29.46 j |

## Comparaison appariée des horizons

- Différence moyenne d’erreur absolue, 15 juin moins 31 mai : **-0.199 jour**.
- Intervalle bootstrap à 95 % : **[-0.492; 0.095]**.
- Probabilité bootstrap que le 15 juin ait une erreur plus faible : **90.6%**.
- Conclusion statistique : **inconclusive**.

## Protocole anti-fuite

- La dernière année est réservée au test final.
- L’avant-dernière année sert uniquement à la calibration des intervalles.
- La sélection du modèle utilise GroupKFold par `ID_PARCEL` sur les années antérieures.
- Les identifiants de parcelle, variables de pic, variables DOY et agrégats AMJ non prouvés sont exclus.
- Une analyse séparée mesure l’effet des variables à risque, sans les rendre déployables.

## Fusion multimodale et ablations

### Horizon may31

| Configuration | Variables | MAE | RMSE | R² |
|---|---:|---:|---:|---:|
| all_modalities | 67 | 8.749 | 10.904 | 0.008 |
| satellite_weather | 37 | 8.843 | 10.848 | 0.019 |
| soil_weather | 41 | 8.881 | 11.517 | -0.106 |
| soil | 33 | 9.294 | 12.049 | -0.211 |
| satellite_soil | 59 | 9.492 | 11.927 | -0.186 |
| satellite | 29 | 9.551 | 11.791 | -0.160 |
| sentinel1 | 20 | 9.555 | 12.081 | -0.217 |
| weather | 11 | 9.648 | 11.944 | -0.190 |
| sentinel2 | 12 | 9.698 | 12.024 | -0.206 |
| context_only | 3 | 10.825 | 13.616 | -0.546 |

### Horizon june15

| Configuration | Variables | MAE | RMSE | R² |
|---|---:|---:|---:|---:|
| satellite_weather | 42 | 8.429 | 10.386 | 0.100 |
| all_modalities | 72 | 8.457 | 10.368 | 0.103 |
| soil_weather | 46 | 8.598 | 10.647 | 0.054 |
| weather | 16 | 9.293 | 11.107 | -0.029 |
| soil | 33 | 9.294 | 12.049 | -0.211 |
| satellite_soil | 59 | 9.492 | 11.927 | -0.186 |
| satellite | 29 | 9.551 | 11.791 | -0.160 |
| sentinel1 | 20 | 9.555 | 12.081 | -0.217 |
| sentinel2 | 12 | 9.698 | 12.024 | -0.206 |
| context_only | 3 | 10.825 | 13.616 | -0.546 |

## Incertitude

Les intervalles sont produits par split-conformal prediction. La largeur et la couverture réelles sont rapportées pour le test final. Une couverture proche de 90 % est souhaitée, mais ne garantit pas automatiquement une validité sur une autre région ou un autre régime climatique.

## Robustesse

### Horizon may31

| Scénario | MAE | Δ MAE | Variation relative |
|---|---:|---:|---:|
| baseline | 8.493 | 0.000 | 0.0% |
| numeric_missing_10pct | 8.568 | 0.075 | 0.9% |
| numeric_noise_5pct_std | 8.490 | -0.003 | -0.0% |
| missing_soil | 8.968 | 0.475 | 5.6% |
| missing_sentinel1 | 8.461 | -0.032 | -0.4% |
| missing_sentinel2 | 8.580 | 0.088 | 1.0% |
| missing_weather | 8.841 | 0.348 | 4.1% |

### Horizon june15

| Scénario | MAE | Δ MAE | Variation relative |
|---|---:|---:|---:|
| baseline | 8.294 | 0.000 | 0.0% |
| numeric_missing_10pct | 8.373 | 0.079 | 0.9% |
| numeric_noise_5pct_std | 8.325 | 0.031 | 0.4% |
| missing_soil | 8.556 | 0.262 | 3.2% |
| missing_sentinel1 | 8.401 | 0.107 | 1.3% |
| missing_sentinel2 | 8.329 | 0.035 | 0.4% |
| missing_weather | 8.870 | 0.576 | 6.9% |

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
