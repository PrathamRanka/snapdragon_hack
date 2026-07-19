import asyncio
from dataclasses import dataclass

import numpy as np

from formfusion.config import Settings
from formfusion.contracts.http import ProjectionCalibrationRequest
from formfusion.pipeline.formfusion import FormFusionPipeline, ProjectionCalibration
from formfusion.services.synchronizer import FrameSynchronizer


@dataclass(slots=True)
class SessionRuntime:
    synchronizer: FrameSynchronizer
    pipeline: FormFusionPipeline


class RuntimeRegistry:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._runtimes: dict[str, SessionRuntime] = {}
        self._lock = asyncio.Lock()

    async def get(self, session_id: str) -> SessionRuntime:
        async with self._lock:
            runtime = self._runtimes.get(session_id)
            if runtime is None:
                runtime = SessionRuntime(
                    synchronizer=FrameSynchronizer(
                        self._settings.frame_queue_capacity,
                        self._settings.frame_sync_tolerance_ms,
                    ),
                    pipeline=FormFusionPipeline(
                        session_id,
                        self._settings.min_keypoint_confidence,
                    ),
                )
                self._runtimes[session_id] = runtime
            return runtime

    async def configure_calibration(
        self, session_id: str, request: ProjectionCalibrationRequest
    ) -> None:
        runtime = await self.get(session_id)
        runtime.pipeline.configure(
            ProjectionCalibration(
                device_a=request.device_a,
                device_b=request.device_b,
                projection_a=np.asarray(request.projection_a, dtype=np.float64),
                projection_b=np.asarray(request.projection_b, dtype=np.float64),
                reprojection_error=request.reprojection_error,
            )
        )

    async def delete(self, session_id: str) -> None:
        async with self._lock:
            self._runtimes.pop(session_id, None)
