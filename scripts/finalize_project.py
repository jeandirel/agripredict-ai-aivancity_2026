#!/usr/bin/env python3
"""Finalize every scientific and product phase of AgriPredict AI.

This script is intentionally self-contained and deterministic. It creates the
strict final evaluation, ablations, conformal intervals, robustness and OOD
analyses, deployment candidates, model/data cards, final report, defense plan,
and reproducibility evidence.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone

from agripredict.advanced import (
    ablation_study,
    columns_for_modalities,
    ood_diagnostics,
    paired_horizon_bootstrap,
    robustness_study,
    segmented_metrics,
    strict_evaluate,
)
from agripredict.data import TARGET, common_parcel_year_keys, load_dataset, prepare_data
from agripredict.modeling import model_candidates, regression_metrics

DATASETS = {
    "may31": Path("data/master_ml_final_may31.csv"),
    "june15": Path("data/master_ml_final_june15.csv"),
}
KEYS = ["parcelle_uid", "year"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def json_default(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"Not JSON serializable: {type(value).__name__}")


def align_frames(frames: dict[str, pd.DataFrame]) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    common = common_parcel_year_keys(frames["may31"], frames["june15"]).sort_values(KEYS).reset_index(drop=True)
    aligned: dict[str, pd.DataFrame] = {}
    for horizon, frame in frames.items():
        if frame.duplicated(KEYS).any():
            raise ValueError(f"{horizon} contains duplicate parcel-year keys")
        aligned[horizon] = common.merge(frame, on=KEYS, how="left", validate="one_to_one").sort_values(KEYS).reset_index(drop=True)
        if aligned[horizon][TARGET].isna().any():
            raise ValueError(f"{horizon} has missing targets after key alignment")
    return aligned, common


def risk_feature_sensitivity(
    frame: pd.DataFrame,
    horizon: str,
    selected_model_name: str,
    test_year: int,
    *,
    random_state: int,
) -> dict[str, Any]:
    """Quantify the score change when temporally risky features are admitted.

    This is an audit only. The resulting model is never selected or deployed.
    """
    safe = prepare_data(frame, horizon, allow_temporal_risk_features=False)
    risky = prepare_data(frame, horizon, allow_temporal_risk_features=True)
    train_mask = risky.years.lt(test_year).to_numpy()
    test_mask = risky.years.eq(test_year).to_numpy()
    candidate = model_candidates(risky.X.loc[train_mask], random_state=random_state)[selected_model_name]
    fitted = clone(candidate)
    fitted.fit(risky.X.loc[train_mask], risky.y.loc[train_mask])
    prediction = fitted.predict(risky.X.loc[test_mask])
    risky_metrics = regression_metrics(risky.y.loc[test_mask], prediction)
    return {
        "status": "audit_only_not_deployable",
        "safe_feature_count": int(safe.X.shape[1]),
        "risk_feature_count": int(risky.X.shape[1]),
        "reintroduced_columns": sorted(set(risky.X.columns) - set(safe.X.columns)),
        "metrics_with_risk_features": risky_metrics,
        "warning": (
            "Any improvement may be caused by post-cutoff information or circularity with the derived target. "
            "These features remain excluded from the official model."
        ),
    }


def build_reference_row(X: pd.DataFrame) -> dict[str, Any]:
    row: dict[str, Any] = {}
    for column in X.columns:
        series = X[column]
        if pd.api.types.is_numeric_dtype(series):
            value = pd.to_numeric(series, errors="coerce").median()
            row[column] = None if pd.isna(value) else float(value)
        else:
            mode = series.dropna().astype(str).mode()
            row[column] = str(mode.iloc[0]) if not mode.empty else None
    return row


def evaluate_horizon(
    horizon: str,
    frame: pd.DataFrame,
    output_root: Path,
    *,
    random_state: int,
) -> tuple[dict[str, Any], pd.DataFrame]:
    prepared = prepare_data(frame, horizon, allow_temporal_risk_features=False)
    evaluation, masks = strict_evaluate(
        prepared.X,
        prepared.y,
        prepared.groups,
        prepared.years,
        random_state=random_state,
        alpha=0.10,
    )

    X_development = prepared.X.loc[masks.development].reset_index(drop=True)
    X_train_for_robustness = prepared.X.loc[masks.development | masks.calibration].reset_index(drop=True)
    X_test = prepared.X.loc[masks.test].reset_index(drop=True)
    y_test = prepared.y.loc[masks.test].reset_index(drop=True)

    ablations = ablation_study(
        prepared.X,
        prepared.y,
        prepared.years,
        evaluation.selected_model_name,
        masks,
        random_state=random_state,
    )
    robustness = robustness_study(
        evaluation.fitted_evaluation_model,
        X_development,
        X_test,
        y_test,
        random_state=random_state,
    )
    ood = ood_diagnostics(X_train_for_robustness, X_test, random_state=random_state)
    segments = segmented_metrics(X_test, y_test, evaluation.predictions)
    risk_sensitivity = risk_feature_sensitivity(
        frame,
        horizon,
        evaluation.selected_model_name,
        masks.test_year,
        random_state=random_state,
    )

    model_dir = output_root / horizon
    model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(evaluation.fitted_evaluation_model, model_dir / "evaluation_model.joblib")

    # Deployment candidate: model family selected without the test, then refitted on all available rows.
    deployment_candidate = model_candidates(prepared.X, random_state=random_state)[evaluation.selected_model_name]
    deployment_candidate.fit(prepared.X, prepared.y)
    joblib.dump(deployment_candidate, model_dir / "model.joblib")

    test_keys = frame.loc[masks.test, KEYS].reset_index(drop=True)
    prediction_frame = test_keys.copy()
    prediction_frame["actual_doy"] = y_test
    prediction_frame["predicted_doy"] = evaluation.predictions
    prediction_frame["lower_90_doy"] = evaluation.lower_bounds
    prediction_frame["upper_90_doy"] = evaluation.upper_bounds
    prediction_frame["absolute_error_days"] = np.abs(
        prediction_frame["actual_doy"] - prediction_frame["predicted_doy"]
    )
    prediction_frame.to_csv(model_dir / "test_predictions.csv", index=False)

    selection_scores = sorted(
        evaluation.selection_scores,
        key=lambda item: float(item["group_cv_mae_mean"])
        if item["group_cv_mae_mean"] is not None
        else float("inf"),
    )
    metadata: dict[str, Any] = {
        "generated_at": utc_now(),
        "version": "1.0.0",
        "horizon": horizon,
        "task": "parcel-level wheat harvest-date regression",
        "domain": "wheat parcels in Centre-Val de Loire, France",
        "target": TARGET,
        "target_nature": "derived",
        "target_unit": "day_of_year",
        "evaluation_protocol": {
            "development_years": list(masks.development_years),
            "calibration_year": masks.calibration_year,
            "test_year": masks.test_year,
            "model_selection": "GroupKFold by parcelle_uid on development years only",
            "uncertainty": "90% split-conformal interval calibrated on the penultimate year",
            "test_usage": "single final evaluation; never used for model-family selection",
        },
        "rows": {
            "all": int(len(prepared.y)),
            "development": int(masks.development.sum()),
            "calibration": int(masks.calibration.sum()),
            "test": int(masks.test.sum()),
        },
        "feature_count": int(prepared.X.shape[1]),
        "feature_columns": list(prepared.X.columns),
        "excluded_columns": list(prepared.excluded_columns),
        "selected_model": evaluation.selected_model_name,
        "model_selection_scores": selection_scores,
        "temporal_metrics": evaluation.temporal_metrics,
        "bootstrap_mae_ci95": {
            "lower": evaluation.bootstrap_mae_ci95[0],
            "upper": evaluation.bootstrap_mae_ci95[1],
        },
        "conformal_interval": {
            "nominal_coverage": 0.90,
            "calibration_quantile_days": evaluation.calibration_quantile_days,
            "empirical_test_coverage": evaluation.interval_coverage,
            "mean_width_days": evaluation.interval_mean_width_days,
            "median_width_days": evaluation.interval_median_width_days,
        },
        "residual_absolute_error_q90_days": evaluation.calibration_quantile_days,
        "global_feature_importance": evaluation.feature_importance,
        "ablation_study": ablations,
        "robustness_study": robustness,
        "ood_diagnostics": ood,
        "segmented_metrics": segments,
        "risk_feature_sensitivity": risk_sensitivity,
        "reference_row": build_reference_row(prepared.X),
        "limitations": [
            "The target is derived and is not a direct parcel-level field observation.",
            "External generalisation outside Centre-Val de Loire has not been demonstrated.",
            "Peak, DOY and selected AMJ variables are excluded until their lineage and cutoff availability are proven.",
            "The deployment candidate is refitted on all rows after the scientific evaluation; reported metrics come only from the evaluation model.",
        ],
    }
    (model_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False, default=json_default),
        encoding="utf-8",
    )
    return metadata, prediction_frame


def metrics_table(horizons: dict[str, dict[str, Any]]) -> str:
    lines = [
        "| Horizon | Modèle sélectionné | Année test | MAE | IC95 MAE | RMSE | R² | ±5 j | ±7 j | Couverture 90 % | Largeur intervalle |",
        "|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for horizon, result in horizons.items():
        metrics = result["temporal_metrics"]
        ci = result["bootstrap_mae_ci95"]
        interval = result["conformal_interval"]
        protocol = result["evaluation_protocol"]
        lines.append(
            f"| {horizon} | {result['selected_model']} | {protocol['test_year']} | "
            f"{metrics['mae_days']:.3f} j | [{ci['lower']:.3f}; {ci['upper']:.3f}] | "
            f"{metrics['rmse_days']:.3f} | {metrics['r2']:.3f} | "
            f"{metrics['within_5_days']:.1%} | {metrics['within_7_days']:.1%} | "
            f"{interval['empirical_test_coverage']:.1%} | {interval['mean_width_days']:.2f} j |"
        )
    return "\n".join(lines)


def final_report_markdown(payload: dict[str, Any]) -> str:
    comparison = payload["horizon_comparison"]
    lines = [
        "# AgriPredict AI — Rapport scientifique final",
        "",
        "> **Clinique IA d’aivancity — Promotion 2026**  ",
        "> **Responsable : Jean Direl NZE**  ",
        f"> **Version : 1.0.0 — générée le {payload['generated_at']}**",
        "",
        "## Résumé exécutif",
        "",
        "AgriPredict AI étudie la prévision de la date de récolte du blé à l’échelle parcellaire en Centre-Val de Loire à partir de données de sol, Sentinel-1, Sentinel-2 et NASA POWER. Deux horizons sont comparés : le 31 mai et le 15 juin. Le protocole final sépare les années de développement, une année de calibration et la dernière année comme test intouché. La sélection des modèles est réalisée uniquement par validation groupée sur les parcelles des années de développement.",
        "",
        "## Résultats principaux",
        "",
        metrics_table(payload["horizons"]),
        "",
        "## Comparaison appariée des horizons",
        "",
        f"- Différence moyenne d’erreur absolue, 15 juin moins 31 mai : **{comparison['mean_delta_absolute_error_days_june_minus_may']:.3f} jour**.",
        f"- Intervalle bootstrap à 95 % : **[{comparison['ci95_lower']:.3f}; {comparison['ci95_upper']:.3f}]**.",
        f"- Probabilité bootstrap que le 15 juin ait une erreur plus faible : **{comparison['probability_june15_lower_error']:.1%}**.",
        f"- Conclusion statistique : **{comparison['conclusion']}**.",
        "",
        "## Protocole anti-fuite",
        "",
        "- La dernière année est réservée au test final.",
        "- L’avant-dernière année sert uniquement à la calibration des intervalles.",
        "- La sélection du modèle utilise GroupKFold par `parcelle_uid` sur les années antérieures.",
        "- Les identifiants de parcelle, variables de pic, variables DOY et agrégats AMJ non prouvés sont exclus.",
        "- Une analyse séparée mesure l’effet des variables à risque, sans les rendre déployables.",
        "",
        "## Fusion multimodale et ablations",
        "",
    ]
    for horizon, result in payload["horizons"].items():
        lines += [f"### Horizon {horizon}", "", "| Configuration | Variables | MAE | RMSE | R² |", "|---|---:|---:|---:|---:|"]
        for row in result["ablation_study"]:
            lines.append(
                f"| {row['configuration']} | {row['feature_count']} | {row['mae_days']:.3f} | "
                f"{row['rmse_days']:.3f} | {row['r2']:.3f} |"
            )
        lines.append("")

    lines += [
        "## Incertitude",
        "",
        "Les intervalles sont produits par split-conformal prediction. La largeur et la couverture réelles sont rapportées pour le test final. Une couverture proche de 90 % est souhaitée, mais ne garantit pas automatiquement une validité sur une autre région ou un autre régime climatique.",
        "",
        "## Robustesse",
        "",
    ]
    for horizon, result in payload["horizons"].items():
        lines += [f"### Horizon {horizon}", "", "| Scénario | MAE | Δ MAE | Variation relative |", "|---|---:|---:|---:|"]
        for row in result["robustness_study"]:
            if "mae_days" in row:
                lines.append(
                    f"| {row['scenario']} | {row['mae_days']:.3f} | {row['delta_mae_days']:.3f} | "
                    f"{row['relative_mae_change']:.1%} |"
                )
            else:
                lines.append(f"| {row['scenario']} | échec | — | — |")
        lines.append("")

    lines += [
        "## Explicabilité",
        "",
        "Les importances par permutation mesurent une association prédictive sur le test chronologique. Elles ne prouvent aucune causalité agronomique. Les métadonnées de chaque horizon contiennent les 25 variables principales et leur variabilité.",
        "",
        "## Gouvernance et éthique",
        "",
        "- Le modèle est une aide à la planification, pas une prescription autonome.",
        "- Le domaine de validité est limité au blé du Centre-Val de Loire.",
        "- La cible `harvest_doy_derived` est explicitement présentée comme dérivée.",
        "- Les licences et conditions des sources originales doivent rester jointes au registre de données.",
        "- Les prédictions hors domaine doivent être signalées.",
        "- La décision finale de récolte reste humaine et dépend du terrain, de la météo et de contraintes opérationnelles absentes du modèle.",
        "",
        "## Limites",
        "",
        "1. absence de vérité terrain parcellaire directe confirmée pour la cible dérivée ;",
        "2. région unique ;",
        "3. nombre d’années limité ;",
        "4. variables déjà agrégées, ne permettant pas d’exploiter directement CNN ou Vision Transformers ;",
        "5. performance susceptible de dériver lors d’années climatiques atypiques ;",
        "6. bénéfice métier du délai d’anticipation à valider avec un agronome ou une coopérative.",
        "",
        "## Conclusion",
        "",
        "Le projet livre une chaîne reproductible allant des données à l’API, avec validation temporelle, séparation des parcelles, comparaison d’horizons, incertitude, ablations, robustesse, explicabilité, détection hors domaine et documentation de gouvernance. Les scores doivent être lus comme ceux d’un prototype de recherche responsable, et non comme une validation agronomique définitive.",
        "",
    ]
    return "\n".join(lines)


def model_card(horizon: str, result: dict[str, Any]) -> str:
    metrics = result["temporal_metrics"]
    interval = result["conformal_interval"]
    return f"""# Model Card — AgriPredict AI {horizon}

