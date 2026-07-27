# AgriPredict AI — Problématique scientifique

> **Cadre :** Clinique IA d’aivancity — Promotion 2026  
> **Version :** 2.0  
> **Statut :** aligné sur les datasets officiels

## 1. Contexte

La date de récolte du blé dépend d’interactions complexes entre la phénologie de la culture, la météo, les propriétés du sol, l’état hydrique, la dynamique du couvert végétal et les conditions propres à chaque parcelle.

Une estimation suffisamment précoce peut aider à préparer :

- la mobilisation des machines ;
- l’organisation des équipes ;
- la logistique de collecte et de stockage ;
- la planification des interventions ;
- l’anticipation des écarts liés aux conditions climatiques.

Les données disponibles pour AgriPredict AI réunissent plusieurs modalités complémentaires :

- informations parcellaires françaises ;
- propriétés de sol issues de SoilGrids ;
- indices optiques Sentinel-2 ;
- rétrodiffusions radar Sentinel-1 ;
- variables météorologiques NASA POWER ;
- références Céré'Obs ;
- tables combinées et jeux ML arrêtés au 31 mai ou au 15 juin.

## 2. Problème métier

Le besoin central est de répondre à la question suivante :

> **À quelle date une parcelle de blé du Centre-Val de Loire sera-t-elle probablement récoltée, en utilisant uniquement les informations disponibles jusqu’à une date de coupure donnée ?**

Le système doit produire une estimation compréhensible, accompagnée d’un intervalle d’incertitude et d’un avertissement lorsque la parcelle est éloignée du domaine d’entraînement.

## 3. Problème scientifique principal

> **Comment concevoir et évaluer un modèle d’intelligence artificielle multimodal capable de prévoir le jour de récolte du blé à l’échelle parcellaire à partir de données de sol, Sentinel-1, Sentinel-2 et météo, tout en quantifiant le compromis entre précocité de la prévision, précision, généralisation temporelle, explicabilité et incertitude ?**

## 4. Originalité de l’étude

L’originalité principale repose sur une comparaison contrôlée entre deux dates de coupure :

- **31 mai** : prévision plus précoce, mais avec moins d’informations ;
- **15 juin** : prévision plus proche de la récolte, avec davantage de signaux phénologiques et météo.

Le projet doit donc mesurer non seulement la meilleure performance possible, mais également la **valeur opérationnelle du délai d’anticipation**.

## 5. Formulation IA

### Type de problème

Régression supervisée tabulaire multimodale.

### Unité d’observation

Parcelle × année.

### Entrées

- identifiants et surface de parcelle ;
- année et région ;
- propriétés du sol à plusieurs profondeurs ;
- variables Sentinel-2 ;
- variables Sentinel-1 ;
- variables météorologiques et agroclimatiques ;
- variables disponibles avant la date de coupure retenue.

### Cible principale

```text
harvest_doy_derived
```

### Unité de la cible

Jour de l’année, ou DOY — Day of Year.

### Sorties attendues

- jour de récolte prédit ;
- date calendaire correspondante ;
- intervalle prédictif en jours ;
- facteurs les plus influents ;
- indicateur de domaine de validité.

## 6. Sous-problèmes scientifiques

### 6.1 Construction de la cible

La cible est dérivée. Il faut déterminer :

- la méthode exacte de génération ;
- les sources utilisées ;
- l’existence éventuelle d’informations futures ;
- le lien avec la variante régionale ;
- le risque de circularité avec les features satellitaires ou météo.

### 6.2 Précocité contre précision

Le gain de précision du dataset du 15 juin doit être comparé au bénéfice opérationnel d’une prévision disponible dès le 31 mai.

### 6.3 Fusion multimodale

Il faut mesurer la contribution réelle de chaque famille de variables :

1. parcelle et année ;
2. sol ;
3. Sentinel-2 ;
4. Sentinel-1 ;
5. météo ;
6. toutes modalités combinées.

### 6.4 Généralisation temporelle

Le modèle doit être évalué sur une année future non utilisée pour l’ajustement ni le tuning.

### 6.5 Généralisation par parcelle

Lorsque la même parcelle est observée sur plusieurs années, elle ne doit pas être distribuée naïvement entre entraînement et test. Une validation groupée par `parcelle_uid` est nécessaire.

