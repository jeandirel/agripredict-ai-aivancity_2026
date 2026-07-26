# AgriPredict AI — Inventaire initial des données et sources

> **Cadre :** Clinique IA d’aivancity — 2026  
> **Version :** 1.0  
> **Statut :** Inventaire initial fondé sur les documents disponibles dans le dépôt et les références du projet. Les fichiers de données brutes, leurs licences et leurs schémas doivent encore être vérifiés avant modélisation.

## 1. Règle de gouvernance

Une publication, un rapport ou un PDF décrivant un dataset ne constitue pas automatiquement un droit d’accès ni de redistribution du dataset.

Chaque source doit donc être classée comme :

- **référence scientifique** ;
- **source de téléchargement** ;
- **fichier de données effectivement acquis** ;
- **donnée dérivée produite par la pipeline**.

Aucune donnée brute ne doit être ajoutée au dépôt public avant validation de sa licence.

## 2. Inventaire synthétique

| ID | Source | Nature | Module | Statut d’accès | Licence / redistribution | Action suivante |
|---|---|---|---|---|---|---|
| DS-001 | Rapport RYP — intégration télédétection et ML pour rendement du riz | Rapport de projet / référence | Rendement | PDF disponible | À vérifier pour les datasets sous-jacents | Localiser les fichiers bruts et confirmer les droits |
| DS-002 | Sentinel-2 / Copernicus | Imagerie satellitaire optique | Rendement | Source identifiée | Conditions Copernicus à documenter | Définir zone, période et méthode de téléchargement |
| DS-003 | EOS-06 SCAT-3 / MOSDAC | Données micro-ondes | Rendement | Source identifiée | Conditions MOSDAC à vérifier | Confirmer accès, format et droits d’usage |
| DS-004 | Masques riz 2023–2024 | Raster de cultures | Rendement | Mentionnés dans le rapport | Source et licence non précisées | Identifier le fournisseur exact |
| DS-005 | GADM | Limites administratives | Rendement | Source identifiée | Licence GADM à vérifier pour l’usage prévu | Documenter la version et la redistribution |
| DS-006 | Paramètres du sol AWC, FC, WP, SWC | Données pédologiques | Rendement | Mentionnés dans le rapport | Source exacte à confirmer | Retrouver fichier et documentation |
| DS-007 | Rendements de riz par district | Cible supervisée | Rendement | Rapports gouvernementaux mentionnés | Source et licence à confirmer | Identifier organisme, unité et années |
| DS-008 | Données météo associées aux districts | Séries météorologiques | Rendement | Non fixées | À déterminer | Choisir une source cohérente avec la zone |
| DS-009 | US drought meteorological data | Dataset tabulaire / temporel potentiel | Sécheresse | Source Kaggle mentionnée | Licence Kaggle/dataset à vérifier | Télécharger et auditer la chronologie réelle |
| DS-010 | Crop Recommendation dataset | Dataset tabulaire | Recommandation | Source Kaggle mentionnée | Licence à vérifier | Télécharger, empreinter et vérifier les doublons |
| DS-011 | data.gov.in | Statistiques agricoles | Rendement / extension | Portail identifié | Licence ouverte à confirmer par ressource | Identifier les jeux précis utilisés |
| DS-012 | aps.dac.gov.in | Production agricole indienne | Rendement / extension | Portail identifié | Conditions à vérifier | Vérifier disponibilité historique et granularité |

## 3. Source principale — Rendement du riz multimodal

### 3.1 Référence

Le rapport **Integrating Remote Sensing Data with Machine Learning for Predicting Rice Crop Yields: A Geospatial Analysis Approach** décrit un cadre de prédiction du rendement du riz à l’échelle des districts.

### 3.2 Périmètre décrit

- 13 États rizicoles de l’Inde : Andhra Pradesh, Assam, Bihar, Chhattisgarh, Haryana, Jharkhand, Karnataka, Madhya Pradesh, Odisha, Punjab, Telangana, Uttar Pradesh et West Bengal ;
- années 2023 et 2024 ;
- sorties à l’échelle district × année ;
- agrégation temporelle par périodes de quinze jours entre juillet et septembre.

### 3.3 Variables décrites

#### Satellitaire optique

- NDVI ;
- EVI ;
- Sentinel-2 ;
- résolution annoncée de 10 à 20 mètres selon les bandes.

#### Micro-ondes

