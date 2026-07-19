from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike


def calculate_angle_3d(point_a: ArrayLike, point_b: ArrayLike, point_c: ArrayLike) -> float:
    vector_a = np.asarray(point_a, dtype=np.float64) - np.asarray(point_b, dtype=np.float64)
    vector_c = np.asarray(point_c, dtype=np.float64) - np.asarray(point_b, dtype=np.float64)
    denominator = float(np.linalg.norm(vector_a) * np.linalg.norm(vector_c))
    if denominator <= 1e-12:
        raise ValueError("angle requires non-zero adjacent vectors")
    cosine = float(np.clip(np.dot(vector_a, vector_c) / denominator, -1.0, 1.0))
    return float(np.degrees(np.arccos(cosine)))


@dataclass(slots=True)
class RepCounter:
    down_threshold: float = 160.0
    up_threshold: float = 50.0
    min_frames_per_state: int = 3
    count: int = 0
    state: str = "unknown"
    _candidate: str = "unknown"
    _candidate_frames: int = 0

    def update(self, angle: float) -> tuple[int, str]:
        candidate = self.state
        if angle >= self.down_threshold:
            candidate = "down"
        elif angle <= self.up_threshold:
            candidate = "up"

        if candidate == self.state:
            self._candidate = candidate
            self._candidate_frames = 0
            return self.count, self.state

        if candidate != self._candidate:
            self._candidate = candidate
            self._candidate_frames = 1
            return self.count, self.state

        self._candidate_frames += 1
        if self._candidate_frames >= self.min_frames_per_state:
            previous = self.state
            self.state = candidate
            self._candidate_frames = 0
            if previous == "down" and self.state == "up":
                self.count += 1
        return self.count, self.state
