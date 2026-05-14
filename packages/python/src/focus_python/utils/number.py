"""
Author: Sean Froning
Created Date: 5.9.2026
Number field validator utils
"""


class NumberUtils:
    """Field serializers for numbers"""

    @staticmethod
    def _to_float(value) -> float:
        """Coerce Decimal / Optional / numeric to float, treating None as NaN"""
        if value is None:
            return float("nan")
        try:
            return float(value)
        except (TypeError, ValueError):
            return float("nan")
