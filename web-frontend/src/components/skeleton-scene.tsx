"use client";

import { Grid, Line, OrbitControls, PerspectiveCamera } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { useMemo } from "react";
import type { Vector3Tuple } from "three";

const EDGES = [
  [0, 1], [0, 2], [1, 3], [2, 4],
  [5, 6], [5, 7], [7, 9], [6, 8], [8, 10],
  [5, 11], [6, 12], [11, 12],
  [11, 13], [13, 15], [12, 14], [14, 16],
] as const;

function normalizedJoints(joints: Record<string, [number, number, number]>) {
  const entries = Object.entries(joints);
  if (!entries.length) return {};
  const xs = entries.map(([, point]) => point[0]);
  const ys = entries.map(([, point]) => point[1]);
  const zs = entries.map(([, point]) => point[2]);
  const center: Vector3Tuple = [
    (Math.min(...xs) + Math.max(...xs)) / 2,
    Math.min(...ys),
    (Math.min(...zs) + Math.max(...zs)) / 2,
  ];
  const height = Math.max(Math.max(...ys) - Math.min(...ys), 0.001);
  const scale = 3.4 / height;
  return Object.fromEntries(
    entries.map(([id, point]) => [
      id,
      [
        (point[0] - center[0]) * scale,
        (point[1] - center[1]) * scale,
        (point[2] - center[2]) * scale,
      ] satisfies Vector3Tuple,
    ]),
  );
}

function Skeleton({ joints }: { joints: Record<string, [number, number, number]> }) {
  const points = useMemo(() => normalizedJoints(joints), [joints]);
  return (
    <group position={[0, -1.7, 0]}>
      {EDGES.map(([start, end]) => {
        const from = points[String(start)];
        const to = points[String(end)];
        if (!from || !to) return null;
        return (
          <Line
            key={`${start}-${end}`}
            points={[from, to]}
            color="#5d5fef"
            lineWidth={4}
            transparent
            opacity={0.92}
          />
        );
      })}
      {Object.entries(points).map(([id, position]) => (
        <mesh key={id} position={position}>
          <sphereGeometry args={[Number(id) <= 4 ? 0.055 : 0.075, 20, 20]} />
          <meshStandardMaterial color="#ff6b5f" roughness={0.28} metalness={0.08} />
        </mesh>
      ))}
    </group>
  );
}

export default function SkeletonScene({
  joints,
}: {
  joints: Record<string, [number, number, number]>;
}) {
  return (
    <Canvas dpr={[1, 1.7]} gl={{ antialias: true, alpha: true }}>
      <PerspectiveCamera makeDefault position={[4.4, 2.2, 5.2]} fov={38} />
      <ambientLight intensity={1.8} />
      <directionalLight position={[3, 6, 4]} intensity={3.2} color="#ffffff" />
      <directionalLight position={[-4, 2, -3]} intensity={2} color="#7779ff" />
      <Skeleton joints={joints} />
      <Grid
        position={[0, -1.72, 0]}
        args={[8, 8]}
        cellSize={0.35}
        cellThickness={0.6}
        cellColor="#c7c8dc"
        sectionSize={1.4}
        sectionThickness={1.1}
        sectionColor="#8e90b6"
        fadeDistance={8}
        fadeStrength={1.5}
        infiniteGrid
      />
      <OrbitControls
        makeDefault
        enablePan={false}
        minDistance={4}
        maxDistance={9}
        minPolarAngle={Math.PI / 4}
        maxPolarAngle={Math.PI / 2.05}
      />
    </Canvas>
  );
}

