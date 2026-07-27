"""Streamlit demonstration interface for AgriPredict AI."""

from __future__ import annotations

import json

import requests
import streamlit as st

st.set_page_config(page_title="AgriPredict AI", page_icon="🌾", layout="wide")
st.title("🌾 AgriPredict AI")
st.caption("Clinique IA d’aivancity 2026 — prévision multimodale de la date de récolte du blé")

api_url = st.sidebar.text_input("API URL", "http://localhost:8000")
horizon = st.sidebar.selectbox("Horizon", ["may31", "june15"], format_func=lambda x: "31 mai" if x == "may31" else "15 juin")
year = st.sidebar.number_input("Année", min_value=2000, max_value=2100, value=2024, step=1)

st.info(
    "Le modèle est limité aux parcelles de blé du Centre-Val de Loire. "
    "La cible est dérivée et la sortie constitue une aide à la planification, pas une certitude terrain."
)

example = {
    "SURF_PARC": 5.0,
    "region": "Centre-Val de Loire",
    "phh2o_0-5cm": 67.0,
    "nitrogen_0-5cm": 500.0,
    "s2_ndvi_may_mean": 0.78,
    "s1_vv_mean": -12.0,
    "meteo_gdd_to_may31": 2100.0,
}
features_text = st.text_area("Variables de la parcelle au format JSON", json.dumps(example, indent=2, ensure_ascii=False), height=280)

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
            st.metric("Date prévue", result["predicted_date"])
            st.metric("Jour de l’année", f"{result['predicted_doy']:.1f}")
            interval = result["prediction_interval_approx_90"]
            st.success(f"Intervalle approximatif : {interval['low_date']} → {interval['high_date']}")
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
            st.json(response.json())
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
            st.warning("Aucune importance n’est encore disponible. Entraînez les modèles.")
        st.caption(explanation.get("caution", ""))
    except requests.RequestException as exc:
        st.error(f"Impossible de charger l’explication : {exc}")
