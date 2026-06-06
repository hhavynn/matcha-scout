"use client";

import { useState, useMemo } from "react";
import CafeCard from "@/components/CafeCard";
import RegionPicker from "@/components/RegionPicker";
import type { Cafe, RegionKey } from "@/lib/types";

interface Props {
  cafes: Cafe[];
}

export default function CafesClient({ cafes }: Props) {
  const [region, setRegion] = useState<RegionKey>("all");

  const filtered = useMemo(() => {
    if (region === "all") return cafes;
    return cafes.filter((c) => c.region_key === region);
  }, [cafes, region]);

  const sdCount = cafes.filter((c) => c.region_key === "san-diego").length;
  const ocCount = cafes.filter((c) => c.region_key === "orange-county").length;

  return (
    <div style={{ maxWidth: 1140, margin: "0 auto", padding: "30px 20px 56px" }}>
      {/* Page header */}
      <div className="flex flex-wrap items-end justify-between gap-4 mb-6">
        <div>
          <span className="ms-eyebrow">Where to find it</span>
          <h1
            className="ms-display"
            style={{ fontSize: "clamp(24px, 5vw, 34px)", margin: "6px 0 4px", color: "#2a3124" }}
          >
            Matcha cafes
          </h1>
          <p style={{ fontSize: 14.5, color: "#585e4d", margin: 0 }}>
            {filtered.length === cafes.length
              ? `${cafes.length} cafes in San Diego & Orange County`
              : `${filtered.length} cafes in ${region === "san-diego" ? "San Diego" : "Orange County"}`}
          </p>
        </div>

        <RegionPicker value={region} onChange={setRegion} />
      </div>

      {/* Region summary chips */}
      {region === "all" && (sdCount > 0 || ocCount > 0) && (
        <div className="flex flex-wrap gap-2 mb-5" style={{ fontSize: 12.5, color: "#8c8a78" }}>
          {sdCount > 0 && (
            <button
              onClick={() => setRegion("san-diego")}
              style={{
                border: "none", cursor: "pointer",
                background: "#fffdf8", color: "#585e4d",
                boxShadow: "inset 0 0 0 1px #ded5c1",
                padding: "5px 12px", borderRadius: 999, fontSize: 12.5, fontWeight: 500,
              }}
            >
              📍 {sdCount} in San Diego
            </button>
          )}
          {ocCount > 0 && (
            <button
              onClick={() => setRegion("orange-county")}
              style={{
                border: "none", cursor: "pointer",
                background: "#fffdf8", color: "#585e4d",
                boxShadow: "inset 0 0 0 1px #ded5c1",
                padding: "5px 12px", borderRadius: 999, fontSize: 12.5, fontWeight: 500,
              }}
            >
              📍 {ocCount} in Orange County
            </button>
          )}
        </div>
      )}

      {/* Empty state */}
      {filtered.length === 0 ? (
        <div
          style={{
            background: "#fffdf8",
            borderRadius: 18,
            padding: "32px 24px",
            textAlign: "center",
            boxShadow: "inset 0 0 0 1px #e8e1d0",
          }}
        >
          <p style={{ color: "#8c8a78", fontSize: 14 }}>No cafes in this region yet.</p>
        </div>
      ) : (
        <div
          className="grid gap-4"
          style={{ gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))" }}
        >
          {filtered.map((cafe: Cafe) => (
            <CafeCard key={cafe.id} cafe={cafe} />
          ))}
        </div>
      )}
    </div>
  );
}
