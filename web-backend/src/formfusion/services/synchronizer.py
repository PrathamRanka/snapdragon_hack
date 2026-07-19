from dataclasses import dataclass

from formfusion.contracts.websocket import PoseFrame


@dataclass(frozen=True, slots=True)
class SyncedPair:
    first: PoseFrame
    second: PoseFrame
    delta_ms: int


@dataclass(frozen=True, slots=True)
class SyncOutcome:
    pair: SyncedPair | None
    dropped_frame_ids: tuple[int, ...] = ()


class FrameSynchronizer:
    """Pairs nearest frames from two devices while keeping every queue bounded."""

    def __init__(self, capacity: int, tolerance_ms: int) -> None:
        self._capacity = capacity
        self._tolerance_ms = tolerance_ms
        self._queues: dict[str, list[PoseFrame]] = {}
        self._recent_ids: dict[str, set[int]] = {}

    def push(self, frame: PoseFrame) -> SyncOutcome:
        recent = self._recent_ids.setdefault(frame.device_id, set())
        if frame.frame_id in recent:
            return SyncOutcome(pair=None, dropped_frame_ids=(frame.frame_id,))

        queue = self._queues.setdefault(frame.device_id, [])
        queue.append(frame)
        queue.sort(key=lambda item: (item.captured_at_ms, item.frame_id))
        recent.add(frame.frame_id)

        dropped: list[int] = []
        while len(queue) > self._capacity:
            old = queue.pop(0)
            recent.discard(old.frame_id)
            dropped.append(old.frame_id)

        device_ids = sorted(device_id for device_id, items in self._queues.items() if items)
        if len(device_ids) < 2:
            return SyncOutcome(pair=None, dropped_frame_ids=tuple(dropped))

        device_a, device_b = device_ids[:2]
        queue_a = self._queues[device_a]
        queue_b = self._queues[device_b]
        best: tuple[int, int, int] | None = None
        for index_a, candidate_a in enumerate(queue_a):
            for index_b, candidate_b in enumerate(queue_b):
                delta = abs(candidate_a.captured_at_ms - candidate_b.captured_at_ms)
                if best is None or delta < best[0]:
                    best = (delta, index_a, index_b)

        if best is not None and best[0] <= self._tolerance_ms:
            delta, index_a, index_b = best
            first = queue_a.pop(index_a)
            second = queue_b.pop(index_b)
            self._recent_ids[device_a].discard(first.frame_id)
            self._recent_ids[device_b].discard(second.frame_id)
            return SyncOutcome(SyncedPair(first, second, delta), tuple(dropped))

        newest = max(items[-1].captured_at_ms for items in self._queues.values() if items)
        cutoff = newest - self._tolerance_ms
        for device_id, items in self._queues.items():
            while items and items[0].captured_at_ms < cutoff:
                old = items.pop(0)
                self._recent_ids[device_id].discard(old.frame_id)
                dropped.append(old.frame_id)
        return SyncOutcome(pair=None, dropped_frame_ids=tuple(dropped))

    @property
    def depths(self) -> dict[str, int]:
        return {device_id: len(items) for device_id, items in self._queues.items()}
