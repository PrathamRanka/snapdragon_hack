import numpy as np
import pytest

from formfusion.pipeline.biomechanics import RepCounter, calculate_angle_3d
from formfusion.pipeline.triangulation import triangulate_point


def test_calculate_right_angle() -> None:
    angle = calculate_angle_3d([1, 0, 0], [0, 0, 0], [0, 1, 0])
    assert angle == pytest.approx(90.0)


def test_rep_counter_requires_stable_transitions() -> None:
    counter = RepCounter(min_frames_per_state=2)
    counter.update(170)
    assert counter.update(170) == (0, "down")
    counter.update(40)
    assert counter.update(40) == (1, "up")


def test_triangulation_round_trip() -> None:
    projection_a = np.array(
        [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]],
        dtype=np.float64,
    )
    projection_b = np.array(
        [[1, 0, 0, -1], [0, 1, 0, 0], [0, 0, 1, 0]],
        dtype=np.float64,
    )
    recovered = triangulate_point((0.04, 0.02), (-0.16, 0.02), projection_a, projection_b)
    assert recovered == pytest.approx([0.2, 0.1, 5.0], abs=1e-8)
