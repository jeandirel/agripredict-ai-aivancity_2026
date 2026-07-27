# AgriPredict AI — Audit automatisé de Phase 0

> Généré le `2026-07-27T23:50:22.249086+00:00`.

## Décision G0 : `PHASE_0_COMPLETE_WITH_PHASE_2_PREREQUISITES`

### Points de vigilance

- may31: 4 peak/DOY or AMJ columns require lineage review
- june15: 15 peak/DOY or AMJ columns require lineage review
- Manual prerequisite: validate the derivation of harvest_doy_derived from the methodological report/code.

## Synthèse des datasets

| Dataset | Lignes | Colonnes | Années | Parcelles | Cible min–max | Manquants | Doublons clé | SHA-256 |
|---|---:|---:|---|---:|---|---:|---:|---|
| may31 | 1363 | 74 | 2020, 2021, 2022, 2023, 2024 | 1363 | 165.0–217.0 | 0 | 0 | `e38c03a6b095…` |
| june15 | 1363 | 90 | 2020, 2021, 2022, 2023, 2024 | 1363 | 165.0–217.0 | 0 | 0 | `7e46f8dd44a2…` |

## Comparaison 31 mai / 15 juin

- Colonnes communes : **74**
- Colonnes uniquement au 31 mai : `[]`
- Colonnes uniquement au 15 juin : `['meteo_dry_streak_max', 'meteo_et0_amj_sum', 'meteo_gdd_amj', 'meteo_heat_stress_days', 'meteo_precip_amj_n_days', 'meteo_precip_amj_sum', 'meteo_radiation_amj_sum', 'meteo_t_amj_max', 'meteo_t_amj_mean', 'meteo_t_amj_min', 'meteo_t_amj_std', 'meteo_wb_amj', 'meteo_wet_streak_max', 's2_ndwi_peak_doy', 's2_peak_doy', 's2_peak_evi']`
- Clés communes : **1363**
- Clés uniquement au 31 mai : **0**
- Clés uniquement au 15 juin : **0**
- Cibles différentes sur clés communes : **0**

## Règles scientifiques actées

- Le MAE en jours est la métrique principale.
- La comparaison des horizons utilise uniquement les parcelles-années communes et les mêmes splits.
- Le test final est chronologique.
- Une validation groupée par `parcelle_uid` est obligatoire.
- Les colonnes de pics, de DOY et d’agrégats AMJ restent interdites au modèle final tant que leur fenêtre de calcul n’est pas prouvée.
- La cible dérivée doit être décrite comme telle dans la Data Card et la Model Card.

## Fichiers de preuve

- `reports/phase0/phase0_data_audit.json`
- `reports/phase0/feature_availability_register.csv`
- `configs/data/datasets.json`
- `data/manifests/datasets_download_status.json` lorsque le téléchargement Kaggle a été exécuté.
