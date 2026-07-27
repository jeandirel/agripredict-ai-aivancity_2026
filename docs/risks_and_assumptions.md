# AgriPredict AI — Registre des risques et hypothèses

> **Cadre :** Clinique IA d’aivancity — Promotion 2026  
> **Responsable du suivi :** Jean Direl NZE  
> **Version :** 2.0

## 1. Méthode

- **Probabilité :** Faible, Moyenne, Élevée.
- **Impact :** Faible, Moyen, Élevé, Critique.
- **Priorité :** combinaison de la probabilité et de l’impact.
- **Déclencheur :** signal concret indiquant que le risque devient actif.

Le registre est revu chaque semaine et à chaque passage de Quality Gate.

## 2. Registre des risques

| ID | Risque | Probabilité | Impact | Priorité | Déclencheur | Prévention | Réponse |
|---|---|---:|---:|---:|---|---|---|
| R-001 | Cible `harvest_doy_derived` construite à partir de variables également utilisées comme features | Élevée | Critique | Critique | Performance anormalement élevée ou méthode de dérivation circulaire | Audit du rapport méthodologique et du code de cible | Exclure les variables concernées, redéfinir l’expérience ou utiliser la variante régionale |
| R-002 | Variables postérieures au 31 mai présentes dans le jeu 31 mai | Moyenne | Critique | Critique | Date de calcul ou nom de feature incohérent | Registre de disponibilité temporelle par colonne | Supprimer les colonnes et reconstruire le dataset |
| R-003 | Variables postérieures au 15 juin présentes dans le jeu 15 juin | Moyenne | Critique | Critique | Feature calculée sur toute la saison | Audit temporel et code de génération | Reconstruire les agrégats strictement avant la coupure |
| R-004 | Même parcelle dans train et test | Élevée | Critique | Critique | `parcelle_uid` commun aux deux ensembles | Split groupé avant preprocessing | Invalider et réentraîner tous les modèles concernés |
| R-005 | Split aléatoire surestimant la généralisation temporelle | Élevée | Élevé | Critique | Score aléatoire nettement meilleur que le test futur | Test final chronologique obligatoire | Retenir le protocole chronologique comme résultat principal |
| R-006 | Relation ambiguë entre jeux `final`, `derived` et `regional` | Élevée | Élevé | Critique | Schémas ou lignes différents sans documentation | Comparaison de hashes, clés, colonnes et cibles | Établir une table de lineage avant entraînement |
| R-007 | Licence Kaggle ou source originale incompatible avec la redistribution | Moyenne | Élevé | Élevée | Licence absente ou restrictive | Relever licence et conditions par source | Garder scripts et liens, retirer les données du dépôt public |
| R-008 | Données brutes indisponibles ou difficiles à retélécharger | Moyenne | Élevé | Élevée | Échec API, fichier supprimé ou accès restreint | Script Kaggle, manifeste et hashes | Conserver une copie autorisée hors Git et documenter la procédure |
| R-009 | Couverture temporelle non commune entre Sentinel-1, Sentinel-2 et météo | Élevée | Élevé | Critique | Années ou parcelles manquantes selon modalité | Table de couverture par parcelle-année | Comparer intersection complète et modèles à modalités partielles |
| R-010 | Valeurs manquantes importantes dans les signaux satellites | Élevée | Élevé | Critique | Taux élevé ou biais saisonnier | Audit par année et modalité | Imputation contrôlée, indicateurs de manque ou exclusion justifiée |
| R-011 | Propriétés du sol interprétées dans de mauvaises unités | Moyenne | Élevé | Élevée | Plages physiques incohérentes | Utiliser les dictionnaires de données | Corriger unités ou transformations avant modélisation |
| R-012 | Identifiants de parcelles non stables entre sources | Moyenne | Critique | Critique | Jointures multiples ou perte massive de lignes | Tests d’unicité et de cardinalité | Revoir les clés et produire une table de correspondance |
| R-013 | Biais de sélection des 1 500 parcelles | Moyenne | Élevé | Élevée | Distribution peu représentative du Centre-Val de Loire | Comparer surfaces, années et sous-zones | Limiter le domaine de validité et documenter l’échantillon |
| R-014 | Trop peu d’observations pour des réseaux profonds | Élevée | Élevé | Critique | Surapprentissage et forte variance | Architectures compactes et baselines fortes | Retenir un modèle d’arbres ou un MLP plus simple |
| R-015 | Modèle du 15 juin plus précis mais moins utile opérationnellement | Moyenne | Moyen | Élevée | Gain faible par rapport aux 15 jours perdus | Mesurer gain en jours et discuter avec le métier | Préférer le modèle du 31 mai pour certains usages |
| R-016 | Fusion multimodale sans gain stable | Moyenne | Moyen | Élevée | Ablations équivalentes au modèle complet | Étude par année et modalité | Présenter le résultat négatif et simplifier le modèle |
| R-017 | Performance masquant de fortes erreurs tardives ou précoces | Élevée | Élevé | Critique | Erreurs concentrées sur certaines dates | Métriques par quantile et plage de cible | Calibration, modèle spécialisé ou domaine restreint |
| R-018 | Intervalles d’incertitude trop étroits | Moyenne | Élevé | Élevée | Couverture inférieure au nominal | Jeu de calibration séparé | Recalibrer ou afficher un niveau plus prudent |
| R-019 | Explications instables entre folds | Moyenne | Élevé | Élevée | Variables importantes changeant fortement | Stabilité des rangs et plusieurs méthodes | Signaler l’instabilité et éviter les conclusions fortes |
| R-020 | Comparaison 31 mai / 15 juin faite sur des observations différentes | Moyenne | Critique | Critique | Nombre ou clés non identiques | Intersection commune obligatoire | Refaire la comparaison sur les mêmes parcelles-années |
| R-021 | Tuning indirect sur le test final | Moyenne | Critique | Critique | Choix répétés après lecture du score final | Gel du test et journal de décisions | Reconstituer un test non consulté si possible |
| R-022 | Résultats non reproductibles | Moyenne | Critique | Critique | Notebook manuel ou dépendances flottantes | Scripts, lockfile, DVC et MLflow | Ne pas inclure le résultat dans le rapport |
| R-023 | Dépôt public contenant des fichiers non redistribuables | Moyenne | Critique | Critique | Revue de licence défavorable | Audit avant commit | Retirer, purger l’historique et documenter l’incident |
| R-024 | Absence d’expertise agronomique | Élevée | Élevé | Critique | Interprétation non validée | Identifier un relecteur métier | Limiter les conclusions et employer un vocabulaire prudent |
| R-025 | Interface présentant la date comme certaine | Moyenne | Critique | Critique | Absence d’intervalle ou d’avertissement | Incertitude et OOD obligatoires | Bloquer ou dégrader la sortie en cas de faible confiance |
| R-026 | Démo dépendante de Kaggle ou d’Internet | Moyenne | Élevé | Élevée | Échec réseau le jour de la soutenance | Cache local autorisé, Docker et exemple embarqué | Mode démonstration hors ligne et vidéo de secours |

