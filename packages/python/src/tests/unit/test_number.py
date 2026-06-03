"""
Author: Sean Froning
Created Date: 6.3.2026
Unit tests for NumberUtils decimal clamping
"""

import math
import pytest
from focus_python import NumberUtils


def test_clamp_decimal_rounds_to_scale():
    assert NumberUtils.clamp_decimal(1.23456, precision=6, scale=4) == 1.2346


def test_clamp_decimal_clamps_above_limit():
    assert NumberUtils.clamp_decimal(999999.0, precision=6, scale=4) == 99.9999


def test_clamp_decimal_clamps_below_limit():
    assert NumberUtils.clamp_decimal(-999999.0, precision=6, scale=4) == -99.9999


def test_clamp_decimal_positive_infinity_maps_to_upper_limit():
    assert NumberUtils.clamp_decimal(math.inf, precision=6, scale=4) == 99.9999


def test_clamp_decimal_negative_infinity_maps_to_lower_limit():
    assert NumberUtils.clamp_decimal(-math.inf, precision=6, scale=4) == -99.9999


@pytest.mark.parametrize("value", [None, float("nan")])
def test_clamp_decimal_rejects_nan_or_none(value):
    with pytest.raises(ValueError):
        NumberUtils.clamp_decimal(value, precision=6, scale=4)
