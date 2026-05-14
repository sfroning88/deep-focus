"""
Author: Sean Froning
Created Date: 5.9.2026
Train Sklearn testing script
"""

from typing import Any, Dict, List

from ..endpoints import TRAIN_CONTROLLABLE_PRD_URL, endpoint_test
from ..helpers import wait_for_jobs


def run_training_tests() -> None:
    """Hit ai/train/controllable_prd, then block until each enqueued RQ job finishes"""
    print("Training integration endpoint test start")

    response: Dict[str, Any] = endpoint_test(
        TRAIN_CONTROLLABLE_PRD_URL,
        name="train_controllable_prd",
    )

    job_ids: List[str] = list(response.get("job_ids") or [])
    if not job_ids:
        raise RuntimeError("Training endpoint returned no job_ids")

    print(f"Enqueued {len(job_ids)} training jobs: {job_ids}")
    wait_for_jobs(job_ids, timeout=600)

    print("\nTraining integration testing complete")
