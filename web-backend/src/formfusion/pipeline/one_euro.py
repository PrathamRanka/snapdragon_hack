import math

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def _alpha(cutoff: float, delta_time: float) -> float:
    tau = 1.0 / (2.0 * math.pi * cutoff)
    return 1.0 / (1.0 + tau / delta_time)


class OneEuroFilter3D:
    def __init__(
        self, min_cutoff: float = 1.0, beta: float = 0.1, derivative_cutoff: float = 1.0
    ) -> None:
        self._min_cutoff = min_cutoff
        self._beta = beta
        self._derivative_cutoff = derivative_cutoff
        self._previous_value: FloatArray | None = None
        self._previous_derivative: FloatArray = np.zeros(3, dtype=np.float64)
        self._previous_timestamp: float | None = None

    def filter(self, value: FloatArray, timestamp: float) -> FloatArray:
        value = np.asarray(value, dtype=np.float64)
        if self._previous_value is None or self._previous_timestamp is None:
            self._previous_value = value
            self._previous_timestamp = timestamp
            return value.copy()

        delta_time = max(timestamp - self._previous_timestamp, 1e-6)
        derivative = (value - self._previous_value) / delta_time
        derivative_alpha = _alpha(self._derivative_cutoff, delta_time)
        filtered_derivative = (
            derivative_alpha * derivative + (1.0 - derivative_alpha) * self._previous_derivative
        )
        cutoff = self._min_cutoff + self._beta * float(np.linalg.norm(filtered_derivative))
        value_alpha = _alpha(cutoff, delta_time)
        filtered = value_alpha * value + (1.0 - value_alpha) * self._previous_value

        self._previous_value = filtered
        self._previous_derivative = filtered_derivative
        self._previous_timestamp = timestamp
        return filtered.copy()
