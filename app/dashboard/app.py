"""Streamlit demonstration interface for AgriPredict AI."""

from __future__ import annotations

import json
import os

import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="AgriPredict AI",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

    :root {
        --forest: #173f35;
        --forest-2: #235b4b;
        --leaf: #79a85b;
        --lime: #ddecbd;
        --cream: #f7f5ed;
        --ink: #17231e;
        --muted: #65736c;
        --line: #dfe5dc;
    }

    html, body, [class*="css"] { font-family: "DM Sans", sans-serif; }
    h1, h2, h3 { font-family: "Manrope", sans-serif !important; letter-spacing: -0.035em; }
    .stApp { background: var(--cream); color: var(--ink); }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] {
        background: var(--forest);
        border-right: 0;
    }
    [data-testid="stSidebar"] * { color: #f7fbf5; }
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] input {
        background: rgba(255,255,255,.09);
        border-color: rgba(255,255,255,.15);
    }
    [data-testid="stSidebar"] .stCaption { color: #bed0c8 !important; }
    .block-container { max-width: 1440px; padding: 2.25rem 3rem 4rem; }
    [data-testid="stAppViewContainer"] > .main { background:
        radial-gradient(circle at 92% 2%, rgba(121,168,91,.10), transparent 24rem),
        var(--cream);
    }

    .brand {
        display:flex; align-items:center; gap:.75rem; margin: .35rem 0 2.4rem;
        font-family:"Manrope", sans-serif; font-weight:800; font-size:1.18rem;
    }
    .brand-mark {
        width:2.25rem; height:2.25rem; display:grid; place-items:center;
        background:var(--lime); color:var(--forest); border-radius:.7rem;
    }
    .eyebrow {
        color:var(--forest-2); font-size:.76rem; font-weight:700;
        text-transform:uppercase; letter-spacing:.14em; margin-bottom:.65rem;
    }
    .hero {
        background:var(--forest); color:white; border-radius:1.6rem;
        padding:2.2rem 2.5rem; margin-bottom:1.25rem; position:relative;
        overflow:hidden; box-shadow: 0 18px 45px rgba(23,63,53,.12);
    }
    .hero:after {
        content:""; position:absolute; width:260px; height:260px; right:-70px; top:-100px;
        border:48px solid rgba(221,236,189,.11); border-radius:50%;
    }
    .hero h1 { color:white; font-size:clamp(2.3rem,4vw,4rem); line-height:1.02; margin:0 0 .9rem; max-width:900px; }
    .hero p { color:#cbdad4; max-width:720px; margin:0; font-size:1.02rem; }
    .pill {
        display:inline-block; margin-top:1.25rem; padding:.42rem .72rem;
        border-radius:99px; background:rgba(221,236,189,.12);
        color:var(--lime); font-size:.78rem; font-weight:700;
    }
    div[data-testid="stMetric"] {
        background:#fff; border:1px solid var(--line); border-radius:1rem;
        padding:1rem 1.15rem; box-shadow:0 5px 18px rgba(35,55,45,.04);
    }
    [data-testid="stMetricLabel"] { color:var(--muted); }
    [data-testid="stMetricValue"] {
        color:var(--forest); font-family:"Manrope", sans-serif; font-weight:700;
    }
    .section-title { margin:2.2rem 0 .2rem; font-size:1.35rem; font-weight:800; }
    .section-copy { color:var(--muted); margin-bottom:1.2rem; }
    .workflow {
        display:grid; grid-template-columns:repeat(3,1fr); gap:1px;
        background:var(--line); border:1px solid var(--line); border-radius:1rem;
        overflow:hidden; margin:1.2rem 0 1.5rem;
    }
    .workflow > div { background:#fff; padding:.9rem 1rem; color:var(--muted); font-size:.85rem; }
    .workflow b {
        width:1.6rem; height:1.6rem; border-radius:50%; display:inline-grid; place-items:center;
        margin-right:.45rem; background:var(--forest); color:#fff; font-size:.72rem;
    }
    .input-panel {
        background:#fff; border:1px solid var(--line); border-radius:1.15rem;
        padding:1rem 1.1rem .35rem; box-shadow:0 10px 30px rgba(35,55,45,.04);
    }
    .signal {
        font-size:.72rem; color:var(--muted); text-transform:uppercase;
        letter-spacing:.12em; font-weight:700; margin:.4rem 0 .75rem;
    }
    .notice {
        background:#eef4e8; border-left:4px solid var(--leaf); color:#365343;
        padding:.9rem 1rem; border-radius:0 .75rem .75rem 0; margin:1.1rem 0 1.5rem;
    }
    .result-card {
        background:linear-gradient(135deg,#e5f0d4,#f3f6e9); border:1px solid #d4e4bf;
        border-radius:1rem; padding:1rem 1.15rem; margin:.75rem 0;
    }
    .status-dot {
        width:.55rem; height:.55rem; border-radius:50%; background:#86c36b;
        box-shadow:0 0 0 4px rgba(134,195,107,.15); display:inline-block; margin-right:.45rem;
    }
    .stButton > button {
        border-radius:.75rem; min-height:2.9rem; font-weight:700;
        border:1px solid #cfd9d1;
    }
    .stButton > button[kind="primary"] {
        background:var(--forest); border-color:var(--forest); color:white;
    }
    .stButton > button[kind="primary"]:hover { background:var(--forest-2); }
    [data-testid="stTextArea"] textarea {
        background:#fff; border-color:var(--line); border-radius:.85rem;
        font-family:"Consolas", monospace; font-size:.82rem;
    }
    [data-testid="stDataFrame"] { border-radius:.9rem; overflow:hidden; }
    footer { visibility:hidden; }
    @media (max-width: 800px) {
        .block-container { padding:1.2rem 1rem 3rem; }
        .hero { padding:1.6rem 1.3rem; }
        .hero h1 { font-size:1.8rem; }
        .workflow { grid-template-columns:1fr; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

api_default = os.getenv("AGRIPREDICT_API_URL", "http://localhost:8000")

with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-mark">A</span>AgriPredict</div>', unsafe_allow_html=True)
    st.caption("PARAMÈTRES DE PRÉVISION")
    horizon = st.selectbox(
        "Horizon d'observation",
        ["may31", "june15"],
        format_func=lambda value: "31 mai" if value == "may31" else "15 juin",
    )
    year = st.number_input("Année de campagne", min_value=2000, max_value=2100, value=2024, step=1)
    st.divider()
    api_url = st.text_input("Adresse de l'API", api_default)
    st.caption("Les données restent locales et sont envoyées uniquement à l'API AgriPredict configurée.")

try:
    health_response = requests.get(f"{api_url.rstrip('/')}/health", timeout=4)
    health_response.raise_for_status()
    health = health_response.json()
    api_available = True
except requests.RequestException:
    health = {}
    api_available = False

st.markdown(
    """
    <div class="eyebrow">Decision intelligence for agriculture</div>
    <section class="hero">
      <h1>La bonne récolte commence par la bonne date.</h1>
      <p>Une estimation multimodale de la date de récolte du blé, conçue pour
      transformer les signaux sol, satellite et météo en décision opérationnelle.</p>
      <span class="pill">AI-powered · Multimodal · Human-controlled</span>
    </section>
    """,
    unsafe_allow_html=True,
)

status_col, scope_col, protocol_col, horizon_col = st.columns(4)
with status_col:
    st.metric("État du service", "Opérationnel" if api_available else "Hors ligne")
    st.caption(
        f"{len(health.get('available_models', []))} modèle(s) chargé(s)"
        if api_available
        else "Démarrez l'API avec make api"
    )
with scope_col:
    st.metric("Territoire", "Centre-Val de Loire")
    st.caption("Blé · parcelle × année")
with protocol_col:
    st.metric("Validation", "Temporelle")
    st.caption("Dernière année en test")
with horizon_col:
    st.metric("Observation", "31 mai" if horizon == "may31" else "15 juin")
    st.caption(f"Campagne {int(year)}")

st.markdown(
    '<div class="notice"><strong>Aide à la décision.</strong> La prédiction complète les observations terrain ; '
    "elle ne remplace pas l'expertise agronomique ni les contraintes météo au jour de la récolte.</div>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="workflow">
      <div><b>1</b>Décrivez la parcelle</div>
      <div><b>2</b>Le modèle croise les signaux</div>
      <div><b>3</b>Planifiez avec une fourchette fiable</div>
    </div>
    """,
    unsafe_allow_html=True,
)

predict_tab, explain_tab, model_tab = st.tabs(["Prévision", "Facteurs clés", "Fiabilité du modèle"])

with predict_tab:
    st.markdown('<div class="section-title">Nouvelle estimation</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Renseignez les caractéristiques connues de la parcelle, puis lancez le calcul.</div>',
        unsafe_allow_html=True,
    )
    input_col, result_col = st.columns([1.05, 1], gap="large")
    with input_col:
        st.markdown('<div class="signal">Données essentielles</div>', unsafe_allow_html=True)
        field_a, field_b = st.columns(2)
        surface = field_a.number_input(
            "Surface de la parcelle",
            min_value=0.1,
            max_value=1000.0,
            value=5.0,
            step=0.5,
            help="Surface cultivée, en hectares.",
        )
        region = field_b.selectbox("Région", ["Centre-Val de Loire"])
        ph = field_a.number_input(
            "pH du sol · 0–5 cm",
            min_value=0.0,
            max_value=140.0,
            value=67.0,
            step=1.0,
            help="Valeur issue de la source sol utilisée par le projet.",
        )
        nitrogen = field_b.number_input(
            "Azote du sol · 0–5 cm",
            min_value=0.0,
            max_value=5000.0,
            value=500.0,
            step=10.0,
        )
        st.markdown('<div class="signal">Signaux satellite & météo</div>', unsafe_allow_html=True)
        field_c, field_d = st.columns(2)
        ndvi = field_c.number_input("NDVI moyen en mai", min_value=-1.0, max_value=1.0, value=0.78, step=0.01)
        radar = field_d.number_input("Radar Sentinel‑1 VV", min_value=-50.0, max_value=20.0, value=-12.0, step=0.5)
        gdd = st.number_input(
            "Degrés-jours cumulés au 31 mai",
            min_value=0.0,
            max_value=10000.0,
            value=2100.0,
            step=50.0,
        )

        features = {
            "SURF_PARC": surface,
            "region": region,
            "phh2o_0-5cm": ph,
            "nitrogen_0-5cm": nitrogen,
            "s2_ndvi_may_mean": ndvi,
            "s1_vv_mean": radar,
            "meteo_gdd_to_may31": gdd,
        }
        with st.expander("Mode expert · modifier le JSON"):
            features_text = st.text_area(
                "Variables transmises à l'API",
                json.dumps(features, indent=2, ensure_ascii=False),
                height=260,
                label_visibility="collapsed",
            )
            try:
                features = json.loads(features_text)
            except json.JSONDecodeError:
                features = None
        predict = st.button("Calculer la date de récolte", type="primary", width="stretch")

    with result_col:
        st.markdown("#### Résultat de la prévision")
        if not predict:
            st.markdown(
                '<div class="result-card"><strong>Prêt à calculer</strong><br>'
                '<span style="color:#607066">La date estimée et son intervalle de confiance apparaîtront ici.</span></div>',
                unsafe_allow_html=True,
            )
        else:
            try:
                if features is None:
                    raise json.JSONDecodeError("Format JSON invalide", features_text, 0)
                response = requests.post(
                    f"{api_url.rstrip('/')}/predict/harvest-date",
                    json={"horizon": horizon, "year": int(year), "features": features},
                    timeout=30,
                )
                response.raise_for_status()
                result = response.json()
                interval = result["prediction_interval_approx_90"]
                st.markdown(
                    f'<div class="result-card"><span class="status-dot"></span><strong>Estimation disponible</strong>'
                    f'<h2 style="margin:.55rem 0 .15rem;color:#173f35">{result["predicted_date"]}</h2>'
                    f'<span style="color:#607066">Fourchette : {interval["low_date"]} → {interval["high_date"]}</span></div>',
                    unsafe_allow_html=True,
                )
                date_col, doy_col, width_col = st.columns(3)
                date_col.metric("Date prévue", result["predicted_date"])
                doy_col.metric("Jour annuel", f"{result['predicted_doy']:.0f}")
                width_col.metric("Marge 90 %", f"± {interval['half_width_days']:.1f} j")
                for warning in result.get("warnings", []):
                    st.warning(warning)
                with st.expander("Voir la réponse technique"):
                    st.json(result)
            except json.JSONDecodeError as exc:
                st.error(f"Le JSON n'est pas valide : {exc}")
            except requests.RequestException as exc:
                st.error(f"Impossible de joindre le service de prévision : {exc}")

with explain_tab:
    st.markdown('<div class="section-title">Ce qui influence la prévision</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Classement global des variables utilisées par le modèle pour cet horizon.</div>',
        unsafe_allow_html=True,
    )
    if st.button("Charger l'importance des variables", width="content"):
        try:
            response = requests.get(f"{api_url.rstrip('/')}/explain/{horizon}", timeout=15)
            response.raise_for_status()
            explanation = response.json()
            importance = explanation.get("global_feature_importance", [])
            if importance:
                importance_frame = pd.DataFrame(importance)
                numeric_columns = importance_frame.select_dtypes(include="number").columns
                if len(numeric_columns):
                    label_columns = [column for column in importance_frame.columns if column not in numeric_columns]
                    chart_frame = importance_frame.head(12)
                    if label_columns:
                        chart_frame = chart_frame.set_index(label_columns[0])
                    st.bar_chart(chart_frame[numeric_columns[0]], color="#79a85b")
                st.dataframe(importance_frame, width="stretch", hide_index=True)
            else:
                st.warning("Aucune importance disponible. Exécutez d'abord make final.")
            st.caption(explanation.get("caution", ""))
        except requests.RequestException as exc:
            st.error(f"Impossible de charger l'explication : {exc}")
    else:
        st.info("Chargez les facteurs clés pour visualiser les signaux dominants du modèle.")

with model_tab:
    st.markdown('<div class="section-title">Carte d’identité du modèle</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Performances observées sur la dernière année tenue à l’écart de l’entraînement.</div>',
        unsafe_allow_html=True,
    )
    if st.button("Afficher les indicateurs du modèle", width="content"):
        try:
            response = requests.get(f"{api_url.rstrip('/')}/model-info", timeout=15)
            response.raise_for_status()
            model_info = response.json()
            metadata = model_info.get("metadata", {}).get(horizon, {})
            if metadata:
                temporal = metadata.get("temporal_metrics", {})
                model_col, mae_col, test_col = st.columns(3)
                model_col.metric("Modèle retenu", metadata.get("selected_model", "—").replace("_", " ").title())
                mae_col.metric("Erreur absolue", f"{temporal.get('mae_days', float('nan')):.2f} jours")
                test_year = metadata.get("evaluation_protocol", {}).get("test_year", metadata.get("test_year", "—"))
                test_col.metric("Année de test", test_year)
            with st.expander("Métadonnées complètes"):
                st.json(model_info)
        except requests.RequestException as exc:
            st.error(f"Impossible de lire les informations du modèle : {exc}")
    else:
        st.info("Affichez les indicateurs pour consulter le modèle sélectionné et son erreur mesurée.")

st.divider()
st.caption(
    "AgriPredict AI v1.0.0 · Clinique IA d’aivancity 2026 · "
    "Prototype de recherche — la décision finale de récolte reste humaine."
)
