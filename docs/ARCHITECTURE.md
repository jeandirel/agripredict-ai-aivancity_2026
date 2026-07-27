# AgriPredict AI — Architecture finale

## 1. Vue d’ensemble

```text
Sources originales
├── Parcelles de blé — données françaises
├── SoilGrids
├── NASA POWER
├── Sentinel-1
├── Sentinel-2
└── Céré'Obs / référence régionale
        │
        ▼
Bronze — jeux bruts immuables et hashés
        │
        ▼
Silver — master_raw_regional / master_raw_derived
        │
        ▼
Gold — master_ml_* / jeux finaux 31 mai et 15 juin
        │
        ▼
Contrôles de schéma, disponibilité temporelle et fuite
        │
        ▼
Développement ancien ─ GroupKFold par parcelle ─ sélection du modèle
        │
        ├── Année N-1 : calibration split-conformal
        └── Année N   : test chronologique final
        │
        ▼
Ablations + robustesse + OOD + explicabilité
        │
        ▼
Modèle de déploiement refitté sur toutes les données
        │
        ├── FastAPI
        ├── Dashboard Streamlit
        └── Docker Compose
```

## 2. Principes d’architecture

- Séparation stricte entre données, préparation, entraînement, évaluation et inférence.
- Aucun identifiant parcellaire utilisé comme variable d’apprentissage.
- Aucune sélection de modèle sur l’année test.
- Calibration des intervalles sur une année distincte.
- Deux horizons indépendants : 31 mai et 15 juin.
- Métadonnées de modèle versionnées avec les artefacts.
- Résultats scientifiques générés automatiquement.
- API sans état et modèles chargés depuis `AGRIPREDICT_MODEL_DIR`.

## 3. Composants

### Données

- `configs/data/datasets.json` : manifeste autoritatif.
- `scripts/download_kaggle_datasets.py` : téléchargement et hashes.
- `scripts/audit_phase0.py` : audit structurel et temporel.
- `src/agripredict/data.py` : garde-fous de préparation.

### Machine Learning

- `src/agripredict/modeling.py` : baselines et MLP compact.
- `src/agripredict/advanced.py` : protocole final, conformal, ablations, robustesse et OOD.
- `scripts/train_models.py` : benchmark initial.
- `scripts/finalize_project.py` : évaluation scientifique et livrables v1.0.0.

### Produit

- `app/api/main.py` : API FastAPI.
- `app/dashboard/app.py` : interface Streamlit.
- `Dockerfile` : image applicative.
- `docker-compose.yml` : API + dashboard.

### Qualité et livraison

- `tests/` : tests unitaires et API.
- `.github/workflows/finalize-project.yml` : pipeline finale.
- `reports/final/` : rapport, Data Card, Model Cards et soutenance.
- `artifacts/models/` : modèles et métadonnées produits par la CI.

## 4. Flux d’inférence

```text
Requête JSON
  │
  ▼
Validation Pydantic
  │
  ▼
Alignement avec feature_columns
  │
  ▼
Imputation + encodage dans la pipeline scikit-learn
  │
  ▼
Prédiction du DOY
  │
  ├── Conversion en date calendaire
  ├── Intervalle prédictif à 90 %
  ├── Diagnostic de couverture des entrées
  └── Avertissements de domaine
```

## 5. Haute disponibilité visée

Le prototype académique est stateless. Une mise en production peut utiliser :

- plusieurs réplicas de l’API derrière un load balancer ;
- stockage objet versionné pour les modèles ;
- rolling deployment ;
- health/readiness probes ;
- logs structurés et monitoring de dérive ;
- cache local des modèles ;
- reprise automatique des conteneurs.

Ces mécanismes sont une architecture cible ; ils ne constituent pas une preuve de disponibilité en production dans la version académique.
