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
Années anciennes → sélection GroupKFold par parcelle
Avant-dernière année → calibration split-conformal
Dernière année → test final intouché
```

Les identifiants parcellaires, variables de pic, variables DOY et agrégats AMJ non prouvés sont exclus du modèle officiel.

## Résultats déjà reproduits

Le benchmark initial automatisé couvre **1 363 parcelles-années communes** et confirme que la cible est identique entre les deux horizons. Sur l’année 2024, le benchmark conservateur obtient :

| Horizon | Modèle du benchmark initial | MAE | RMSE | R² |
|---|---|---:|---:|---:|
| 31 mai | Ridge | 8,51 jours | 10,64 | 0,056 |
| 15 juin | Extra Trees | 8,46 jours | 10,32 | 0,112 |

Ces chiffres constituent un benchmark initial. Le pipeline v1.0.0 produit ensuite une évaluation plus stricte avec sélection sans test, intervalles conformes, bootstrap, ablations, robustesse et OOD.

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
- [Architecture](docs/ARCHITECTURE.md)
- [Déploiement](docs/DEPLOYMENT.md)
- [Éthique et gouvernance](docs/ETHICS_AND_GOVERNANCE.md)
- [Registre officiel des données](docs/data_sources.md)
- [Charte du projet](docs/project_charter.md)
- [Problématique scientifique](docs/problem_statement.md)
- [Questions de recherche](docs/research_questions.md)
- [Critères de succès](docs/success_metrics.md)
- [Risques et hypothèses](docs/risks_and_assumptions.md)
- [Rapport final généré](reports/final/FINAL_REPORT.md)
- [Data Card générée](reports/final/DATA_CARD.md)
- [Plan de soutenance généré](reports/final/DEFENSE_15_SLIDES.md)

## Gouvernance scientifique

- La cible `harvest_doy_derived` est dérivée et n’est pas présentée comme une observation terrain directe.
- Les importances sont prédictives, pas causales.
- Le domaine de validité est limité au blé du Centre-Val de Loire.
- La décision finale de récolte reste humaine.
- Une validation agronomique externe est nécessaire avant un usage opérationnel.

## Statut

**Version 1.0.0 — prototype de recherche complet.**

Toutes les phases sont implémentées dans le dépôt : cadrage, données, baselines, modèles, validation, ablations, incertitude, explicabilité, robustesse, API, interface, Docker, CI, gouvernance, rapport et soutenance.

## Licence

Le code est distribué sous licence MIT. Les datasets restent soumis aux licences et conditions de leurs fournisseurs d’origine.

## Établissement

**aivancity — École de l’intelligence artificielle et de la data**  
**Clinique IA — Promotion 2026**