## 3. Hypothèses structurantes

| ID | Hypothèse | Statut | Vérification | Conséquence si fausse |
|---|---|---|---|---|
| A-001 | La culture étudiée est le blé | Confirmée par les noms des jeux sources | Vérifier les fichiers et dictionnaires | Revoir le domaine agronomique |
| A-002 | La zone principale est le Centre-Val de Loire | Confirmée par les sources | Vérifier `region` et les parcelles | Réviser le périmètre géographique |
| A-003 | L’unité d’observation est parcelle × année | Très probable | Tester l’unicité de la clé | Repenser les splits et l’agrégation |
| A-004 | `harvest_doy_derived` représente un jour de récolte dérivé | Très probable | Rapport méthodologique et distributions | Redéfinir la cible |
| A-005 | La cible ne dépend pas de features postérieures aux coupures | À confirmer | Audit de construction | Invalider ou reconstruire la cible |
| A-006 | Le jeu du 31 mai ne contient que des données disponibles au 31 mai | À confirmer | Registre temporel par colonne | Reconstruire le jeu |
| A-007 | Le jeu du 15 juin ne contient que des données disponibles au 15 juin | À confirmer | Registre temporel par colonne | Reconstruire le jeu |
| A-008 | Les années complètes communes sont probablement 2020–2024 | À confirmer | Audit de l’intersection | Adapter le split temporel |
| A-009 | Environ 1 500 parcelles existent dans les sources brutes | À confirmer par comptage | Comptage d’identifiants uniques | Ajuster le protocole et la complexité |
| A-010 | Les modèles d’arbres sont de fortes baselines | Probable | Benchmark | Retenir un autre modèle si démontré |
| A-011 | Un réseau compact peut être testé sans devenir le cœur artificiel du projet | Probable | Courbes d’apprentissage | Supprimer ou simplifier le réseau |
| A-012 | La variante régionale est comparable ou utilisable comme référence | À confirmer | Dictionnaire et jointure | La conserver comme analyse séparée |
| A-013 | Les datasets Kaggle sont téléchargeables via API | À confirmer | Test automatisé | Documenter téléchargement manuel ou stockage contrôlé |
| A-014 | Les licences permettent au moins l’usage académique | À confirmer | Revue de chaque source | Restreindre redistribution et usage |
| A-015 | Un référent académique validera le cadrage | Probable | Revue Phase 0 | Conserver un decision log détaillé |
| A-016 | Un expert métier pourra relire la valeur du délai d’anticipation | Incertain | Identifier un contact | Présenter l’analyse comme hypothèse opérationnelle |