- coefficient de rétrodiffusion SH ;
- coefficient de rétrodiffusion SV ;
- ratio SH/SV ;
- EOS-06 SCAT-3 ;
- résolution annoncée proche de 2 km.

#### Sol

- AWC — Available Water Content ;
- FC — Field Capacity ;
- WP — Wilting Point ;
- SWC — Saturated Water Content.

#### Géographie et agriculture

- État ;
- district ;
- année ;
- rendement ;
- masque de riz ;
- limites administratives.

### 3.4 Pipeline décrit

- calibration des valeurs SCAT-3 ;
- filtrage par couverture de riz ;
- agrégation spatiale par district ;
- comblement hybride des valeurs manquantes ;
- agrégation en fenêtres de quinze jours ;
- fusion satellite + sol + rendement ;
- comparaison Random Forest et XGBoost.

### 3.5 Points critiques à vérifier

- Les fichiers bruts sont-ils présents dans le dépôt ou accessibles séparément ?
- Quelle est la source exacte des masques riz 2023 et 2024 ?
- Quelle est la source exacte des quatre propriétés du sol ?
- Quelle est l’unité du rendement ?
- Combien de districts et d’observations restent après nettoyage ?
- Les données 2023 et 2024 sont-elles suffisantes pour une validation temporelle crédible ?
- Les NDVI/EVI sont-ils des rasters bruts ou déjà agrégés ?
- Les valeurs SH/SV ont-elles déjà subi calibration, filtrage et imputation ?
- La formule exacte du ratio SH/SV doit être vérifiée dans le code ou les données, car la notation du rapport doit être contrôlée.

### 3.6 Schéma Gold envisagé

| Colonne | Type | Unité | Rôle | Statut |
|---|---|---|---|---|
| state | catégorie | — | groupe géographique | À confirmer |
| district | catégorie | — | groupe géographique | À confirmer |
| year | entier | année | temps | À confirmer |
| yield_t_ha | flottant | t/ha | cible | Unité à confirmer |
| ndvi_t1…t6 | flottant | indice | série optique | Décrit |
| evi_t1…t6 | flottant | indice | série optique | Décrit, présence finale à confirmer |
| sh_t1…t6 | flottant | dB | série micro-ondes | Décrit |
| sv_t1…t6 | flottant | dB | série micro-ondes | Décrit |
| sh_sv_ratio_t1…t6 | flottant | ratio | feature dérivée | À recalculer de manière contrôlée |
| awc | flottant | à confirmer | sol | Décrit |
| fc | flottant | à confirmer | sol | Décrit |
| wp | flottant | à confirmer | sol | Décrit |
| swc | flottant | à confirmer | sol | Décrit |
| imputed_* | booléen | — | traçabilité | À créer |

## 4. Source sécheresse

### 4.1 Référence

L’article **Meteorological drought severity forecasting utilizing blended modelling**, publié dans MethodsX en 2025, décrit une approche d’ensemble combinant XGBoost, LSTM et TabNet.

### 4.2 Dataset décrit

- environ 50 000 lignes ;
- variables météorologiques ;
- score de sévérité de sécheresse ;
- données historiques sur plusieurs années selon l’article ;
- source Kaggle indiquée : dataset de données météorologiques de sécheresse aux États-Unis.

### 4.3 Variables mentionnées

- température ;
- précipitations ;
- humidité ;
- vitesse du vent ;
- point de rosée ;
- région ;
- État ;
- durée de sécheresse ;
- indice ou score de sévérité.

### 4.4 Risque majeur

Le PDF décrit un problème de forecasting, mais il faut vérifier dans le fichier réel :

- l’existence d’un timestamp fiable ;
- la fréquence temporelle ;
- la continuité des séquences ;
- l’identifiant géographique ;
- la définition exacte de la cible ;
- l’absence de variables calculées avec des informations futures.

Sans chronologie exploitable, le module devra être requalifié en régression de sévérité plutôt qu’en prévision temporelle.

### 4.5 Schéma Gold envisagé

| Colonne | Type | Unité | Rôle |
|---|---|---|---|
| timestamp | datetime | — | temps |
| region | catégorie | — | groupe |
| state | catégorie | — | groupe |
| temperature | flottant | à confirmer | entrée |
| precipitation | flottant | à confirmer | entrée |
| humidity | flottant | % probable | entrée |
| wind_speed | flottant | à confirmer | entrée |
| dew_point | flottant | à confirmer | entrée |
| severity | flottant / ordinal | 0–4 selon le document | cible |
| drought_duration | entier | jours selon le document | entrée à auditer pour fuite |

