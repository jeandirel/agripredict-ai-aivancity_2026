# AgriPredict AI — aivancity 2026

Projet réalisé dans le cadre de la **Clinique IA d’aivancity — Promotion 2026**.

## Objectif

AgriPredict AI est un système d’intelligence artificielle multimodal destiné à **prédire la date de récolte du blé à l’échelle parcellaire en Centre-Val de Loire**.

Le projet combine :

- données parcellaires françaises ;
- propriétés du sol issues de SoilGrids ;
- indices optiques Sentinel-2 ;
- rétrodiffusions radar Sentinel-1 ;
- données météorologiques NASA POWER ;
- références agricoles et cibles dérivées.

La sortie principale est une estimation du **jour de l’année de la récolte**, accompagnée d’un intervalle d’incertitude en jours et d’explications.

## Expérience scientifique principale

Deux horizons sont comparés :

- **31 mai** : prévision plus précoce ;
- **15 juin** : prévision enrichie avec davantage d’informations.

Le projet mesure le compromis entre **anticipation et précision**, sous validation temporelle et séparation stricte des parcelles.

## Datasets

Les données officielles sont répertoriées dans :

- [Registre officiel des données](docs/data_sources.md)
- [Charte du projet](docs/project_charter.md)
- [Problématique scientifique](docs/problem_statement.md)
- [Questions de recherche](docs/research_questions.md)
- [Critères de succès](docs/success_metrics.md)
- [Risques et hypothèses](docs/risks_and_assumptions.md)

Fichiers finaux déjà présents :

```text
data/
├── master_ml_final_may31.csv
└── master_ml_final_june15.csv
```

## Modèles envisagés

### Baselines et modèles d’arbres

- régression linéaire, Ridge et ElasticNet ;
- Random Forest et Extra Trees ;
- XGBoost et CatBoost.

### Réseaux neuronaux tabulaires

- MLP régularisé ;
- TabNet ;
- FT-Transformer compact comme extension contrôlée.

Les réseaux lourds ne sont pas retenus par défaut : leur utilité doit être démontrée face aux modèles d’arbres sur les données réellement disponibles.

## Qualité scientifique

Le projet inclut :

- audit de la cible `harvest_doy_derived` ;
- contrôle des fuites temporelles et de cible ;
- comparaison 31 mai / 15 juin ;
- étude d’ablation des modalités ;
- validation sur année future ;
- validation groupée par `parcelle_uid` ;
- estimation d’incertitude ;
- explicabilité et analyse d’erreurs ;
- tests, DVC, MLflow, FastAPI, Docker et GitHub Actions.

## Feuille de route

➡️ [Consulter le plan expert de réalisation](docs/PLAN_EXPERT_CLINIQUE_IA.md)

## Statut

Phase 0 en cours : cadrage corrigé, sources officielles enregistrées, audit programmatique et validation de la cible à réaliser.

## Établissement

**aivancity — École de l’intelligence artificielle et de la data**  
**Clinique IA — Promotion 2026**
