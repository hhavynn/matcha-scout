"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import ConfidenceBadge from "@/components/ConfidenceBadge";
import RegionPicker from "@/components/RegionPicker";
import { IconArrow, IconSpark } from "@/components/Icons";
import type { RegionKey, ReviewTargetDrink } from "@/lib/types";

interface Props {
  targets: ReviewTargetDrink[];
}

function temperatureLabel(drink: ReviewTargetDrink): string | null {
  if (drink.is_iced === true && drink.is_hot === true) return "iced + hot";
  if (drink.is_iced === true && drink.is_hot === false) return "iced only";
  if (drink.is_hot === true && drink.is_iced === false) return "hot only";
  if (drink.is_iced === true) return "iced";
  if (drink.is_hot === true) return "hot";
  return null;
}

export default function ReviewTargetsClient({ targets }: Props) {
  const [region, setRegion] = useState<RegionKey>("all");
  const filtered = useMemo(() => {
    if (region === "all") return targets;
    return targets.filter((target) => target.region_key === region);
  }, [region, targets]);

  const unratedCount = filtered.filter((target) => target.review_count === 0).length;

  return (
    <div style={{ maxWidth: 1140, margin: "0 auto", padding: "30px 20px 56px" }}>
      <div className="flex flex-wrap items-end justify-between gap-4 mb-6">
        <div>
          <span className="ms-eyebrow">Review queue</span>
          <h1
            className="ms-display"
            style={{ fontSize: "clamp(28px, 6vw, 42px)", margin: "6px 0 6px", color: "#2a3124" }}
          >
            Help verify the taste
          </h1>
          <p style={{ fontSize: 14.5, color: "#585e4d", margin: 0, maxWidth: 640, lineHeight: 1.6 }}>
            Tried one of these? Leave a quick taste-focused review. Only review drinks you have actually tried.
          </p>
        </div>
        <RegionPicker value={region} onChange={setRegion} />
      </div>

      <div
        className="flex flex-wrap gap-3 items-center mb-6"
        style={{ color: "#8c8a78", fontSize: 13 }}
      >
        <span>
          <strong style={{ color: "#585e4d" }}>{filtered.length}</strong> review targets
        </span>
        <span style={{ width: 4, height: 4, borderRadius: 9, background: "#aaa794", display: "inline-block" }} />
        <span>
          <strong style={{ color: "#585e4d" }}>{unratedCount}</strong> unrated
        </span>
        <span style={{ width: 4, height: 4, borderRadius: 9, background: "#aaa794", display: "inline-block" }} />
        <span>Sorted by lowest review count first</span>
      </div>

      {filtered.length === 0 ? (
        <div
          style={{
            background: "#fffdf8",
            borderRadius: 18,
            padding: "34px 24px",
            textAlign: "center",
            boxShadow: "inset 0 0 0 1px #e8e1d0",
          }}
        >
          <IconSpark size={24} color="#5f7850" />
          <p className="ms-serif" style={{ fontSize: 20, color: "#2a3124", margin: "14px 0 6px" }}>
            Nothing needs reviews here right now
          </p>
          <p style={{ fontSize: 14, color: "#8c8a78", margin: 0 }}>
            Try another region or browse all drinks.
          </p>
        </div>
      ) : (
        <div
          className="grid gap-4"
          style={{ gridTemplateColumns: "repeat(auto-fill, minmax(270px, 1fr))" }}
        >
          {filtered.map((target) => {
            const tempLabel = temperatureLabel(target);
            return (
              <Link
                key={target.id}
                href={`/drinks/${target.id}#review`}
                style={{ textDecoration: "none" }}
              >
                <article
                  className="h-full flex flex-col"
                  style={{
                    background: "#fffdf8",
                    borderRadius: 18,
                    padding: 18,
                    boxShadow: "inset 0 0 0 1px #e8e1d0, var(--shadow-sm)",
                    transition: "transform .15s ease, box-shadow .15s ease",
                  }}
                >
                  <div className="flex items-start justify-between gap-3 mb-4">
                    <div>
                      <h2 className="ms-serif" style={{ fontSize: 20, margin: "0 0 4px", color: "#2a3124" }}>
                        {target.name}
                      </h2>
                      <p style={{ fontSize: 13, color: "#8c8a78", margin: 0 }}>
                        {target.cafe_name}
                      </p>
                    </div>
                    <span className="ms-mono" style={{ fontSize: 18, color: "#44563a", flexShrink: 0 }}>
                      ${target.price.toFixed(2)}
                    </span>
                  </div>

                  <p style={{ fontSize: 13.5, color: "#585e4d", lineHeight: 1.55, margin: "0 0 14px" }}>
                    {target.description}
                  </p>

                  <div className="flex flex-wrap gap-2 mb-4">
                    {target.region_label && (
                      <span className="ms-pill ms-pill-bare ms-pill-sm">{target.region_label}</span>
                    )}
                    {tempLabel && (
                      <span className="ms-pill ms-pill-bare ms-pill-sm">{tempLabel}</span>
                    )}
                    <span className="ms-pill ms-pill-bare ms-pill-sm">verified</span>
                  </div>

                  <div className="mt-auto flex flex-col gap-4">
                    <ConfidenceBadge
                      label={target.confidence_label}
                      reviewCount={target.review_count}
                    />
                    <div
                      className="inline-flex items-center justify-between gap-2"
                      style={{ color: "#44563a", fontWeight: 700, fontSize: 13 }}
                    >
                      Review if you tried it
                      <IconArrow size={15} />
                    </div>
                  </div>
                </article>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
