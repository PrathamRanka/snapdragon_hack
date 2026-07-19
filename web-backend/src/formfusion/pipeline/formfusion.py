from dataclasses import dataclass

import numpy as np

from formfusion.contracts.websocket import PoseResult
from formfusion.domain.errors import CalibrationRequired
from formfusion.pipeline.biomechanics import RepCounter, calculate_angle_3d
from formfusion.pipeline.one_euro import OneEuroFilter3D
from formfusion.pipeline.triangulation import triangulate_point
from formfusion.services.synchronizer import SyncedPair


@dataclass(slots=True)
class ProjectionCalibration:
    device_a: str
    device_b: str
    projection_a: np.ndarray
    projection_b: np.ndarray
    reprojection_error: float | None = None


class FormFusionPipeline:
    """Stateful per-session triangulation and biomechanics pipeline."""

    LEFT_SHOULDER = 5
    LEFT_ELBOW = 7
    LEFT_WRIST = 9

    def __init__(self, session_id: str, min_confidence: float) -> None:
        self._session_id = session_id
        self._min_confidence = min_confidence
        self._calibration: ProjectionCalibration | None = None
        self._filters: dict[int, OneEuroFilter3D] = {}
        self._counter = RepCounter()

    @property
    def calibrated(self) -> bool:
        return self._calibration is not None

    def configure(self, calibration: ProjectionCalibration) -> None:
        self._calibration = calibration
        self._filters.clear()
        self._counter = RepCounter()

    def process(self, pair: SyncedPair) -> PoseResult:
        calibration = self._calibration
        if calibration is None:
            raise CalibrationRequired("projection calibration has not been configured")

        frames = {pair.first.device_id: pair.first, pair.second.device_id: pair.second}
        try:
            frame_a = frames[calibration.device_a]
            frame_b = frames[calibration.device_b]
        except KeyError as exc:
            raise CalibrationRequired("connected devices do not match the calibration") from exc

        points_a = {point.id: point for point in frame_a.person.keypoints}
        points_b = {point.id: point for point in frame_b.person.keypoints}
        timestamp = max(frame_a.captured_at_ms, frame_b.captured_at_ms) / 1_000.0
        joints: dict[int, np.ndarray] = {}

        for joint_id in sorted(points_a.keys() & points_b.keys()):
            point_a = points_a[joint_id]
            point_b = points_b[joint_id]
            if min(point_a.confidence, point_b.confidence) < self._min_confidence:
                continue
            raw = triangulate_point(
                (point_a.x, point_a.y),
                (point_b.x, point_b.y),
                calibration.projection_a,
                calibration.projection_b,
            )
            filter_3d = self._filters.setdefault(joint_id, OneEuroFilter3D())
            joints[joint_id] = filter_3d.filter(raw, timestamp)

        angle: float | None = None
        required = {self.LEFT_SHOULDER, self.LEFT_ELBOW, self.LEFT_WRIST}
        if required.issubset(joints):
            angle = calculate_angle_3d(
                joints[self.LEFT_SHOULDER],
                joints[self.LEFT_ELBOW],
                joints[self.LEFT_WRIST],
            )
            rep_count, state = self._counter.update(angle)
        else:
            rep_count, state = self._counter.count, self._counter.state

        return PoseResult(
            session_id=self._session_id,
            source_frame_ids={
                frame_a.device_id: frame_a.frame_id,
                frame_b.device_id: frame_b.frame_id,
            },
            captured_at_ms=max(frame_a.captured_at_ms, frame_b.captured_at_ms),
            joints_3d={str(joint_id): point.tolist() for joint_id, point in joints.items()},
            joint_angle_degrees=angle,
            rep_count=rep_count,
            state=state,
            pairing_delta_ms=pair.delta_ms,
            reprojection_error=calibration.reprojection_error,
        )
