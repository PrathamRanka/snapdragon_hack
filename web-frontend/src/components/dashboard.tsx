"use client";

import { skipToken, useQuery } from "@tanstack/react-query";
import {
  Activity,
  Camera,
  Check,
  CircleGauge,
  Clock3,
  RefreshCcw,
  ShieldCheck,
  TriangleAlert,
  Waves,
} from "lucide-react";
import dynamic from "next/dynamic";
import { useMemo, useState } from "react";
import { useInterval } from "usehooks-ts";

import type { ConnectionConfig } from "@/lib/contracts";
import { sessionQueryOptions } from "@/lib/session-query";
import { useLiveSessionStore } from "@/store/live-session";
import { AngleHistoryChart } from "./angle-history-chart";
import { ConnectionPanel } from "./connection-panel";
import styles from "./dashboard.module.css";
import { LiveSessionBridge } from "./live-session-bridge";

const SkeletonScene = dynamic(() => import("./skeleton-scene"), {
  ssr: false,
  loading: () => <StageMessage title="Preparing 3D viewport" detail="Loading renderer…" />,
});

function StageMessage({ title, detail }: { title: string; detail: string }) {
  return (
    <div className={styles.stageMessage}>
      <div className={styles.stageGlyph}><Waves size={25} /></div>
      <strong>{title}</strong>
      <p>{detail}</p>
    </div>
  );
}

