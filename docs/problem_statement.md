# AgriPredict AI — Problématique scientifique

> **Cadre :** Clinique IA d’aivancity — 2026  
> **Version :** 1.0  
> **Statut :** À valider avec l’encadrement académique

## 1. Contexte

La production agricole dépend d’interactions complexes entre le climat, l’état du sol, la dynamique de la végétation, les pratiques culturales et les caractéristiques géographiques. Les méthodes traditionnelles d’estimation du rendement reposent souvent sur des enquêtes, des mesures terrain ou des statistiques historiques. Elles peuvent être précises localement mais difficiles à généraliser rapidement à grande échelle.

Les données de télédétection apportent une observation répétée des cultures. Les indices optiques tels que le NDVI et l’EVI décrivent la vigueur de la végétation, tandis que les mesures micro-ondes comme les rétrodiffusions SH et SV restent disponibles dans des conditions nuageuses et renseignent indirectement sur la structure du couvert et l’humidité. Les propriétés du sol et les données météorologiques complètent ces observations.

Cependant, la réunion de ces sources pose plusieurs difficultés :

- résolutions spatiales et temporelles différentes ;
- valeurs manquantes et couverture nuageuse ;
- données agricoles fragmentées ;
- faible nombre d’années ou d’observations pour certaines zones ;
- risques de fuite de données géographiques et temporelles ;
- décalage entre performance sur un split aléatoire et généralisation réelle ;
- difficulté à expliquer et calibrer les prédictions.

## 2. Problème métier

Les acteurs agricoles ont besoin d’indicateurs plus précoces et plus fiables pour :

- anticiper les rendements ;
- détecter les risques de sécheresse ;
- comparer plusieurs cultures possibles ;
- comprendre les facteurs qui influencent une estimation ;
- distinguer une prédiction fiable d’une prédiction incertaine.

Une simple valeur prédite sans explication, sans intervalle d’incertitude et sans validation hors distribution est insuffisante pour soutenir une décision responsable.

## 3. Problème scientifique principal

> **Comment concevoir et évaluer un système d’intelligence artificielle multimodal capable de prédire le rendement agricole à partir de séries satellitaires, de données météorologiques, de propriétés du sol et d’informations géographiques, tout en démontrant sa généralisation temporelle et spatiale, son explicabilité et la fiabilité de son incertitude ?**

## 4. Sous-problèmes scientifiques

### 4.1 Fusion multimodale

Déterminer si la combinaison de sources complémentaires améliore réellement la prédiction par rapport à chaque source utilisée séparément.

### 4.2 Représentation temporelle

Identifier l’architecture la plus adaptée pour représenter l’évolution de la végétation et des conditions météorologiques : agrégats tabulaires, LSTM, GRU, TCN ou Transformer temporel compact.

### 4.3 Représentation statique

Combiner correctement les propriétés du sol, les variables géographiques et les variables catégorielles avec les séries temporelles.

### 4.4 Généralisation

Mesurer la capacité du modèle à fonctionner sur :

- une année future ;
- un district non observé ;
- un État ou une région non observé ;
- des observations présentant davantage de valeurs manquantes.

### 4.5 Incertitude

Produire un intervalle prédictif exploitable et vérifier sa couverture réelle.

### 4.6 Explicabilité

Identifier les variables, périodes et modalités qui contribuent aux prédictions, sans présenter une corrélation comme une causalité.

## 5. Définition opérationnelle des trois modules

## 5.1 Module principal — Rendement agricole

### Question métier

Quel rendement agricole peut être attendu pour une zone et une période données ?

### Formulation IA

Régression supervisée multimodale.

### Entrées envisagées

- séries NDVI et EVI ;
- séries SH et SV ;
- ratio SH/SV ;
- température, précipitations, humidité et vent ;
- AWC, FC, WP et SWC ;
- État, district, année et variables géographiques.

### Cible

Rendement agricole rapporté, idéalement exprimé en tonnes par hectare.

### Unité

`t/ha`, à confirmer dans les fichiers de données définitifs.

### Sortie attendue

- estimation ponctuelle ;
- intervalle d’incertitude ;
- explication globale et locale ;
- indicateur de confiance ou de domaine de validité.

### Protocoles de validation obligatoires

- validation temporelle ;
- GroupKFold par district ;
- Leave-One-State-Out ou équivalent géographique ;
- comparaison à des baselines simples.

## 5.2 Module avancé — Sécheresse

### Question métier

Quel sera le niveau de sévérité de la sécheresse à un horizon futur défini ?

### Formulation IA

Prévision de série temporelle ou régression temporelle supervisée.

### Entrées envisagées

- température ;
- précipitations ;
- humidité ;
- vent ;
- point de rosée ;
- historiques de sévérité ;
- région et saisonnalité.

### Cible

Indice futur de sévérité de la sécheresse.

### Horizon

À fixer explicitement après audit : J+7, J+30 ou période suivante.

### Sortie attendue

- valeur future ;
- classe de risque ;
- intervalle d’incertitude ;
- facteurs principaux.

### Condition de validité

Le module ne pourra être qualifié de « forecasting » que si les données comportent une chronologie exploitable et si le protocole interdit toute information future dans l’entraînement.

## 5.3 Module opérationnel — Recommandation de cultures

### Question métier

Quelles cultures sont les plus compatibles avec les conditions du sol et du climat fournies ?

### Formulation IA

Classification multiclasse avec classement Top-k.

### Entrées envisagées

- azote ;
- phosphore ;
- potassium ;
- température ;
- humidité ;
- pH ;
- précipitations.

### Cible

Type de culture.

### Sortie attendue

- top 3 des cultures ;
- probabilités calibrées ;
- facteurs explicatifs ;
- avertissement en cas d’entrée hors distribution.

## 6. Écart de recherche visé

Le projet ne doit pas seulement reproduire un modèle existant. Sa contribution doit être démontrée par :

1. une pipeline commune et reproductible ;
2. une comparaison contrôlée mono-source contre multimodale ;
3. une validation temporelle et géographique ;
4. une architecture neuronale adaptée aux séries et variables statiques ;
5. une étude d’ablation ;
6. une estimation d’incertitude ;
7. une analyse d’erreurs et de robustesse ;
8. une démonstration produit complète.

## 7. Critères de non-réussite scientifique

Le projet serait considéré scientifiquement insuffisant si :

- la performance est mesurée uniquement sur un split aléatoire ;
- les baselines simples sont absentes ;
- le modèle complexe n’est pas comparé équitablement ;
- les données du test influencent la préparation ou le tuning ;
- la provenance et la licence des données ne sont pas documentées ;
- les résultats ne sont pas reproductibles ;
- aucune analyse d’incertitude ou de limite n’est fournie ;
- le projet revendique une causalité non démontrée.

## 8. Formulation courte pour le rapport

> AgriPredict AI étudie la capacité d’une architecture multimodale à combiner télédétection, météo, propriétés du sol et historique agricole afin d’améliorer la prédiction du rendement. Le système est évalué non seulement sur sa précision, mais aussi sur sa généralisation temporelle et géographique, son explicabilité, sa robustesse et la calibration de son incertitude.

## 9. Points à confirmer avant clôture de la Phase 0

- Culture principale retenue pour le module rendement.
- Zone géographique définitive.
- Années réellement disponibles.
- Unité et définition exacte du rendement.
- Horizon de prévision de la sécheresse.
- Existence d’un partenaire ou expert agronome.
- Droits de stockage et de redistribution des datasets.
- Ressources de calcul disponibles.