## Identification

- Version : `1.0.0`
- Horizon : `{horizon}`
- Modèle : `{result['selected_model']}`
- Tâche : régression de la date de récolte du blé
- Sortie : jour de l’année
- Domaine : Centre-Val de Loire

## Sélection et validation

- Années de développement : {result['evaluation_protocol']['development_years']}
- Année de calibration : {result['evaluation_protocol']['calibration_year']}
- Année de test : {result['evaluation_protocol']['test_year']}
- Sélection : GroupKFold par parcelle, sans consultation du test

## Performance sur le test chronologique

- MAE : {metrics['mae_days']:.3f} jours
- RMSE : {metrics['rmse_days']:.3f} jours
- R² : {metrics['r2']:.3f}
- Prédictions à ±5 jours : {metrics['within_5_days']:.1%}
- Prédictions à ±7 jours : {metrics['within_7_days']:.1%}
- IC bootstrap 95 % du MAE : [{result['bootstrap_mae_ci95']['lower']:.3f}; {result['bootstrap_mae_ci95']['upper']:.3f}]

## Incertitude

- Méthode : split-conformal
- Couverture nominale : 90 %
- Couverture observée : {interval['empirical_test_coverage']:.1%}
- Largeur moyenne : {interval['mean_width_days']:.2f} jours

