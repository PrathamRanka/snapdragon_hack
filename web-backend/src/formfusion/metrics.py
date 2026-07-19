from prometheus_client import Counter, Gauge, Histogram

ACTIVE_WEBSOCKETS = Gauge(
    "formfusion_active_websockets",
    "Current WebSocket connections",
)
FRAMES_RECEIVED = Counter(
    "formfusion_frames_received_total",
    "Pose frames accepted from devices",
)
FRAMES_PAIRED = Counter(
    "formfusion_frames_paired_total",
    "Pose-frame pairs produced",
)
FRAMES_DROPPED = Counter(
    "formfusion_frames_dropped_total",
    "Frames dropped due to duplication, age, or backpressure",
)
PAIRING_DELTA_MS = Histogram(
    "formfusion_pairing_delta_ms",
    "Capture timestamp delta for synchronized frame pairs",
    buckets=(5, 10, 20, 40, 60, 80, 120, 250, 500),
)
PIPELINE_SECONDS = Histogram(
    "formfusion_pipeline_seconds",
    "Time spent processing a synchronized pose pair",
)
