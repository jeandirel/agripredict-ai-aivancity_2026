import pandas as pd

from agripredict.data import TARGET, common_parcel_year_keys, prepare_data, temporal_risk_reason


def sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "parcelle_uid": ["2020_1", "2021_1", "2021_2"],
            "year": [2020, 2021, 2021],
            "ID_PARCEL": [1, 1, 2],
            "SURF_PARC": [2.0, 2.0, 3.0],
            "s2_peak_doy": [120, 121, 122],
            "meteo_t_amj_mean": [12.0, 13.0, 14.0],
            "s2_ndvi_may_mean": [0.7, 0.8, 0.6],
            TARGET: [180.0, 182.0, 178.0],
            "region": ["Centre-Val de Loire"] * 3,
        }
    )


def test_temporal_risk_filter_is_conservative() -> None:
    prepared = prepare_data(sample_frame(), "may31")
    assert TARGET not in prepared.X.columns
    assert "ID_PARCEL" not in prepared.X.columns
    assert "s2_peak_doy" not in prepared.X.columns
    assert "meteo_t_amj_mean" not in prepared.X.columns
    assert "s2_ndvi_may_mean" in prepared.X.columns


def test_temporal_risk_reason() -> None:
    assert temporal_risk_reason("s2_peak_ndvi", "june15") is not None
    assert temporal_risk_reason("meteo_t_amj_mean", "june15") is not None
    assert temporal_risk_reason("s2_ndvi_may_mean", "may31") is None


def test_common_keys() -> None:
    left = sample_frame()
    right = sample_frame().iloc[:2]
    keys = common_parcel_year_keys(left, right)
    assert len(keys) == 2
