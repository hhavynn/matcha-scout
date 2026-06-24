"use client";

import Link from "next/link";
import type { Cafe } from "@/lib/types";

interface Props {
  cafe: Cafe;
}

export default function CafeCard({ cafe }: Props) {
  return (
    <Link
      href={`/cafes/${cafe.id}`}
      className="block no-underline"
      style={{ textDecoration: "none" }}
    >
      <div
        className="flex flex-col gap-3 cursor-pointer transition-all h-full"
        style={{
          background: "#fffdf8",
          borderRadius: 18,
          padding: 18,
          boxShadow:
            "inset 0 0 0 1px #e8e1d0, 0 1px 2px rgba(62,52,28,0.05), 0 2px 6px -2px rgba(62,52,28,0.06)",
        }}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLDivElement).style.transform = "translateY(-3px)";
          (e.currentTarget as HTMLDivElement).style.boxShadow =
            "inset 0 0 0 1px #ded5c1, 0 22px 48px -16px rgba(52,44,22,0.22), 0 6px 16px -8px rgba(52,44,22,0.10)";
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLDivElement).style.transform = "";
          (e.currentTarget as HTMLDivElement).style.boxShadow =
            "inset 0 0 0 1px #e8e1d0, 0 1px 2px rgba(62,52,28,0.05), 0 2px 6px -2px rgba(62,52,28,0.06)";
        }}
      >
        {/* Header row */}
        <div className="flex justify-between items-start gap-2">
          <div style={{ flex: 1, minWidth: 0 }}>
            <div className="ms-serif" style={{ fontSize: 18, color: "#2a3124", lineHeight: 1.2 }}>
              {cafe.name}
            </div>
            <div style={{ fontSize: 12.5, color: "#8c8a78", marginTop: 3 }}>
              {cafe.location}
            </div>
          </div>
          <div className="flex gap-1.5 items-center flex-shrink-0">
            {cafe.beli_rating != null && (
              <span
                style={{
                  fontSize: 10.5,
                  fontWeight: 600,
                  color: "#ffffff",
                  background: "#1e293b",
                  border: "1px solid #0f172a",
                  padding: "2px 8px",
                  borderRadius: 999,
                  flexShrink: 0,
                }}
              >
                Beli: {cafe.beli_rating.toFixed(1)}
              </span>
            )}
            {cafe.is_popup && (
              <span
                style={{
                  fontSize: 10.5,
                  fontWeight: 600,
                  color: "#d97706",
                  background: "#fef3c7",
                  border: "1px solid #fde68a",
                  padding: "2px 8px",
                  borderRadius: 999,
                  flexShrink: 0,
                }}
              >
                Pop-up
              </span>
            )}
            {cafe.business_status && cafe.business_status !== "open" && (
              <span
                style={{
                  fontSize: 10.5,
                  fontWeight: 600,
                  color: cafe.business_status === "upcoming" ? "#7c3aed" : "#9a3412",
                  background: cafe.business_status === "upcoming" ? "#f3e8ff" : "#fff7ed",
                  border: `1px solid ${cafe.business_status === "upcoming" ? "#e9d5ff" : "#fed7aa"}`,
                  padding: "2px 8px",
                  borderRadius: 999,
                  textTransform: "capitalize",
                  flexShrink: 0,
                }}
              >
                {cafe.business_status}
              </span>
            )}
            {cafe.ceremonial_matcha && (
              <span
                style={{
                  fontSize: 10.5,
                  fontWeight: 600,
                  color: "#44563a",
                  background: "#edf3e5",
                  border: "1px solid #cdd9b8",
                  padding: "2px 8px",
                  borderRadius: 999,
                  flexShrink: 0,
                }}
              >
                Ceremonial
              </span>
            )}
            {cafe.source === "yelp" && (
              <span
                style={{
                  fontSize: 10.5,
                  fontWeight: 600,
                  color: "#d32323",
                  background: "#fef0f0",
                  border: "1px solid #f8d0d0",
                  padding: "2px 8px",
                  borderRadius: 999,
                  flexShrink: 0,
                }}
              >
                Yelp
              </span>
            )}
          </div>
        </div>

        {/* Address */}
        {cafe.address && (
          <p style={{ fontSize: 12.5, color: "#585e4d", margin: 0, lineHeight: 1.5 }}>
            {cafe.address}
          </p>
        )}

        {cafe.menu_summary && (
          <p
            style={{
              fontSize: 12.5,
              color: "#585e4d",
              margin: 0,
              lineHeight: 1.5,
              display: "-webkit-box",
              WebkitLineClamp: 2,
              WebkitBoxOrient: "vertical",
              overflow: "hidden",
            }}
          >
            {cafe.menu_summary}
          </p>
        )}

        {/* Yelp metadata row */}
        {(cafe.rating != null || cafe.review_count != null || cafe.price) && (
          <div
            className="flex flex-wrap gap-x-3 gap-y-1 items-center"
            style={{ fontSize: 12.5, color: "#8c8a78" }}
          >
            {cafe.rating != null && (
              <span style={{ color: "#585e4d" }}>
                <span style={{ color: "#d4873a" }}>★</span> {cafe.rating.toFixed(1)}
              </span>
            )}
            {cafe.review_count != null && (
              <span>{cafe.review_count.toLocaleString()} Yelp reviews</span>
            )}
            {cafe.price && <span>{cafe.price}</span>}
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between gap-2 mt-auto pt-1">
          {cafe.external_url ? (
            <a
              href={cafe.external_url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              style={{
                fontSize: 12,
                color: "#5f7850",
                textDecoration: "none",
                fontWeight: 600,
              }}
            >
              View on Yelp ↗
            </a>
          ) : (
            <span />
          )}
          <span style={{ fontSize: 12, color: "#8c8a78", fontWeight: 600 }}>
            See drinks →
          </span>
        </div>
      </div>
    </Link>
  );
}
