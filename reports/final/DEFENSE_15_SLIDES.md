# Soutenance — plan de 15 diapositives

## 1. Titre
AgriPredict AI — Prédiction multimodale de la date de récolte du blé, Clinique IA aivancity 2026, Jean Direl NZE.

## 2. Problème métier
Anticiper la récolte pour organiser machines, équipes, collecte et stockage.

## 3. Question scientifique
Fusion sol + Sentinel-1 + Sentinel-2 + météo et compromis 31 mai / 15 juin.

## 4. Données
Centre-Val de Loire, parcelle × année, cible dérivée, 13 jeux Kaggle documentés.

## 5. Architecture des données
Bronze → Silver → Gold → modèles → API → interface.

## 6. Risque scientifique majeur
Fuite temporelle et circularité de `harvest_doy_derived` ; variables sensibles exclues.

## 7. Protocole final
Développement sur années anciennes, calibration sur avant-dernière année, test sur 2024, GroupKFold par parcelle.

## 8. Modèles
Dummy, Ridge, Random Forest, Extra Trees, HistGradientBoosting et MLP compact.

## 9. Résultat 31 mai
MAE 8.50 jours, RMSE 10.34, R² 0.108.

## 10. Résultat 15 juin
MAE 8.34 jours, RMSE 10.23, R² 0.128.

## 11. Comparaison appariée
Présenter le delta bootstrap, l’intervalle à 95 % et le compromis anticipation–précision.

## 12. Ablations et explicabilité
Montrer la contribution des modalités et les variables principales, sans causalité revendiquée.

## 13. Incertitude et robustesse
Intervalles conformes, données manquantes, bruit, modalité absente et OOD.

## 14. Produit et MLOps
FastAPI, Streamlit, Docker, tests, CI, artefacts versionnés et documentation.

## 15. Limites et perspectives
Cible dérivée, région unique, validation terrain et extension à d’autres régions/cultures.

## Répartition suggérée des 40 minutes

- Slides 1–3 : 6 min
- Slides 4–7 : 11 min
- Slides 8–12 : 15 min
- Slides 13–15 et démonstration : 8 min
- Questions : 10 min
