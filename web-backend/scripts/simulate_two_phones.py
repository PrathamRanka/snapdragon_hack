"""Small manual load/demo client. Requires the backend dev dependencies."""

import argparse
import asyncio
import json
import time

import httpx
import websockets


async def main(base_url: str) -> None:
    async with httpx.AsyncClient(base_url=base_url) as client:
        session = (await client.post("/api/v1/sessions", json={})).raise_for_status().json()
        tokens = {}
        for device_id in ("phone-a", "phone-b"):
            response = await client.post(
                f"/api/v1/sessions/{session['session_id']}/join",
                json={"join_code": session["join_code"], "device_id": device_id},
            )
            tokens[device_id] = response.raise_for_status().json()["device_token"]

        await client.put(
            f"/api/v1/sessions/{session['session_id']}/calibration/projections",
            headers={"Authorization": f"Bearer {session['host_token']}"},
            json={
                "device_a": "phone-a",
                "device_b": "phone-b",
                "projection_a": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]],
                "projection_b": [[1.0, 0.0, 0.0, -1.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]],
            },
        )

    websocket_base = base_url.replace("http://", "ws://").replace("https://", "wss://")
    session_id = session["session_id"]

    async def phone(device_id: str, offset: float) -> None:
        uri = f"{websocket_base}/api/v1/ws/sessions/{session_id}?token={tokens[device_id]}"
        async with websockets.connect(uri) as socket:
            await socket.send(
                json.dumps(
                    {
                        "schema_version": 1,
                        "type": "device.hello",
                        "session_id": session_id,
                        "device_id": device_id,
                        "role": "device",
                    }
                )
            )
            print(device_id, await socket.recv())
            for frame_id in range(30):
                timestamp = int(time.time() * 1_000)
                payload = {
                    "schema_version": 1,
                    "type": "pose.frame",
                    "session_id": session_id,
                    "device_id": device_id,
                    "frame_id": frame_id,
                    "captured_at_ms": timestamp,
                    "image": {
                        "width": 640,
                        "height": 480,
                        "rotation_degrees": 0,
                        "mirrored": False,
                    },
                    "person": {
                        "track_id": 1,
                        "keypoints": [{"id": 5, "x": 0.04 + offset, "y": 0.02, "confidence": 0.95}],
                    },
                }
                await socket.send(json.dumps(payload))
                print(device_id, await socket.recv())
                await asyncio.sleep(1 / 15)

    await asyncio.gather(phone("phone-a", 0.0), phone("phone-b", -0.2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    args = parser.parse_args()
    asyncio.run(main(args.base_url))
