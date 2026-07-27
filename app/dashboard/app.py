"""Streamlit demonstration interface for AgriPredict AI."""

from __future__ import annotations

import json
import os

import requests
import streamlit as st

st.set_page_config(page_title="AgriPredict AI", page_icon="🌾", layout="wide")
st.title("🌾 AgriPredict AI")
st.caption("Clinique IA d’aivancity 2026 — prévision multimodale de la date de récolte du blé")

api_default = os.getenv("AGRIPREDICT_API_URL", "http://localhost:8000")
api_url = st.sidebar.text_input("API URL", api_default)
horizon = st.sidebar.selectbox(
    "Horizon",
    ["may31", "june15"],
    format_func=lambda value: "31 mai" if value == "may31" else "15 juin",
)
year = st.sidebar.number_input("Année", min_value=2000, max_value=2100, value=2024, step=1)

st.info(
    "Le modèle est limité aux parcelles de blé du Centre-Val de Loire. "
    "La cible est dérivée et la sortie constitue une aide à la planification, pas une certitude terrain."
)

status_col, scope_col, protocol_col = st.columns(3)
with status_col:
    try:
        health_response = requests.get(f"{api_url.rstrip('/')}/health", timeout=4)
        health_response.raise_for_status()
        health = health_response.json()
        st.metric("API", "Disponible")
        st.caption(f"Modèles chargés : {', '.join(health.get('available_models', [])) or 'aucun'}")
    except requests.RequestException:
        st.metric("API", "Indisponible")
        st.caption("Lancez `make api` ou `docker compose up --build`.")
with scope_col:
    st.metric("Domaine", "Blé — CVL")
    st.caption("Centre-Val de Loire, parcelle × année")
with protocol_col:
    st.metric("Validation", "Temporelle")
    st.caption("Dernière année test + GroupKFold par parcelle")

example = {
    "SURF_PARC": 5.0,
    "region": "Centre-Val de Loire",
    "phh2o_0-5cm": 67.0,
    "nitrogen_0-5cm": 500.0,
    "s2_ndvi_may_mean": 0.78,
    "s1_vv_mean": -12.0,
    "meteo_gdd_to_may31": 2100.0,
}
features_text = st.text_area(
    "Variables de la parcelle au format JSON",
    json.dumps(example, indent=2, ensure_ascii=False),
    height=280,
)

col_predict, col_info = st.columns(2)
with col_predict:
    if st.button("Prédire la date de récolte", type="primary", use_container_width=True):
        try:
            features = json.loads(features_text)
            response = requests.post(
                f"{api_url.rstrip('/')}/predict/harvest-date",
                json={"horizon": horizon, "year": int(year), "features": features},
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            metric_date, metric_doy, metric_width = st.columns(3)
            metric_date.metric("Date prévue", result["predicted_date"])
            metric_doy.metric("Jour de l’année", f"{result['predicted_doy']:.1f}")
            interval = result["prediction_interval_approx_90"]
            metric_width.metric("Demi-largeur 90 %", f"{interval['half_width_days']:.1f} j")
            st.success(f"Intervalle à 90 % : {interval['low_date']} → {interval['high_date']}")
            if result.get("warnings"):
                for warning in result["warnings"]:
                    st.warning(warning)
            with st.expander("Réponse JSON complète"):
                st.json(result)
        except json.JSONDecodeError as exc:
            st.error(f"JSON invalide : {exc}")
        except requests.RequestException as exc:
            st.error(f"API indisponible ou erreur d’inférence : {exc}")

with col_info:
    if st.button("Afficher les informations du modèle", use_container_width=True):
        try:
            response = requests.get(f"{api_url.rstrip('/')}/model-info", timeout=15)
            response.raise_for_status()
            model_info = response.json()
            metadata = model_info.get("metadata", {}).get(horizon, {})
            if metadata:
                st.metric("Modèle sélectionné", metadata.get("selected_model", "—"))
                temporal = metadata.get("temporal_metrics", {})
                st.metric("MAE test", f"{temporal.get('mae_days', float('nan')):.2f} jours")
                st.caption(
                    f"Année test : {metadata.get('evaluation_protocol', {}).get('test_year', metadata.get('test_year', '—'))}"
                )
            with st.expander("Métadonnées complètes"):
                st.json(model_info)
        except requests.RequestException as exc:
            st.error(f"Impossible de lire les informations du modèle : {exc}")

st.subheader("Explicabilité globale")
if st.button("Charger les variables importantes"):
    try:
        response = requests.get(f"{api_url.rstrip('/')}/explain/{horizon}", timeout=15)
        response.raise_for_status()
        explanation = response.json()
        importance = explanation.get("global_feature_importance", [])
        if importance:
            st.dataframe(importance, use_container_width=True)
        else:
            st.warning("Aucune importance n’est encore disponible. Entraînez les modèles avec `make final`.")
        st.caption(explanation.get("caution", ""))
    except requests.RequestException as exc:
        st.error(f"Impossible de charger l’explication : {exc}")

st.divider()
st.caption(
    "AgriPredict AI v1.0.0 — Prototype de recherche. La décision finale de récolte reste humaine et doit intégrer les observations terrain."
)
