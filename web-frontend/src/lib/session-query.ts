import { queryOptions } from "@tanstack/react-query";

import type { ConnectionConfig, SessionStatus } from "./contracts";

async function fetchSession(config: ConnectionConfig): Promise<SessionStatus> {
  const response = await fetch(
    `${config.backendUrl.replace(/\/$/, "")}/api/v1/sessions/${encodeURIComponent(config.sessionId)}`,
  );
  if (!response.ok) throw new Error("The session could not be loaded from the backend.");
  return response.json() as Promise<SessionStatus>;
}

export function sessionQueryOptions(config: ConnectionConfig) {
  return queryOptions({
    queryKey: ["session", config.backendUrl, config.sessionId],
    queryFn: () => fetchSession(config),
    refetchInterval: 5_000,
  });
}

