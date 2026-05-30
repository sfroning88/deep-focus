"""
Author: Sean Froning
Created Date: 5.9.2026
Train Sklearn testing script
"""

from typing import Any, Dict, List

from ..endpoints import SHUFFLE_URL, TRAIN_CONTROLLABLE_PRD_URL, endpoint_test
from ..helpers import wait_for_jobs


def run_training_tests() -> None:
    """Shuffle snapshots into function groups, then train and block until all RQ jobs finish"""
    print("Training integration endpoint test start")

    shuffle_response: Dict[str, Any] = endpoint_test(
        SHUFFLE_URL,
        name="shuffle",
    )

    shuffle_job_id: str = shuffle_response.get("job_id") or ""
    if not shuffle_job_id:
        raise RuntimeError("Shuffle endpoint returned no job_id")

    print(f"Enqueued shuffle job: {shuffle_job_id}")
    wait_for_jobs([shuffle_job_id], timeout=120)

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
