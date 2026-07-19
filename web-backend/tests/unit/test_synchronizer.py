from formfusion.contracts.common import ImageMetadata, Keypoint
from formfusion.contracts.websocket import PersonPose, PoseFrame
from formfusion.services.synchronizer import FrameSynchronizer


def frame(device_id: str, frame_id: int, timestamp: int) -> PoseFrame:
    return PoseFrame(
        session_id="session",
        device_id=device_id,
        frame_id=frame_id,
        captured_at_ms=timestamp,
        image=ImageMetadata(width=640, height=480),
        person=PersonPose(keypoints=[Keypoint(id=5, x=1.0, y=2.0, confidence=0.9)]),
    )


def test_pairs_nearest_frames() -> None:
    synchronizer = FrameSynchronizer(capacity=4, tolerance_ms=50)
    assert synchronizer.push(frame("a", 1, 1_000)).pair is None
    outcome = synchronizer.push(frame("b", 8, 1_012))
    assert outcome.pair is not None
    assert outcome.pair.delta_ms == 12


def test_queue_is_bounded() -> None:
    synchronizer = FrameSynchronizer(capacity=2, tolerance_ms=10)
    synchronizer.push(frame("a", 1, 1_000))
    synchronizer.push(frame("a", 2, 1_001))
    outcome = synchronizer.push(frame("a", 3, 1_002))
    assert outcome.dropped_frame_ids == (1,)
    assert synchronizer.depths["a"] == 2


def test_duplicate_frame_is_dropped() -> None:
    synchronizer = FrameSynchronizer(capacity=2, tolerance_ms=10)
    synchronizer.push(frame("a", 1, 1_000))
    outcome = synchronizer.push(frame("a", 1, 1_001))
    assert outcome.dropped_frame_ids == (1,)
