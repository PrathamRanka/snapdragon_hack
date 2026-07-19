"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Cable, Eye, EyeOff, LoaderCircle, Unplug } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";

import {
  connectionSchema,
  type ConnectionFormValues,
} from "@/lib/connection-schema";
import type { ConnectionConfig, ConnectionPhase } from "@/lib/contracts";
import styles from "./dashboard.module.css";

type Props = {
  config: ConnectionConfig | null;
  phase: ConnectionPhase;
  onConnect: (config: ConnectionConfig) => void;
  onDisconnect: () => void;
};

export function ConnectionPanel({ config, phase, onConnect, onDisconnect }: Props) {
  const [showToken, setShowToken] = useState(false);
  const [expanded, setExpanded] = useState(config === null);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ConnectionFormValues>({
    resolver: zodResolver(connectionSchema),
    defaultValues: {
      backendUrl: process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000",
      sessionId: "",
      token: "",
    },
  });

  const connecting = phase === "connecting" || phase === "reconnecting";

  return (
    <section className={styles.connectionPanel} aria-label="Backend connection">
      <button
        type="button"
        className={styles.connectionSummary}
        onClick={() => setExpanded((current) => !current)}
        aria-expanded={expanded}
      >
        <span className={`${styles.statusDot} ${styles[`status_${phase}`]}`} />
        <span>
          <strong>{config ? config.sessionId : "No live session"}</strong>
          <small>{phase === "idle" ? "Connect to begin" : phase}</small>
        </span>
        <span className={styles.connectionAction}>{expanded ? "Close" : "Configure"}</span>
      </button>

      {expanded && (
        <div className={styles.connectionBody}>
          {config ? (
            <div className={styles.connectedDetails}>
              <div>
                <span>Backend</span>
                <strong>{config.backendUrl}</strong>
              </div>
              <button type="button" className={styles.secondaryButton} onClick={onDisconnect}>
                <Unplug size={16} /> Disconnect
              </button>
            </div>
          ) : (
            <form
              className={styles.connectionForm}
              onSubmit={handleSubmit((values) => {
                onConnect(values);
                setExpanded(false);
              })}
            >
              <label>
                <span>Backend URL</span>
                <input {...register("backendUrl")} placeholder="https://api.example.com" />
                {errors.backendUrl && <em>{errors.backendUrl.message}</em>}
              </label>
              <label>
                <span>Session ID</span>
                <input {...register("sessionId")} placeholder="Paste session ID" />
                {errors.sessionId && <em>{errors.sessionId.message}</em>}
              </label>
              <label>
                <span>Dashboard token</span>
                <div className={styles.tokenField}>
                  <input
                    {...register("token")}
                    type={showToken ? "text" : "password"}
                    autoComplete="off"
                    placeholder="Signed host token"
                  />
                  <button
                    type="button"
                    onClick={() => setShowToken((current) => !current)}
                    aria-label={showToken ? "Hide token" : "Show token"}
                  >
                    {showToken ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
                {errors.token && <em>{errors.token.message}</em>}
              </label>
              <button type="submit" className={styles.primaryButton} disabled={connecting}>
                {connecting ? <LoaderCircle className={styles.spin} size={17} /> : <Cable size={17} />}
                Connect live session
              </button>
            </form>
          )}
        </div>
      )}
    </section>
  );
}