function formatExercise(value?: string) {
  if (!value) return "Exercise not selected";
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function Dashboard() {
  const [config, setConfig] = useState<ConnectionConfig | null>(null);
  const [now, setNow] = useState(0);
  const phase = useLiveSessionStore((state) => state.phase);
  const latest = useLiveSessionStore((state) => state.latest);
  const history = useLiveSessionStore((state) => state.history);
  const error = useLiveSessionStore((state) => state.error);
  const lastMessageAt = useLiveSessionStore((state) => state.lastMessageAt);
  const reset = useLiveSessionStore((state) => state.reset);
  const clearHistory = useLiveSessionStore((state) => state.clearHistory);

  useInterval(() => setNow(Date.now()), 1_000);

  const sessionQuery = useQuery(
    config
      ? sessionQueryOptions(config)
      : { queryKey: ["session", "inactive"], queryFn: skipToken },
  );
  const session = sessionQuery.data;
  const dataAge = lastMessageAt ? now - lastMessageAt : null;
  const stale = dataAge !== null && dataAge > 3_000;
  const devices = session?.device_ids.length ?? 0;

  const stage = useMemo(() => {
    if (!config) {
      return <StageMessage title="Connect a live session" detail="Enter the backend session credentials above." />;
    }
    if (sessionQuery.isError) {
      return <StageMessage title="Session unavailable" detail="The backend did not return this session." />;
    }
    if (phase === "connecting" || phase === "reconnecting") {
      return <StageMessage title="Establishing live link" detail="The dashboard will resume automatically." />;
    }
    if (devices < 2) {
      return <StageMessage title="Waiting for both cameras" detail={`${devices} of 2 pose devices have joined.`} />;
    }
    if (session && !session.calibrated) {
      return <StageMessage title="Calibration required" detail="Complete paired checkerboard capture before 3D reconstruction." />;
    }
    if (!latest) {
      return <StageMessage title="Waiting for synchronized frames" detail="Both phones are connected; no 3D result has arrived yet." />;
    }
    if (stale) {
      return <StageMessage title="Live data paused" detail="The last pose result is stale. Reconnecting without clearing the session." />;
    }
    return <SkeletonScene joints={latest.joints_3d} />;
  }, [config, devices, latest, phase, session, sessionQuery.isError, stale]);

  const quality = latest?.form_quality;
  const qualityLabel = quality === "good" ? "Good rep" : quality === "check" ? "Check form" : "Awaiting assessment";
  const qualityTone = quality === "good" ? styles.good : quality === "check" ? styles.warning : styles.neutral;

  return (
    <main className={styles.shell}>
      <LiveSessionBridge config={config} />
      <header className={styles.header}>
        <div className={styles.brandBlock}>
          <span className={styles.brandMark}><Activity size={20} /></span>
          <div>
            <p>FORMFUSION / MOTION LAB</p>
            <h1>Live biomechanics</h1>
          </div>
        </div>
        <div className={styles.headerMeta}>
          <span><Clock3 size={14} /> {latest ? new Date(latest.captured_at_ms).toLocaleTimeString() : "No frame"}</span>
          <span><ShieldCheck size={14} /> On-device inference</span>
        </div>
      </header>

      <ConnectionPanel
        config={config}
        phase={phase}
        onConnect={(nextConfig) => {
          reset();
          setConfig(nextConfig);
        }}
        onDisconnect={() => {
          setConfig(null);
          reset();
        }}
      />

      {error && (
        <div className={styles.errorBanner} role="alert">
          <TriangleAlert size={17} />
          <span>{error}</span>
        </div>
      )}

      <section className={styles.workspace}>
        <article className={styles.skeletonCard}>
          <div className={styles.cardHeading}>
            <div>
              <span>3D RECONSTRUCTION</span>
              <h2>{formatExercise(session?.exercise)}</h2>
            </div>
            <div className={`${styles.liveBadge} ${stale || !latest ? styles.inactiveBadge : ""}`}>
              <span /> {stale ? "STALE" : latest ? "LIVE" : "STANDBY"}
            </div>
          </div>
          <div className={styles.scene}>{stage}</div>
          <footer className={styles.sceneFooter}>
            <span>Drag to orbit</span>
            <span>{latest ? `${Object.keys(latest.joints_3d).length} joints reconstructed` : "No pose frame"}</span>
          </footer>
        </article>

        <aside className={styles.telemetryColumn}>
          <article className={styles.angleCard}>
            <div className={styles.cardLabel}><CircleGauge size={15} /> TRACKED JOINT ANGLE</div>
            <div className={styles.angleValue}>
              <strong>{latest?.joint_angle_degrees?.toFixed(1) ?? "—"}</strong>
              <span>°</span>
            </div>
            <p>{latest ? `Movement state: ${latest.state}` : "Waiting for a computed angle"}</p>
          </article>

          <article className={styles.repCard}>
            <div>
              <span>REP COUNT</span>
              <strong>{latest?.rep_count ?? "—"}</strong>
            </div>
            <div className={`${styles.qualityPill} ${qualityTone}`}>
              {quality === "good" ? <Check size={16} /> : quality === "check" ? <TriangleAlert size={16} /> : <Waves size={16} />}
              <span>{qualityLabel}</span>
            </div>
            <p>{latest?.form_feedback ?? (quality ? "Assessment received from the backend." : "The backend has not supplied a form-quality result yet.")}</p>
          </article>

          <article className={styles.calibrationCard}>
            <div className={styles.cardHeadingCompact}>
              <div>
                <span>SYSTEM HEALTH</span>
                <h3>Calibration</h3>
              </div>
              <span className={session?.calibrated ? styles.healthGood : styles.healthPending}>
                {session?.calibrated ? "READY" : "PENDING"}
              </span>
            </div>
            <div className={styles.calibrationGauge}>
              <div className={styles.gaugeRail}><span style={{ width: latest?.reprojection_error !== null && latest?.reprojection_error !== undefined ? `${Math.max(4, Math.min(100, 100 - latest.reprojection_error * 40))}%` : "0%" }} /></div>
              <div className={styles.gaugeReadout}>
                <span>Reprojection error</span>
                <strong>{latest?.reprojection_error?.toFixed(4) ?? "—"}<small> px</small></strong>
              </div>
            </div>
            <div className={styles.healthRows}>
              <span><Camera size={14} /> Cameras <strong>{devices}/2</strong></span>
              <span><Waves size={14} /> Pair delta <strong>{latest ? `${latest.pairing_delta_ms} ms` : "—"}</strong></span>
            </div>
          </article>
        </aside>
      </section>

      <section className={styles.historyCard}>
        <div className={styles.historyHeader}>
          <div>
            <span>SESSION TRACE</span>
            <h2>Angle over time</h2>
          </div>
          <button type="button" className={styles.ghostButton} onClick={clearHistory} disabled={!history.length}>
            <RefreshCcw size={14} /> Clear trace
          </button>
        </div>
        <div className={styles.chartWrap}><AngleHistoryChart history={history} /></div>
      </section>
    </main>
  );
}