## Usage prévu

Aide à la planification logistique et à l’analyse expérimentale. Le modèle ne déclenche aucune récolte automatiquement.

## Usages interdits ou non validés

- autre culture ;
- autre région sans validation externe ;
- décision de récolte autonome ;
- interprétation causale des importances ;
- présentation de la cible dérivée comme une observation terrain directe.

## Données et risques

Les identifiants, variables de pic, variables DOY et agrégats AMJ à risque sont exclus du modèle officiel. Les détails figurent dans `metadata.json` et le rapport final.
"""


def data_card(payload: dict[str, Any]) -> str:
    return f"""# Data Card — AgriPredict AI

## Périmètre

- Culture : blé
- Région : Centre-Val de Loire, France
- Unité : parcelle × année
- Cible : `harvest_doy_derived`
- Nature de la cible : dérivée
- Parcelles-années communes aux deux horizons : {payload['dataset_alignment']['common_parcel_years']}

## Sources

- données parcellaires françaises ;
- SoilGrids ;
- NASA POWER ;
- Sentinel-1 ;
- Sentinel-2 ;
- Céré'Obs et références régionales ;
- jeux combinés et ML distribués via Kaggle.

Le registre détaillé des URLs figure dans `docs/data_sources.md` et `configs/data/datasets.json`.

