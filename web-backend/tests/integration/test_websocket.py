def _join(client, session: dict, device_id: str) -> str:
    response = client.post(
        f"/api/v1/sessions/{session['session_id']}/join",
        json={"join_code": session["join_code"], "device_id": device_id},
    )
    assert response.status_code == 200
    return response.json()["device_token"]


def _frame(
    session_id: str, device_id: str, frame_id: int, captured_at_ms: int, x_offset: float
) -> dict:
    return {
        "schema_version": 1,
        "type": "pose.frame",
        "session_id": session_id,
        "device_id": device_id,
        "frame_id": frame_id,
        "captured_at_ms": captured_at_ms,
        "image": {"width": 640, "height": 480, "rotation_degrees": 0, "mirrored": False},
        "person": {
            "track_id": 1,
            "keypoints": [
                {"id": 5, "x": 0.04 + x_offset, "y": 0.02, "confidence": 0.95},
                {"id": 7, "x": 0.05 + x_offset, "y": 0.04, "confidence": 0.95},
                {"id": 9, "x": 0.06 + x_offset, "y": 0.06, "confidence": 0.95},
            ],
        },
    }


def test_two_devices_receive_pose_result(client) -> None:
    session = client.post("/api/v1/sessions", json={}).json()
    token_a = _join(client, session, "phone-a")
    token_b = _join(client, session, "phone-b")

    calibration = client.put(
        f"/api/v1/sessions/{session['session_id']}/calibration/projections",
        headers={"Authorization": f"Bearer {session['host_token']}"},
        json={
            "device_a": "phone-a",
            "device_b": "phone-b",
            "projection_a": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]],
            "projection_b": [[1.0, 0.0, 0.0, -1.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]],
            "reprojection_error": 0.3,
        },
    )
    assert calibration.status_code == 200

    session_id = session["session_id"]
    with client.websocket_connect(f"/api/v1/ws/sessions/{session_id}?token={token_a}") as socket_a:
        socket_a.send_json(
            {
                "schema_version": 1,
                "type": "device.hello",
                "session_id": session_id,
                "device_id": "phone-a",
                "role": "device",
            }
        )
        assert socket_a.receive_json()["type"] == "session.status"

        with client.websocket_connect(
            f"/api/v1/ws/sessions/{session_id}?token={token_b}"
        ) as socket_b:
            socket_b.send_json(
                {
                    "schema_version": 1,
                    "type": "device.hello",
                    "session_id": session_id,
                    "device_id": "phone-b",
                    "role": "device",
                }
            )
            assert socket_b.receive_json()["type"] == "session.status"

            socket_a.send_json(_frame(session_id, "phone-a", 1, 1_000, 0.0))
            assert socket_a.receive_json()["status"] == "queued"
            socket_b.send_json(_frame(session_id, "phone-b", 2, 1_010, -0.2))
            assert socket_b.receive_json()["status"] == "paired"
            result = socket_b.receive_json()
            assert result["type"] == "pose.result"
            assert result["pairing_delta_ms"] == 10
            assert set(result["joints_3d"]) == {"5", "7", "9"}
