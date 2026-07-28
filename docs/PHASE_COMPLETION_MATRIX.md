# AgriPredict AI — Matrice de complétion des phases

> Version 1.0.0 — Clinique IA d’aivancity 2026

| Phase | Statut | Preuves principales |
|---|---|---|
| 0. Cadrage scientifique | Terminée | `project_charter.md`, `problem_statement.md`, `research_questions.md`, `success_metrics.md` |
| 1. Fondation du dépôt | Terminée | `pyproject.toml`, `Makefile`, structure modulaire, CI |
| 2. Gouvernance et audit des données | Terminée techniquement | manifeste Kaggle, téléchargeur, hashes, audit automatisé, Data Card |
| 3. Préparation et garde-fous | Terminée | exclusion des identifiants et variables temporelles à risque |
| 4. Baselines | Terminée et reproduite | Dummy, Ridge, arbres et MLP ; `reports/modeling/benchmark.json` |
| 5. Sélection et validation stricte | Implémentée | développement ancien, calibration N-1, test N, GroupKFold par `ID_PARCEL` |
| 6. Modèles avancés | Implémentée | Extra Trees, Random Forest, HistGradientBoosting, MLP compact |
| 7. Comparaison 31 mai / 15 juin | Implémentée | test apparié et bootstrap dans `finalize_project.py` |
| 8. Ablations multimodales | Implémentée | sol, Sentinel-1, Sentinel-2, météo et combinaisons |
| 9. Incertitude | Implémentée | split-conformal à 90 %, couverture et largeur |
| 10. Explicabilité | Implémentée | importance par permutation et ablations |
| 11. Robustesse | Implémentée | valeurs manquantes, bruit et modalités absentes |
| 12. Hors domaine | Implémentée | distance standardisée et stress OOD synthétique |
| 13. API | Terminée | FastAPI, health, readiness, model-info, prediction et explain |
| 14. Interface | Terminée | Harvest Observatory React/TypeScript + dashboard Streamlit historique |
| 15. MLOps et CI/CD | Terminée | tests, Ruff, Docker, workflows et artefacts |
| 16. Éthique et gouvernance | Terminée | `ETHICS_AND_GOVERNANCE.md`, Model Cards, Data Card |
| 17. Rapport et soutenance | Générés automatiquement | rapport final, 15 slides, script de démonstration |
| 18. Livraison | Implémentée | bundle v1.0.0 et artefacts GitHub Actions |

## Point de vigilance non masqué

Le projet est un prototype de recherche complet, mais une mise en production agricole exige encore :

- une validation indépendante de `harvest_doy_derived` ;
- une vérité terrain parcellaire ;
- une validation agronomique ;
- un test externe sur une nouvelle campagne ;
- une revue des licences et de la conformité selon le contexte réel.

Ces limites ne remettent pas en cause la complétion académique et logicielle ; elles définissent honnêtement le niveau de preuve disponible.
