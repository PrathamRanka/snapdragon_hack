# Operations

## Runtime topology

Backend v1 intentionally runs as one application worker because frame queues, One-Euro filters,
and rep counters are stateful per live session. Do not add multiple Uvicorn workers until Redis
session ownership and session-affinity routing are implemented.

Terminate TLS at the deployment platform or reverse proxy and forward WebSocket upgrades to the
single backend worker.

## Environment

- `FORMFUSION_ENVIRONMENT`: `development`, `test`, or `production`.
- `FORMFUSION_JWT_SECRET`: minimum 32 random characters in production.
- `FORMFUSION_ALLOWED_ORIGINS`: JSON array of dashboard origins.
- `FORMFUSION_SESSION_TTL_SECONDS`: session lifetime.
- `FORMFUSION_FRAME_QUEUE_CAPACITY`: hard queue bound per device.
- `FORMFUSION_FRAME_SYNC_TOLERANCE_MS`: maximum capture-time difference.
- `FORMFUSION_MIN_KEYPOINT_CONFIDENCE`: minimum confidence on both phones.

## Health and metrics

- `/health/live`: process is responding.
- `/health/ready`: required services were initialized.
- `/metrics`: Prometheus metrics for WebSockets, frames, pairing delta, drops, and processing time.

Never log bearer/device tokens, join codes, raw calibration images, or complete pose payloads.

## Deployment checks

1. Use a non-default secret and `FORMFUSION_ENVIRONMENT=production`.
2. Restrict dashboard origins.
3. Confirm the proxy supports WebSocket upgrades and has an idle timeout longer than the ping
   interval used by clients.
4. Keep one application worker.
5. Load the correct projection matrices for the actual physical device pair.
6. Confirm both devices use capture timestamps from the same clock domain or apply clock-offset
   estimation before relying on a tight synchronization tolerance.

