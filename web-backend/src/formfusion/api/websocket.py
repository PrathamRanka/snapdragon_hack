import time
import uuid

import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from pydantic import ValidationError

from formfusion.contracts.common import ClientRole
from formfusion.contracts.websocket import (
    ClientPing,
    DeviceHello,
    ErrorMessage,
    FrameAck,
    PoseFrame,
    StatusMessage,
)
from formfusion.domain.errors import CalibrationRequired, DomainError, Unauthorized
from formfusion.metrics import (
    ACTIVE_WEBSOCKETS,
    FRAMES_DROPPED,
    FRAMES_PAIRED,
    FRAMES_RECEIVED,
    PAIRING_DELTA_MS,
    PIPELINE_SECONDS,
)

router = APIRouter()
log = structlog.get_logger()


async def _send_error(websocket: WebSocket, code: str, message: str) -> None:
    await websocket.send_json(ErrorMessage(code=code, message=message).model_dump(mode="json"))


@router.websocket("/api/v1/ws/sessions/{session_id}")
async def session_websocket(
    websocket: WebSocket, session_id: str, token: str | None = None
) -> None:
    token_service = websocket.app.state.tokens
    session_service = websocket.app.state.sessions
    registry = websocket.app.state.runtimes
    manager = websocket.app.state.connections
    connection_id = str(uuid.uuid4())

    try:
        if not token:
            raise Unauthorized("token query parameter is required")
        claims = token_service.verify(token)
        if claims.session_id != session_id:
            raise Unauthorized("token does not belong to this session")
        await session_service.get_record(session_id)
    except DomainError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    await manager.register(session_id, websocket)
    ACTIVE_WEBSOCKETS.inc()
    log.info(
        "websocket_connected", connection_id=connection_id, session_id=session_id, role=claims.role
    )

    try:
        raw_hello = await websocket.receive_json()
        hello = DeviceHello.model_validate(raw_hello)
        if hello.session_id != session_id:
            raise Unauthorized("hello session does not match URL")
        if claims.role is ClientRole.DEVICE:
            if hello.role is not ClientRole.DEVICE or hello.device_id != claims.device_id:
                raise Unauthorized("device identity does not match token")
        elif hello.role not in {ClientRole.HOST, ClientRole.DASHBOARD}:
            raise Unauthorized("host token may connect only as host or dashboard")

        record = await session_service.get_record(session_id)
        await websocket.send_json(
            StatusMessage(
                session_id=session_id,
                status="connected",
                connected_devices=len(record.devices),
                calibrated=record.calibrated,
            ).model_dump(mode="json")
        )

        while True:
            raw = await websocket.receive_json()
            message_type = raw.get("type") if isinstance(raw, dict) else None
            if message_type == "ping":
                ClientPing.model_validate(raw)
                await websocket.send_json({"schema_version": 1, "type": "pong"})
                continue
            if message_type != "pose.frame":
                await _send_error(
                    websocket, "unsupported_message", "unsupported WebSocket message type"
                )
                continue
            if claims.role is not ClientRole.DEVICE:
                await _send_error(
                    websocket, "forbidden", "only device connections may send pose frames"
                )
                continue

            frame = PoseFrame.model_validate(raw)
            if frame.session_id != session_id or frame.device_id != claims.device_id:
                raise Unauthorized("frame identity does not match token")

            FRAMES_RECEIVED.inc()
            runtime = await registry.get(session_id)
            outcome = runtime.synchronizer.push(frame)
            if outcome.dropped_frame_ids:
                FRAMES_DROPPED.inc(len(outcome.dropped_frame_ids))
            if outcome.pair is None:
                await websocket.send_json(
                    FrameAck(frame_id=frame.frame_id, status="queued").model_dump(mode="json")
                )
                continue

            FRAMES_PAIRED.inc()
            PAIRING_DELTA_MS.observe(outcome.pair.delta_ms)
            await websocket.send_json(
                FrameAck(frame_id=frame.frame_id, status="paired").model_dump(mode="json")
            )
            started = time.perf_counter()
            try:
                result = runtime.pipeline.process(outcome.pair)
            except CalibrationRequired as exc:
                await _send_error(websocket, exc.code, str(exc))
                continue
            finally:
                PIPELINE_SECONDS.observe(time.perf_counter() - started)
            await manager.broadcast(session_id, result.model_dump(mode="json"))

    except ValidationError as exc:
        await _send_error(websocket, "validation_error", str(exc))
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    except Unauthorized as exc:
        await _send_error(websocket, exc.code, str(exc))
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    except WebSocketDisconnect:
        pass
    except Exception:
        log.exception("websocket_failure", connection_id=connection_id, session_id=session_id)
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except RuntimeError:
            pass
    finally:
        await manager.unregister(session_id, websocket)
        ACTIVE_WEBSOCKETS.dec()
        log.info("websocket_disconnected", connection_id=connection_id, session_id=session_id)
