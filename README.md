# AgriPredict AI — aivancity 2026

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](CITATION.cff)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![AI Clinic](https://img.shields.io/badge/aivancity-Clinique%20IA-6f42c1)](docs/project_charter.md)

Projet réalisé dans le cadre de la **Clinique IA d’aivancity — Promotion 2026** par **Jean Direl NZE**.

## Objectif

AgriPredict AI est un système d’intelligence artificielle multimodal destiné à **prédire la date de récolte du blé à l’échelle parcellaire en Centre-Val de Loire**.

Il combine :

- données parcellaires françaises ;
- propriétés du sol issues de SoilGrids ;
- indices optiques Sentinel-2 ;
- rétrodiffusions radar Sentinel-1 ;
- données météorologiques NASA POWER ;
- références agricoles et cible dérivée.

La sortie comprend le **jour de l’année**, la date calendaire, un intervalle prédictif à 90 %, des avertissements de domaine et des explications globales.

## Expérience scientifique centrale

Deux horizons sont comparés sur les mêmes parcelles-années :

- **31 mai** : anticipation maximale ;
- **15 juin** : informations météo et phénologiques enrichies.

Le protocole final empêche la sélection sur le test :

```text
2020–2022 → sélection GroupKFold par ID_PARCEL
2023      → calibration split-conformal
2024      → test final intouché
```

`parcelle_uid` reste la clé parcelle-année. `ID_PARCEL` est l’identifiant physique stable utilisé pour empêcher qu’une même parcelle apparaisse dans plusieurs folds. Tous les identifiants, variables de pic, variables DOY et agrégats AMJ non prouvés sont exclus du modèle officiel.

## Résultats finaux validés

Les deux horizons couvrent **1 363 parcelles-années communes**, avec une cible identique pour l’ensemble des clés alignées.

| Horizon | Modèle sélectionné | MAE | IC95 du MAE | RMSE | R² | Couverture conformale |
|---|---|---:|---|---:|---:|---:|
| 31 mai | Random Forest | 8,493 jours | [7,609 ; 9,363] | 10,356 | 0,105 | 85,9 % |
| 15 juin | Random Forest | 8,294 jours | [7,410 ; 9,205] | 10,212 | 0,130 | 85,3 % |

La différence appariée d’erreur absolue, 15 juin moins 31 mai, est de **−0,199 jour**, avec un IC bootstrap à 95 % de **[−0,492 ; 0,095]**. Le 15 juin est légèrement meilleur en moyenne, mais l’avantage reste **statistiquement non concluant** car l’intervalle recouvre zéro.

Le workflow observable de validation a terminé avec succès : génération finale, tests, Ruff, readiness de l’API et publication de l’artefact.

## Finalisation en une commande

```bash
python -m venv .venv
source .venv/bin/activate  # Windows : .venv\Scripts\activate
make install
make final
```

`make final` génère :

- modèles 31 mai et 15 juin ;
- évaluation chronologique stricte ;
- intervalles split-conformal ;
- comparaison appariée bootstrap ;
- ablations par modalité ;
- robustesse aux données manquantes et au bruit ;
- diagnostic hors domaine ;
- importances par permutation ;
- Data Card et Model Cards ;
- rapport scientifique final ;
- plan de soutenance de 15 diapositives ;
- script de démonstration.

## Lancer l’application

### Local

```bash
make api
make dashboard
```

- API : `http://localhost:8000`
- Documentation OpenAPI : `http://localhost:8000/docs`
- Dashboard : `http://localhost:8501`

### Docker

```bash
make final
docker compose up --build
```

## Architecture du dépôt

```text
configs/data/             manifeste des datasets
src/agripredict/          préparation, modèles et évaluation avancée
scripts/                  téléchargement, audit, entraînement et finalisation
app/api/                  FastAPI
app/dashboard/            Streamlit
reports/modeling/         benchmark initial reproduit
reports/final/            livrables scientifiques v1.0.0
tests/                    tests unitaires et API
.github/workflows/        CI, audit, entraînement et livraison
```

## Documentation

- [Plan expert complet](docs/PLAN_EXPERT_CLINIQUE_IA.md)
- [Matrice de complétion](docs/PHASE_COMPLETION_MATRIX.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Déploiement](docs/DEPLOYMENT.md)
- [Éthique et gouvernance](docs/ETHICS_AND_GOVERNANCE.md)
- [Registre officiel des données](docs/data_sources.md)
- [Charte du projet](docs/project_charter.md)
- [Problématique scientifique](docs/problem_statement.md)
- [Questions de recherche](docs/research_questions.md)
- [Critères de succès](docs/success_metrics.md)
- [Risques et hypothèses](docs/risks_and_assumptions.md)
- [Rapport scientifique final](reports/final/FINAL_REPORT.md)
- [Résumé JSON des métriques finales](reports/final/FINAL_METRICS.json)
- [Data Card](reports/final/DATA_CARD.md)
- [Model Card — 31 mai](reports/final/MODEL_CARD_MAY31.md)
- [Model Card — 15 juin](reports/final/MODEL_CARD_JUNE15.md)
- [Plan de soutenance](reports/final/DEFENSE_15_SLIDES.md)
- [Script de démonstration](reports/final/DEMO_SCRIPT.md)

## Gouvernance scientifique

- La cible `harvest_doy_derived` est dérivée et n’est pas présentée comme une observation terrain directe.
- Les importances sont prédictives, pas causales.
- Le domaine de validité est limité au blé du Centre-Val de Loire.
- La décision finale de récolte reste humaine.
- Une validation agronomique externe est nécessaire avant un usage opérationnel.

## Statut

**Version 1.0.0 — prototype de recherche complet et validé en CI.**

Toutes les phases sont terminées dans le dépôt : cadrage, données, baselines, modèles, validation, ablations, incertitude, explicabilité, robustesse, hors domaine, API, interface, Docker, CI, gouvernance, rapport et soutenance.

## Licence

Le code est distribué sous licence MIT. Les datasets restent soumis aux licences et conditions de leurs fournisseurs d’origine.

## Établissement

**aivancity — École de l’intelligence artificielle et de la data**  
**Clinique IA — Promotion 2026**
