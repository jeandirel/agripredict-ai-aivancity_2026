# Phase 1 — Exécution accélérée du projet

## Objectif immédiat

Construire aujourd’hui un premier système complet et défendable : audit, baselines, réseau neuronal compact, validation temporelle, validation groupée, API et interface.

## Commande principale

```bash
make install
make reproduce
```

## Garde-fou scientifique

Le pipeline exclut par défaut :

- les identifiants de parcelle utilisés comme features ;
- les variables contenant `peak` ;
- les variables de jour de l’année (`*_doy`) ;
- les agrégats avril-mai-juin (`*_amj_*`).

Ces variables ne doivent être réintroduites qu’après preuve de leur disponibilité à la date de coupure et de leur indépendance vis-à-vis de la construction de `harvest_doy_derived`.

## Benchmark produit

Le script `scripts/train_models.py` compare :

- Dummy médian ;
- Ridge ;
- Random Forest ;
- Extra Trees ;
- HistGradientBoosting ;
- MLP, réseau neuronal compact.

Pour chaque horizon, il publie :

- MAE et RMSE en jours ;
- R² ;
- biais ;
- erreur au 90e percentile ;
- taux à ±3, ±5, ±7 et ±10 jours ;
- MAE en validation groupée par parcelle ;
- importance globale par permutation ;
- intervalle prédictif approximatif fondé sur le 90e percentile des résidus.

## Validation

- Test final : dernière année disponible.
- Validation complémentaire : GroupKFold par `parcelle_uid`.
- Comparaison des horizons : uniquement sur les clés parcelle-année communes.

## Démonstration

```bash
make api
make dashboard
```

API : `http://localhost:8000/docs`  
Interface : `http://localhost:8501`

## Limite assumée

Le premier benchmark est une baseline de qualité et non le résultat scientifique final. La cible dérivée et les variables temporellement sensibles doivent encore être auditées à partir de la pipeline de construction et des rapports méthodologiques.
