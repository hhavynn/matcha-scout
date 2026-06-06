"use client";

import type { RegionKey } from "@/lib/types";
import { REGIONS } from "@/lib/types";

interface Props {
  value: RegionKey;
  onChange: (key: RegionKey) => void;
}

export default function RegionPicker({ value, onChange }: Props) {
  return (
    <div
      className="flex rounded-full p-1 gap-0.5"
      style={{ background: "#efe8d8", boxShadow: "inset 0 0 0 1px #ded5c1" }}
    >
      {REGIONS.map(({ key, label }) => (
        <button
          key={key}
          onClick={() => onChange(key)}
          style={{
            border: "none",
            cursor: "pointer",
            background: value === key ? "#fffdf8" : "transparent",
            color: value === key ? "#2a3124" : "#8c8a78",
            fontWeight: 600,
            fontSize: 13,
            padding: "7px 14px",
            borderRadius: 999,
            boxShadow: value === key ? "var(--shadow-xs)" : "none",
            transition: "all .15s ease",
            whiteSpace: "nowrap",
          }}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
