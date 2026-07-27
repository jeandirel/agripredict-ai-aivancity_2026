#!/usr/bin/env python3
"""Audit the two final AgriPredict datasets and generate Phase 0 evidence.

Outputs:
- reports/phase0/phase0_data_audit.json
- reports/phase0/phase0_data_audit.md
- reports/phase0/feature_availability_register.csv
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

TARGET = "harvest_doy_derived"
KEY_CANDIDATES = ["parcelle_uid", "year"]
DATASETS = {
    "may31": Path("data/master_ml_final_may31.csv"),
    "june15": Path("data/master_ml_final_june15.csv"),
}
OUT_DIR = Path("reports/phase0")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def json_value(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if math.isnan(float(value)) else float(value)
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    return value


def modality(column: str) -> str:
    if column in {"parcelle_uid", "year", "ID_PARCEL", "SURF_PARC", "region"}:
        return "identity_geography"
    if column.startswith(("phh2o_", "nitrogen_", "soc_", "clay_", "sand_", "silt_", "cec_", "bdod_", "cfvo_", "wv", "ocd_")):
        return "soil"
    if column.startswith("s2_"):
        return "sentinel2"
    if column.startswith("s1_"):
        return "sentinel1"
    if column.startswith("meteo_"):
        return "weather"
    if column == TARGET:
        return "target"
    return "other"


def availability(column: str, dataset_name: str) -> tuple[str, str]:
    """Return (status, rationale) for temporal availability."""
    lower = column.lower()
    if column == TARGET:
        return "target", "Target; never used as an input feature."
    if dataset_name == "may31" and any(token in lower for token in ("june", "_amj_", "to_june", "jun")):
        return "forbidden", "Name suggests June information in the 31-May dataset."
    if column.endswith("_doy") or "_doy_" in column:
        return "manual_review", "Phenological day-of-year feature: verify its observation window and target lineage."
    if "peak" in lower:
        return "manual_review", "Peak statistic: verify that the peak is computed only with observations available by cutoff."
    if dataset_name == "june15" and "_amj_" in lower:
        return "manual_review", "AMJ aggregate must stop on 15 June, not at the end of June."
    return "provisionally_allowed", "No obvious cutoff violation from the column name; pipeline evidence still required."


def audit_dataframe(name: str, path: Path) -> tuple[pd.DataFrame, dict[str, Any], list[dict[str, str]]]:
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path, low_memory=False)
    key_columns = [column for column in KEY_CANDIDATES if column in df.columns]
    duplicate_rows = int(df.duplicated().sum())
    duplicate_keys = int(df.duplicated(subset=key_columns).sum()) if len(key_columns) == len(KEY_CANDIDATES) else None
    target = pd.to_numeric(df[TARGET], errors="coerce") if TARGET in df.columns else pd.Series(dtype=float)
    years = sorted(json_value(v) for v in df["year"].dropna().unique()) if "year" in df.columns else []

    missing = df.isna().sum().sort_values(ascending=False)
    missing_columns = [
        {"column": column, "missing": int(count), "rate": float(count / len(df))}
        for column, count in missing.items()
        if count > 0
    ]
    constant_columns = [column for column in df.columns if df[column].nunique(dropna=False) <= 1]
    numeric = df.select_dtypes(include=["number"])
    infinite_values = int(np.isinf(numeric.to_numpy(dtype=float, na_value=np.nan)).sum()) if not numeric.empty else 0

    feature_register: list[dict[str, str]] = []
    forbidden: list[str] = []
    manual_review: list[str] = []
    for column in df.columns:
        status, rationale = availability(column, name)
        feature_register.append(
            {
                "dataset": name,
                "column": column,
                "modality": modality(column),
                "availability_status": status,
                "rationale": rationale,
            }
        )
        if status == "forbidden":
            forbidden.append(column)
        elif status == "manual_review":
            manual_review.append(column)

    report = {
        "name": name,
        "path": str(path),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": list(df.columns),
        "years": years,
        "year_min": json_value(df["year"].min()) if "year" in df.columns else None,
        "year_max": json_value(df["year"].max()) if "year" in df.columns else None,
        "unique_parcels": int(df["parcelle_uid"].nunique()) if "parcelle_uid" in df.columns else None,
        "unique_regions": sorted(str(v) for v in df["region"].dropna().unique()) if "region" in df.columns else [],
        "duplicate_rows": duplicate_rows,
        "duplicate_parcel_year_keys": duplicate_keys,
        "missing_cells": int(df.isna().sum().sum()),
        "missing_cell_rate": float(df.isna().sum().sum() / max(1, df.shape[0] * df.shape[1])),
        "missing_columns": missing_columns,
        "constant_columns": constant_columns,
        "infinite_numeric_values": infinite_values,
        "target_present": TARGET in df.columns,
        "target_non_null": int(target.notna().sum()),
        "target_missing": int(target.isna().sum()),
        "target_min": json_value(target.min()) if not target.empty else None,
        "target_max": json_value(target.max()) if not target.empty else None,
        "target_mean": json_value(target.mean()) if not target.empty else None,
        "target_median": json_value(target.median()) if not target.empty else None,
        "target_std": json_value(target.std()) if not target.empty else None,
        "forbidden_cutoff_columns": forbidden,
        "manual_temporal_review_columns": manual_review,
        "modalities": {
            group: sum(modality(column) == group for column in df.columns)
            for group in sorted({modality(column) for column in df.columns})
        },
    }
    return df, report, feature_register


def compare_datasets(may31: pd.DataFrame, june15: pd.DataFrame) -> dict[str, Any]:
    may_columns, june_columns = set(may31.columns), set(june15.columns)
    common_columns = sorted(may_columns & june_columns)
    keys = [column for column in KEY_CANDIDATES if column in may31.columns and column in june15.columns]
    comparison: dict[str, Any] = {
        "common_columns": len(common_columns),
        "only_may31_columns": sorted(may_columns - june_columns),
        "only_june15_columns": sorted(june_columns - may_columns),
        "key_columns": keys,
    }
    if len(keys) == len(KEY_CANDIDATES):
        left = may31[keys + ([TARGET] if TARGET in may31.columns else [])].copy()
        right = june15[keys + ([TARGET] if TARGET in june15.columns else [])].copy()
        merged = left.merge(right, on=keys, how="outer", suffixes=("_may31", "_june15"), indicator=True)
        comparison.update(
            {
                "common_keys": int((merged["_merge"] == "both").sum()),
                "only_may31_keys": int((merged["_merge"] == "left_only").sum()),
                "only_june15_keys": int((merged["_merge"] == "right_only").sum()),
            }
        )
        if f"{TARGET}_may31" in merged and f"{TARGET}_june15" in merged:
            common = merged[merged["_merge"] == "both"].copy()
            delta = pd.to_numeric(common[f"{TARGET}_may31"], errors="coerce") - pd.to_numeric(
                common[f"{TARGET}_june15"], errors="coerce"
            )
            comparison.update(
                {
                    "common_target_equal": int(delta.fillna(np.inf).eq(0).sum()),
                    "common_target_different": int(delta.fillna(np.inf).ne(0).sum()),
                    "max_absolute_target_difference": json_value(delta.abs().max()),
                }
            )
    return comparison


def gate_status(reports: dict[str, dict[str, Any]], comparison: dict[str, Any]) -> tuple[str, list[str], list[str]]:
    blockers: list[str] = []
    warnings: list[str] = []
    for name, report in reports.items():
        if not report["target_present"]:
            blockers.append(f"{name}: missing target {TARGET}")
        if report["target_missing"]:
            blockers.append(f"{name}: {report['target_missing']} missing target values")
        if report["duplicate_parcel_year_keys"]:
            blockers.append(f"{name}: {report['duplicate_parcel_year_keys']} duplicate parcel-year keys")
        if report["forbidden_cutoff_columns"]:
            blockers.append(f"{name}: cutoff-forbidden columns: {report['forbidden_cutoff_columns']}")
        if report["manual_temporal_review_columns"]:
            warnings.append(
                f"{name}: {len(report['manual_temporal_review_columns'])} peak/DOY or AMJ columns require lineage review"
            )
        if report["missing_cells"]:
            warnings.append(f"{name}: {report['missing_cells']} missing cells")
    if comparison.get("common_target_different", 0):
        blockers.append(
            f"Targets differ for {comparison['common_target_different']} common parcel-year keys between horizons"
        )
    warnings.append("Manual prerequisite: validate the derivation of harvest_doy_derived from the methodological report/code.")
    if blockers:
        return "BLOCKED", blockers, warnings
    return "PHASE_0_COMPLETE_WITH_PHASE_2_PREREQUISITES", blockers, warnings


def markdown_report(payload: dict[str, Any]) -> str:
    lines = [
        "# AgriPredict AI — Audit automatisé de Phase 0",
        "",
        f"> Généré le `{payload['generated_at']}`.",
        "",
        f"## Décision G0 : `{payload['gate']['status']}`",
        "",
    ]
    if payload["gate"]["blockers"]:
        lines += ["### Blocages", ""] + [f"- {item}" for item in payload["gate"]["blockers"]] + [""]
    lines += ["### Points de vigilance", ""] + [f"- {item}" for item in payload["gate"]["warnings"]] + [""]

    lines += [
        "## Synthèse des datasets",
        "",
        "| Dataset | Lignes | Colonnes | Années | Parcelles | Cible min–max | Manquants | Doublons clé | SHA-256 |",
        "|---|---:|---:|---|---:|---|---:|---:|---|",
    ]
    for name, report in payload["datasets"].items():
        years = ", ".join(str(y) for y in report["years"])
        target_range = f"{report['target_min']}–{report['target_max']}"
        lines.append(
            f"| {name} | {report['rows']} | {report['columns']} | {years} | {report['unique_parcels']} | "
            f"{target_range} | {report['missing_cells']} | {report['duplicate_parcel_year_keys']} | `{report['sha256'][:12]}…` |"
        )

    comparison = payload["comparison"]
    lines += [
        "",
        "## Comparaison 31 mai / 15 juin",
        "",
        f"- Colonnes communes : **{comparison.get('common_columns')}**",
        f"- Colonnes uniquement au 31 mai : `{comparison.get('only_may31_columns', [])}`",
        f"- Colonnes uniquement au 15 juin : `{comparison.get('only_june15_columns', [])}`",
        f"- Clés communes : **{comparison.get('common_keys', 'n/a')}**",
        f"- Clés uniquement au 31 mai : **{comparison.get('only_may31_keys', 'n/a')}**",
        f"- Clés uniquement au 15 juin : **{comparison.get('only_june15_keys', 'n/a')}**",
        f"- Cibles différentes sur clés communes : **{comparison.get('common_target_different', 'n/a')}**",
        "",
        "## Règles scientifiques actées",
        "",
        "- Le MAE en jours est la métrique principale.",
        "- La comparaison des horizons utilise uniquement les parcelles-années communes et les mêmes splits.",
        "- Le test final est chronologique.",
        "- Une validation groupée par `parcelle_uid` est obligatoire.",
        "- Les colonnes de pics, de DOY et d’agrégats AMJ restent interdites au modèle final tant que leur fenêtre de calcul n’est pas prouvée.",
        "- La cible dérivée doit être décrite comme telle dans la Data Card et la Model Card.",
        "",
        "## Fichiers de preuve",
        "",
        "- `reports/phase0/phase0_data_audit.json`",
        "- `reports/phase0/feature_availability_register.csv`",
        "- `configs/data/datasets.json`",
        "- `data/manifests/datasets_download_status.json` lorsque le téléchargement Kaggle a été exécuté.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frames: dict[str, pd.DataFrame] = {}
    reports: dict[str, dict[str, Any]] = {}
    registers: list[dict[str, str]] = []
    for name, path in DATASETS.items():
        frame, report, register = audit_dataframe(name, path)
        frames[name] = frame
        reports[name] = report
        registers.extend(register)

    comparison = compare_datasets(frames["may31"], frames["june15"])
    status, blockers, warnings = gate_status(reports, comparison)
    payload = {
        "generated_at": utc_now(),
        "scope": {
            "crop": "wheat",
            "region": "Centre-Val de Loire",
            "task": "parcel-level harvest-date regression",
            "target": TARGET,
            "unit": "day of year",
            "horizons": ["May 31", "June 15"],
        },
        "datasets": reports,
        "comparison": comparison,
        "gate": {"status": status, "blockers": blockers, "warnings": warnings},
    }
    (OUT_DIR / "phase0_data_audit.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=json_value), encoding="utf-8"
    )
    (OUT_DIR / "phase0_data_audit.md").write_text(markdown_report(payload), encoding="utf-8")
    pd.DataFrame(registers).to_csv(OUT_DIR / "feature_availability_register.csv", index=False)
    print(json.dumps(payload["gate"], indent=2, ensure_ascii=False))
    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(main())