## 5. Source recommandation de cultures

### 5.1 Référence

L’article **Crop prediction using machine learning** décrit l’utilisation du dataset Kaggle « Crop Recommendation ».

### 5.2 Dataset décrit

- 2 200 observations ;
- 22 cultures comme classes ;
- 7 variables d’entrée ;
- split 80/20 dans l’étude de référence.

### 5.3 Variables

- N — azote ;
- P — phosphore ;
- K — potassium ;
- température ;
- humidité relative ;
- pH ;
- précipitations ;
- label de culture.

### 5.4 Contrôles nécessaires

- licence du dataset ;
- doublons exacts ou quasi-doublons ;
- équilibre des 22 classes ;
- plausibilité des plages de valeurs ;
- unité des nutriments et précipitations ;
- représentativité géographique ;
- existence d’un biais synthétique ou d’une séparation artificiellement facile.

### 5.5 Schéma Gold envisagé

| Colonne | Type | Unité | Rôle |
|---|---|---|---|
| nitrogen | flottant | à confirmer | entrée |
| phosphorus | flottant | à confirmer | entrée |
| potassium | flottant | à confirmer | entrée |
| temperature | flottant | °C probable | entrée |
| humidity | flottant | % probable | entrée |
| ph | flottant | pH | entrée |
| rainfall | flottant | mm probable | entrée |
| crop | catégorie | — | cible |

## 6. Source statistique agricole historique

L’article **Predicting Agriculture Yields Based on Machine Learning Using Regression and Deep Learning** indique que les données ont été réunies à partir de portails publics indiens, notamment `data.gov.in` et `aps.dac.gov.in`.

Le dataset décrit couvre les années 1997 à 2020 et comprend notamment :

- État ;
- district ;
- année culturale ;
- saison ;
- type de culture ;
- pluie ;
- vent ;
- humidité ;
- zone irriguée ;
- surface ;
- production ;
- rendement.

Cette source peut servir :

- d’extension historique ;
- de baseline statistique ;
- de comparaison avec la télédétection ;
- de source pour élargir le nombre d’années.

Elle ne doit pas être fusionnée automatiquement avec le dataset riz 2023–2024 sans vérifier les définitions, unités, niveaux géographiques et méthodologies de collecte.

## 7. Classification Bronze–Silver–Gold

### Bronze

- fichiers téléchargés sans modification ;
- nom d’origine conservé ;
- hash SHA-256 ;
- date d’acquisition ;
- URL ou instruction de téléchargement ;
- licence associée.

### Silver

- colonnes renommées ;
- unités harmonisées ;
- dates normalisées ;
- géographies alignées ;
- doublons traités ;
- anomalies marquées ;
- aucune feature utilisant la cible.

### Gold

- table prête pour un module précis ;
- split défini ;
- schéma Pandera validé ;
- version DVC ;
- dictionnaire de données ;
- indicateurs d’imputation ;
- absence de fuite vérifiée.

## 8. Métadonnées obligatoires pour chaque fichier

```yaml
source_id: DS-XXX
name: example_dataset
source_url: "À renseigner"
provider: "À renseigner"
acquired_at: "YYYY-MM-DD"
license: "À confirmer"
redistribution_allowed: false
geographic_scope: "À renseigner"
temporal_scope: "À renseigner"
granularity: "À renseigner"
target_definition: "À renseigner"
sha256: "À calculer"
notes: ""
```

## 9. Checklist avant modélisation

- [ ] Le fichier brut est disponible.
- [ ] La source est identifiable.
- [ ] La licence est documentée.
- [ ] Le droit de redistribution est connu.
- [ ] Le hash du fichier est calculé.
- [ ] Les unités sont définies.
- [ ] La cible est précisément définie.
- [ ] La granularité temporelle est connue.
- [ ] La granularité géographique est connue.
- [ ] Les clés de jointure sont validées.
- [ ] Les risques de fuite sont documentés.
- [ ] Le schéma Bronze est enregistré.
- [ ] Le plan de split est défini avant le feature engineering final.

## 10. Décision de Phase 0

Le module rendement est prioritaire, mais son lancement dépend de la confirmation des fichiers réellement disponibles. Le module recommandation constitue le dataset le plus simple pour valider rapidement la chaîne technique. Le module sécheresse ne sera qualifié de prévision temporelle qu’après audit de sa chronologie.
