import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def build_projection_matrix(
    camera_matrix: FloatArray, rotation: FloatArray, translation: FloatArray
) -> FloatArray:
    extrinsic = np.hstack((rotation.reshape(3, 3), translation.reshape(3, 1)))
    return camera_matrix.reshape(3, 3) @ extrinsic


def triangulate_point(
    point_a: tuple[float, float],
    point_b: tuple[float, float],
    projection_a: FloatArray,
    projection_b: FloatArray,
) -> FloatArray:
    x_a, y_a = point_a
    x_b, y_b = point_b
    matrix = np.array(
        [
            x_a * projection_a[2] - projection_a[0],
            y_a * projection_a[2] - projection_a[1],
            x_b * projection_b[2] - projection_b[0],
            y_b * projection_b[2] - projection_b[1],
        ],
        dtype=np.float64,
    )
    _, _, vh = np.linalg.svd(matrix)
    homogeneous = vh[-1]
    if abs(homogeneous[3]) < 1e-12:
        raise ValueError("triangulation produced a point at infinity")
    return np.asarray(homogeneous[:3] / homogeneous[3], dtype=np.float64)
