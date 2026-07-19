export type ConnectionConfig = {
  backendUrl: string;
  sessionId: string;
  token: string;
};

export type ConnectionPhase =
  | "idle"
  | "connecting"
  | "connected"
  | "reconnecting"
  | "closed"
  | "error";

export type PoseResult = {
  schema_version: 1;
  type: "pose.result";
  session_id: string;
  source_frame_ids: Record<string, number>;
  captured_at_ms: number;
  joints_3d: Record<string, [number, number, number]>;
  joint_angle_degrees: number | null;
  rep_count: number;
  state: string;
  pairing_delta_ms: number;
  reprojection_error: number | null;
  form_quality?: "good" | "check" | "unknown";
  form_feedback?: string | null;
};

export type SessionStatus = {
  session_id: string;
  exercise: string;
  device_ids: string[];
  calibrated: boolean;
  expires_at: string;
};

export type SocketError = {
  schema_version: 1;
  type: "error";
  code: string;
  message: string;
  request_id: string | null;
};

export type SessionSocketStatus = {
  schema_version: 1;
  type: "session.status";
  session_id: string;
  status: string;
  connected_devices: number;
  calibrated: boolean;
};

export type SocketMessage =
  | PoseResult
  | SocketError
  | SessionSocketStatus
  | { schema_version: 1; type: "pong" };

export type AngleSample = {
  capturedAt: number;
  elapsedSeconds: number;
  angle: number;
  rep: number;
  quality: PoseResult["form_quality"];
};

