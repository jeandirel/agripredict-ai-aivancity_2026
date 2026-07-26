# AgriPredict AI — Charte de projet

> **Cadre :** Clinique IA d’aivancity — Promotion 2026  
> **Responsable du projet :** Jean Direl NZE  
> **Statut :** Cadrage scientifique initial  
> **Version :** 1.0

## 1. Finalité

AgriPredict AI est une plateforme d’intelligence artificielle agricole multimodale destinée à transformer des données satellitaires, météorologiques, pédologiques et historiques en indicateurs d’aide à la décision.

Le projet doit démontrer, de manière scientifiquement rigoureuse et reproductible, la valeur de la fusion multimodale pour trois usages complémentaires :

1. prédire le rendement agricole ;
2. anticiper la sévérité de la sécheresse ;
3. recommander les cultures les plus adaptées aux conditions observées.

Le cœur scientifique du projet est la **prédiction multimodale du rendement agricole**. Les modules de sécheresse et de recommandation complètent la plateforme sans remplacer ce sujet principal.

## 2. Problématique directrice

> Dans quelle mesure la fusion de données satellitaires, météorologiques, pédologiques et historiques améliore-t-elle la qualité, la robustesse et l’explicabilité des prédictions agricoles par rapport à des modèles mono-source ?

## 3. Objectifs

### 3.1 Objectif scientifique principal

Concevoir et évaluer une architecture multimodale capable de prédire le rendement agricole en combinant :

- des séries temporelles satellitaires ;
- des variables météorologiques ;
- des propriétés statiques du sol ;
- des informations géographiques et historiques.

### 3.2 Objectifs scientifiques secondaires

- Comparer des baselines statistiques, des modèles d’ensemble et des réseaux neuronaux adaptés.
- Mesurer la généralisation temporelle et géographique.
- Quantifier l’incertitude des prédictions.
- Identifier les variables et périodes les plus influentes.
- Vérifier la robustesse du système face aux données manquantes, au bruit et au changement de région.

### 3.3 Objectifs produit

- Proposer une API documentée.
- Développer une interface web de démonstration.
- Afficher les prédictions, intervalles d’incertitude et explications.
- Permettre l’exécution reproductible du projet depuis le dépôt GitHub.

### 3.4 Objectifs d’ingénierie

- Versionner le code, les données et les expériences.
- Automatiser les tests de données et de modèles.
- Conteneuriser la solution.
- Mettre en place une intégration continue.
- Documenter les limites, risques et conditions d’usage.

## 4. Périmètre

### 4.1 Inclus

- Audit, nettoyage et harmonisation des données.
- Traitement géospatial et agrégation temporelle.
- Feature engineering agronomique et climatique.
- Baselines statistiques et machine learning.
- Réseaux neuronaux pour données tabulaires et temporelles.
- Fusion multimodale et ensemble learning.
- Validation temporelle et géographique.
- Explicabilité, calibration et estimation d’incertitude.
- API FastAPI, tableau de bord, tests, Docker et documentation.
- Rapport scientifique et support de soutenance.

### 4.2 Hors périmètre initial

- Pilotage autonome de machines agricoles.
- Déclenchement automatique d’irrigation ou de traitement phytosanitaire.
- Recommandations financières ou assurantielles automatisées.
- Déploiement national en production sans validation agronomique externe.
- Promesse de causalité à partir d’analyses prédictives.
- Collecte terrain à grande échelle, sauf validation expérimentale ciblée.

## 5. Modules

| Module | Priorité | Type de problème | Entrées principales | Sortie |
|---|---:|---|---|---|
| Rendement agricole | 1 | Régression multimodale | NDVI, EVI, SH, SV, météo, sol, géographie | Rendement estimé + intervalle d’incertitude |
| Sécheresse | 2 | Prévision temporelle | Température, pluie, humidité, vent, indices historiques | Sévérité future + niveau de risque |
| Recommandation de cultures | 3 | Classification multiclasse | N, P, K, pH, température, humidité, pluie | Top 3 cultures + probabilités |