## Horizons

- 31 mai : variables disponibles ou supposées disponibles avant le 31 mai ;
- 15 juin : variables disponibles ou supposées disponibles avant le 15 juin.

## Contrôles

- unicité de `parcelle_uid × year` ;
- alignement des cibles entre horizons ;
- exclusion des identifiants ;
- exclusion conservatrice des pics, DOY et agrégats AMJ non prouvés ;
- test chronologique ;
- validation groupée par parcelle ;
- suivi des valeurs manquantes et des modalités.

## Limites

La construction complète de la cible dérivée doit rester documentée et auditée. Les données ne démontrent pas une généralisation nationale ou internationale. Les données distribuées sur Kaggle restent soumises aux licences des jeux et sources originales.
"""


def defense_deck(payload: dict[str, Any]) -> str:
    may = payload["horizons"]["may31"]["temporal_metrics"]
    june = payload["horizons"]["june15"]["temporal_metrics"]
    return f"""# Soutenance — plan de 15 diapositives

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
MAE {may['mae_days']:.2f} jours, RMSE {may['rmse_days']:.2f}, R² {may['r2']:.3f}.

## 10. Résultat 15 juin
MAE {june['mae_days']:.2f} jours, RMSE {june['rmse_days']:.2f}, R² {june['r2']:.3f}.

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
"""


def reproducibility_checklist() -> str:
    return """# Checklist de reproductibilité