## 4. Risques éthiques et d’usage

### 4.1 Surconfiance

Une date précise peut donner une impression de certitude excessive.

**Mesures :**

- intervalle en jours ;
- avertissement explicite ;
- affichage du modèle et de l’horizon ;
- rejet ou prudence en cas d’entrée hors domaine.

### 4.2 Usage hors domaine

Le modèle ne doit pas être appliqué sans validation à :

- d’autres cultures ;
- d’autres régions ;
- des années climatiquement très différentes ;
- des parcelles présentant des caractéristiques absentes de l’entraînement.

### 4.3 Nature dérivée de la cible

La cible ne doit jamais être présentée comme une mesure terrain directe si elle est reconstruite à partir d’indicateurs.

### 4.4 Corrélation et causalité

Les variables importantes pour le modèle ne prouvent pas qu’elles déterminent causalement la date de récolte.

### 4.5 Identifiants parcellaires

Même sans nom de personne, les identifiants et géométries de parcelles doivent être traités avec prudence selon leur niveau de précision et les conditions de redistribution.

## 5. Plans de contingence

### Niveau 1 — Correction locale

- corriger une unité ;
- supprimer une feature temporellement invalide ;
- réentraîner sans modifier la question centrale.

### Niveau 2 — Réduction contrôlée

- utiliser uniquement les années communes ;
- utiliser l’intersection des modalités ;
- limiter les modèles neuronaux ;
- réduire l’analyse à la cible dérivée validée.

### Niveau 3 — Recentrage scientifique

- faire de l’audit de cible une contribution principale ;
- comparer uniquement 31 mai / 15 juin avec baselines fortes ;
- conserver la reconstruction brute comme démonstration partielle.

### Niveau 4 — Blocage critique

Si la cible est scientifiquement invalide ou circulaire :

- suspendre les conclusions prédictives ;
- documenter le problème ;
- reconstruire une cible défendable ou utiliser la référence régionale ;
- ne jamais présenter un score élevé comme une réussite.

## 6. Risques bloquants avant la Phase 1

- méthode exacte de construction de `harvest_doy_derived` ;
- relation entre les jeux `final`, `derived` et `regional` ;
- variables autorisées pour chaque date de coupure ;
- licences et redistribution ;
- années et parcelles réellement communes ;
- stratégie de test temporel ;
- stratégie de séparation par parcelle.

## 7. Revue hebdomadaire

À chaque revue :

1. vérifier les nouveaux risques ;
2. actualiser probabilité et impact ;
3. attribuer une action et une échéance ;
4. relier les preuves aux commits et rapports ;
5. invalider immédiatement tout résultat affecté par une fuite ;
6. fermer les risques uniquement avec une preuve vérifiable.