## 6. Livrables obligatoires

1. Charte, problématique, questions de recherche et critères de succès.
2. Inventaire documenté des sources de données.
3. Pipelines de préparation des données.
4. Baselines reproductibles.
5. Modèles classiques et neuronaux comparés.
6. Étude d’ablation multimodale.
7. Validation temporelle et géographique.
8. Analyse d’erreurs, robustesse et incertitude.
9. Explicabilité globale et locale.
10. API et interface fonctionnelles.
11. Tests automatisés et pipeline CI.
12. Image Docker.
13. Model Cards et Data Cards.
14. Rapport scientifique.
15. Présentation et démonstration de soutenance.
16. Release GitHub `v1.0.0`.

## 7. Principes de réalisation

- **Reproductibilité avant performance brute.**
- **Baselines avant modèles complexes.**
- **Aucune fuite temporelle ou géographique tolérée.**
- **Un réseau neuronal n’est retenu que s’il est adapté au volume et à la structure des données.**
- **Les résultats négatifs sont documentés.**
- **Les métriques sont accompagnées d’intervalles de confiance lorsque possible.**
- **Les prédictions sont présentées comme une aide à la décision, jamais comme une certitude.**
- **Les sources, licences et restrictions d’usage sont explicitement documentées.**

## 8. Parties prenantes

| Rôle | Partie prenante | Responsabilité |
|---|---|---|
| Responsable projet | Jean Direl NZE | Cadrage, architecture, expérimentation, développement, documentation et soutenance |
| Encadrement académique | Clinique IA d’aivancity | Validation pédagogique, retours méthodologiques et évaluation |
| Experts métier | À identifier | Validation agronomique des variables, résultats et limites |
| Utilisateurs cibles | Agriculteurs, analystes, institutions agricoles | Évaluation de la compréhension et de l’utilité des sorties |
| Fournisseurs de données | Organismes publics et plateformes satellitaires | Mise à disposition des données selon leurs licences |

## 9. Gouvernance

### 9.1 Rythme de pilotage

- Revue hebdomadaire des travaux et risques.
- Revue de fin de phase avec critères d’acceptation.
- Décisions techniques majeures consignées dans le dépôt.
- Expériences enregistrées avec version du code, des données et des paramètres.

### 9.2 Contrôle des changements

Toute modification importante du périmètre doit préciser :

- la justification ;
- l’impact sur les délais ;
- l’impact scientifique ;
- l’impact sur les données ;
- le risque de dilution du sujet principal.

## 10. Critères de fin de Phase 0

La Phase 0 est validée lorsque chaque module dispose de :

- sa question métier ;
- sa question scientifique ;
- ses entrées et leurs unités ;
- sa cible et son horizon ;
- ses métriques principales et secondaires ;
- son protocole de validation ;
- son critère d’acceptation ;
- ses principales hypothèses et limites ;
- une source de données identifiée avec statut d’accès et de licence.

## 11. Décisions initiales

| ID | Décision | Justification |
|---|---|---|
| D-001 | Le rendement agricole est le cœur scientifique | Permet une étude approfondie de fusion multimodale sans disperser le projet |
| D-002 | Les modèles classiques servent de référence obligatoire | Évite de confondre complexité et performance scientifique |
| D-003 | La validation doit être temporelle et géographique | Un split aléatoire seul risque de surestimer la généralisation |
| D-004 | L’incertitude et l’explicabilité sont intégrées dès la conception | Les sorties doivent être utilisables et responsables |
| D-005 | Les modules secondaires ne doivent pas retarder le module rendement | La profondeur du cœur scientifique est prioritaire |

## 12. Approbations à obtenir

- Validation du cadrage par le référent de la Clinique IA.
- Confirmation des données réellement accessibles.
- Confirmation des licences et droits de redistribution.
- Validation de la définition exacte des cibles et horizons.
- Confirmation de l’existence ou non d’un partenaire métier/agronomique.
