"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { AngleSample } from "@/lib/contracts";
import styles from "./dashboard.module.css";

export function AngleHistoryChart({ history }: { history: AngleSample[] }) {
  if (!history.length) {
    return (
      <div className={styles.chartEmpty}>
        <span>ANGLE / TIME</span>
        <strong>Waiting for the first computed angle</strong>
        <p>The trace begins when synchronized frames contain the required joints.</p>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={history} margin={{ top: 12, right: 8, bottom: 0, left: -18 }}>
        <CartesianGrid vertical={false} stroke="#dcdae3" strokeDasharray="2 5" />
        <XAxis
          dataKey="elapsedSeconds"
          tickFormatter={(value: number) => `${Math.round(value)}s`}
          tick={{ fill: "#777989", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          minTickGap={32}
        />
        <YAxis
          domain={[0, 180]}
          ticks={[0, 45, 90, 135, 180]}
          tick={{ fill: "#777989", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          cursor={{ stroke: "#9c9eb7", strokeDasharray: "3 3" }}
          contentStyle={{
            background: "#181a31",
            border: 0,
            borderRadius: 12,
            color: "#fff",
            fontSize: 12,
          }}
          formatter={(value) => [`${Number(value).toFixed(1)}°`, "Joint angle"]}
          labelFormatter={(value) => `${Number(value).toFixed(1)} seconds`}
        />
        <ReferenceLine y={90} stroke="#ff6b5f" strokeDasharray="4 5" opacity={0.65} />
        <Line
          type="monotone"
          dataKey="angle"
          stroke="#5d5fef"
          strokeWidth={3}
          dot={false}
          activeDot={{ r: 5, fill: "#ff6b5f", stroke: "#fff", strokeWidth: 2 }}
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