- [x] Données finales présentes dans `data/`.
- [x] Manifeste des sources Kaggle.
- [x] Audit automatisé.
- [x] Seeds fixées.
- [x] Test chronologique séparé.
- [x] Sélection du modèle sans test.
- [x] GroupKFold par parcelle.
- [x] Intervalles conformes.
- [x] Ablations.
- [x] Robustesse.
- [x] OOD.
- [x] API et interface.
- [x] Tests et CI.
- [x] Docker.
- [x] Data Card et Model Cards.
- [x] Rapport et plan de soutenance.

## Commande unique

```bash
make final
```

## Services

```bash
docker compose up --build
```
"""


def demo_script() -> str:
    return """# Script de démonstration — 5 à 7 minutes

1. Présenter la page de statut et les deux horizons disponibles.
2. Charger une ligne de référence ou une parcelle de démonstration.
3. Lancer la prédiction au 31 mai.
4. Montrer la date, le DOY et l’intervalle à 90 %.
5. Afficher les facteurs globaux et rappeler qu’ils ne sont pas causaux.
6. Lancer la même parcelle au 15 juin.
7. Comparer l’écart de précision attendu et le délai d’anticipation.
8. Montrer le diagnostic hors domaine.
9. Ouvrir `/docs` de FastAPI et exécuter `/health` puis `/model-info`.
10. Conclure avec les limites : cible dérivée, région unique et validation humaine.

