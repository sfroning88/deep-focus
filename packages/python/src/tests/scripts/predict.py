"""
Author: Sean Froning
Created Date: 5.9.2026
Predict from models testing script
"""

from typing import Any, Dict, List

from ..endpoints import ML_RELOAD_URL, PREDICT_CONTROLLABLE_PRD_URL, endpoint_test
from ..helpers import PREDICT_PRESET_PATH, load_preset_lines


def _parse_preset(lines: List[str]) -> Dict[str, str]:
    """Parse KEY=VALUE preset lines into a dict (later values win)"""
    out: Dict[str, str] = {}
    for ln in lines:
        if "=" not in ln:
            continue
        key, value = ln.split("=", 1)
        out[key.strip()] = value.strip()
    return out


def run_reload_test() -> None:
    """Simulate CRON: POST /api/ml/reload and assert model_ids are returned"""
    print("Model registry reload (CRON simulation) start")

    response: Dict[str, Any] = endpoint_test(
        ML_RELOAD_URL,
        name="ml_reload",
    )

    model_ids: List[str] = list(response.get("model_ids") or [])
    if not model_ids:
        raise RuntimeError("Registry reload returned no model_ids — no winner loaded")

    print(f"Registry reloaded with {len(model_ids)} model(s): {model_ids}")
    print("Model registry reload complete")


def run_prediction_tests() -> None:
    """Hit backend/predict/controllable_prd against a preset property_id and assert the response shape"""
    print("Prediction integration endpoint test start")

    preset = _parse_preset(load_preset_lines(PREDICT_PRESET_PATH))
    property_id = preset.get("property_id")
    if not property_id:
        raise RuntimeError(f"property_id missing from {PREDICT_PRESET_PATH}")

    multi_enabled = preset.get("multi_enabled", "false").lower() == "true"

    payload: Dict[str, Any] = {
        "property_id": property_id,
        "multi_enabled": multi_enabled,
    }

    response: Dict[str, Any] = endpoint_test(
        PREDICT_CONTROLLABLE_PRD_URL,
        name="predict_controllable_prd",
        payload=payload,
    )

    predictions: List[Dict[str, Any]] = list(response.get("predictions") or [])
    if not predictions:
        raise RuntimeError("Prediction endpoint returned no predictions")

    if not multi_enabled and len(predictions) != 1:
        raise RuntimeError(
            f"Expected 1 prediction (single-winner mode), got {len(predictions)}"
        )

    for pred in predictions:
        if pred.get("propertyId") != property_id:
            raise RuntimeError(
                f"Prediction propertyId mismatch: {pred.get('propertyId')} != {property_id}"
            )
        if pred.get("result") is None:
            raise RuntimeError(f"Prediction missing result: {pred}")
        if pred.get("type") != "controllablePrd":
            raise RuntimeError(
                f"Prediction type must be controllablePrd, got {pred.get('type')!r}"
            )
        if not pred.get("modelType"):
            raise RuntimeError(f"Prediction missing modelType: {pred}")
        if not pred.get("modelBatchId"):
            raise RuntimeError(f"Prediction missing modelBatchId: {pred}")

    print(f"Got {len(predictions)} prediction(s) for property {property_id}")
    for pred in predictions:
        print(f"  - {pred.get('modelType')}: {round(float(pred['result']), 2)}")

    print("\nPrediction integration testing complete")
