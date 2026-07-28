# Model Card — AgriPredict AI june15

## Identification

- Version : `1.0.0`
- Horizon : `june15`
- Modèle : `random_forest`
- Tâche : régression de la date de récolte du blé
- Sortie : jour de l’année
- Domaine : Centre-Val de Loire

## Sélection et validation

- Années de développement : [2020, 2021, 2022]
- Année de calibration : 2023
- Année de test : 2024
- Sélection : GroupKFold par parcelle, sans consultation du test

## Performance sur le test chronologique

- MAE : 8.337 jours
- RMSE : 10.226 jours
- R² : 0.128
- Prédictions à ±5 jours : 30.1%
- Prédictions à ±7 jours : 46.6%
- IC bootstrap 95 % du MAE : [7.475; 9.250]

## Incertitude

- Méthode : split-conformal
- Couverture nominale : 90 %
- Couverture observée : 85.3%
- Largeur moyenne : 29.71 jours

## Usage prévu

Aide à la planification logistique et à l’analyse expérimentale. Le modèle ne déclenche aucune récolte automatiquement.

## Usages interdits ou non validés

- autre culture ;
- autre région sans validation externe ;
- décision de récolte autonome ;
- interprétation causale des importances ;
- présentation de la cible dérivée comme une observation terrain directe.

## Données et risques

Les identifiants, variables de pic, variables DOY et agrégats AMJ à risque sont exclus du modèle officiel. Les détails figurent dans `metadata.json` et le rapport final.