## Solution de secours

Conserver les réponses JSON d’exemple, le rapport final et des captures de l’interface pour une démonstration sans réseau.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts/models")
    parser.add_argument("--report-dir", default="reports/final")
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    output_root = Path(args.output)
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    raw_frames = {horizon: load_dataset(path) for horizon, path in DATASETS.items()}
    frames, common_keys = align_frames(raw_frames)

    horizons: dict[str, dict[str, Any]] = {}
    predictions: dict[str, pd.DataFrame] = {}
    for horizon, frame in frames.items():
        result, prediction_frame = evaluate_horizon(
            horizon,
            frame,
            output_root,
            random_state=args.random_state,
        )
        horizons[horizon] = result
        predictions[horizon] = prediction_frame

    may_prediction = predictions["may31"].sort_values(KEYS).reset_index(drop=True)
    june_prediction = predictions["june15"].sort_values(KEYS).reset_index(drop=True)
    if not may_prediction[KEYS].equals(june_prediction[KEYS]):
        raise ValueError("Final test predictions are not aligned between horizons")
    if not np.allclose(may_prediction["actual_doy"], june_prediction["actual_doy"]):
        raise ValueError("Final test targets differ between horizons")

    comparison = paired_horizon_bootstrap(
        may_prediction["actual_doy"].to_numpy(),
        may_prediction["predicted_doy"].to_numpy(),
        june_prediction["predicted_doy"].to_numpy(),
        random_state=args.random_state,
    )
    payload = {
        "generated_at": utc_now(),
        "version": "1.0.0",
        "project": "AgriPredict AI — aivancity AI Clinic 2026",
        "dataset_alignment": {
            "common_parcel_years": int(len(common_keys)),
            "target_equal_count": int(
                np.isclose(frames["may31"][TARGET], frames["june15"][TARGET], equal_nan=True).sum()
            ),
            "target_different_count": int(
                (~np.isclose(frames["may31"][TARGET], frames["june15"][TARGET], equal_nan=True)).sum()
            ),
        },
        "horizons": horizons,
        "horizon_comparison": comparison,
        "scientific_status": (
            "Complete research prototype. External agronomic validation and direct parcel-level ground truth "
            "remain required before operational use."
        ),
    }

    (report_dir / "final_evaluation.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=json_default),
        encoding="utf-8",
    )
    (report_dir / "FINAL_REPORT.md").write_text(final_report_markdown(payload), encoding="utf-8")
    (report_dir / "DATA_CARD.md").write_text(data_card(payload), encoding="utf-8")
    for horizon, result in horizons.items():
        (report_dir / f"MODEL_CARD_{horizon.upper()}.md").write_text(
            model_card(horizon, result), encoding="utf-8"
        )
    (report_dir / "DEFENSE_15_SLIDES.md").write_text(defense_deck(payload), encoding="utf-8")
    (report_dir / "DEMO_SCRIPT.md").write_text(demo_script(), encoding="utf-8")
    (report_dir / "REPRODUCIBILITY_CHECKLIST.md").write_text(
        reproducibility_checklist(), encoding="utf-8"
    )

    comparison_frame = may_prediction[KEYS + ["actual_doy", "predicted_doy", "absolute_error_days"]].rename(
        columns={
            "predicted_doy": "predicted_doy_may31",
            "absolute_error_days": "absolute_error_may31",
        }
    )
    comparison_frame = comparison_frame.merge(
        june_prediction[KEYS + ["predicted_doy", "absolute_error_days"]].rename(
            columns={
                "predicted_doy": "predicted_doy_june15",
                "absolute_error_days": "absolute_error_june15",
            }
        ),
        on=KEYS,
        validate="one_to_one",
    )
    comparison_frame["delta_absolute_error_june_minus_may"] = (
        comparison_frame["absolute_error_june15"] - comparison_frame["absolute_error_may31"]
    )
    comparison_frame.to_csv(report_dir / "horizon_test_comparison.csv", index=False)

    print(metrics_table(horizons))
    print(f"\nFinal deliverables written to {report_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