### 6.6 Modèles classiques contre réseaux neuronaux

La taille et la structure tabulaire du dataset rendent les modèles d’arbres très compétitifs. Les réseaux neuronaux doivent être compacts, régularisés et comparés équitablement.

### 6.7 Incertitude

Le système doit indiquer la fiabilité de sa prévision, par exemple :

```text
Date prévue : 3 juillet
Intervalle à 90 % : du 28 juin au 8 juillet
```

### 6.8 Explicabilité

L’étude doit identifier les variables associées aux prédictions, tout en évitant toute conclusion causale non démontrée.

## 7. Protocoles de validation

### Protocole principal

- entraînement sur les premières années ;
- validation sur une année intermédiaire ;
- test final sur la dernière année disponible.

### Protocole par parcelle

- `GroupKFold` ou `GroupShuffleSplit` avec `parcelle_uid` comme groupe ;
- aucune parcelle identique entre train et test dans ce protocole.

### Comparaison des horizons

- mêmes observations communes ;
- même split ;
- mêmes métriques ;
- même budget de tuning ;
- analyse du gain en jours et de la perte d’anticipation.

## 8. Métriques

### Métrique principale

- MAE en jours.

### Métriques secondaires

- RMSE en jours ;
- erreur médiane absolue ;
- R² ;
- biais moyen ;
- pourcentage de prédictions à ±3, ±5, ±7 et ±10 jours ;
- couverture et largeur des intervalles prédictifs ;
- métriques par année ;
- métriques par plage de date de récolte ;
- latence et coût d’inférence.

## 9. Baselines et modèles

### Baselines naïves

- moyenne globale de la cible ;
- médiane globale ;
- moyenne par année ;
- référence régionale lorsque sa définition le permet.

### Modèles classiques

- Ridge ;
- ElasticNet ;
- Random Forest ;
- Extra Trees ;
- XGBoost ;
- CatBoost.

### Modèles neuronaux

- MLP régularisé ;
- TabNet ;
- FT-Transformer compact comme extension contrôlée.

LSTM, CNN et Vision Transformer ne sont pas prioritaires avec les tables agrégées actuelles. Ils ne deviennent pertinents que si des séquences ou images brutes sont préparées explicitement.

## 10. Hypothèses de recherche

- La fusion multimodale réduira le MAE par rapport aux approches mono-source.
- Le dataset du 15 juin sera plus précis que celui du 31 mai.
- Le dataset du 31 mai conservera une valeur opérationnelle grâce à une anticipation plus importante.
- Les modèles d’arbres seront difficiles à battre sur ce volume tabulaire.
- La validation aléatoire produira probablement des résultats plus optimistes que la validation temporelle et groupée.
- Les intervalles conformes ou quantiles permettront de communiquer une incertitude exploitable.

## 11. Risques de validité

- cible dérivée construite avec des variables également présentes en entrée ;
- variables calculées après la date de coupure ;
- même parcelle dans le train et le test ;
- couverture temporelle différente entre modalités ;
- confusion entre cible dérivée et observation terrain ;
- échantillon limité à une seule région ;
- biais de sélection des parcelles ;
- performances surestimées par un split aléatoire ;
- comparaison inéquitable entre les jeux 31 mai et 15 juin.

## 12. Contribution attendue

Le projet sera scientifiquement réussi s’il fournit :

1. une documentation vérifiable de la cible ;
2. une pipeline reproductible des données brutes aux tables ML ;
3. une comparaison rigoureuse des horizons 31 mai et 15 juin ;
4. une étude d’ablation multimodale ;
5. une validation temporelle et par parcelle ;
6. une comparaison équitable entre modèles classiques et neuronaux ;
7. une estimation d’incertitude ;
8. une analyse d’erreurs ;
9. une démonstration produit complète.

## 13. Formulation courte pour le rapport

> AgriPredict AI étudie la prédiction multimodale de la date de récolte du blé à l’échelle parcellaire en Centre-Val de Loire. Le projet compare des prévisions arrêtées au 31 mai et au 15 juin afin de quantifier le compromis entre anticipation et précision, tout en évaluant la généralisation temporelle, la robustesse, l’explicabilité et l’incertitude des modèles.
