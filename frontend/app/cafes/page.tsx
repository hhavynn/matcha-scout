import Link from "next/link";
import ErrorState from "@/components/ErrorState";
import { getCafes } from "@/lib/api";
import type { Cafe } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function CafesPage() {
  let cafes: Cafe[] = [];
  let errorMsg: string | null = null;

  try {
    cafes = await getCafes();
  } catch (err) {
    errorMsg = err instanceof Error ? err.message : "Could not load cafes.";
  }

  if (errorMsg) {
    return (
      <div style={{ maxWidth: 1140, margin: "0 auto", padding: "30px 20px" }}>
        <ErrorState message={errorMsg} />
        <p className="text-center text-sm mt-2" style={{ color: "#8c8a78" }}>
          Refresh the page to try again.
        </p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 1140, margin: "0 auto", padding: "30px 20px 56px" }}>
      <div className="mb-7">
        <span className="ms-eyebrow">Where to find it</span>
        <h1
          className="ms-display"
          style={{ fontSize: "clamp(24px, 5vw, 34px)", margin: "6px 0 4px", color: "#2a3124" }}
        >
          Matcha cafes
        </h1>
        <p style={{ fontSize: 14.5, color: "#585e4d", margin: 0 }}>
          {cafes.length} {cafes.length === 1 ? "cafe" : "cafes"} — browse drinks and add ones you&apos;ve tried.
        </p>
      </div>

      {cafes.length === 0 ? (
        <div
          style={{
            background: "#fffdf8",
            borderRadius: 18,
            padding: "32px 24px",
            textAlign: "center",
            boxShadow: "inset 0 0 0 1px #e8e1d0",
          }}
        >
          <p style={{ color: "#8c8a78", fontSize: 14 }}>No cafes yet.</p>
        </div>
      ) : (
        <div
          className="grid gap-4"
          style={{ gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))" }}
        >
          {cafes.map((cafe) => (
            <CafeCard key={cafe.id} cafe={cafe} />
          ))}
        </div>
      )}
    </div>
  );
}

function CafeCard({ cafe }: { cafe: Cafe }) {
  return (
    <Link
      href={`/cafes/${cafe.id}`}
      className="block no-underline"
      style={{ textDecoration: "none" }}
    >
      <div
        className="flex flex-col gap-3 cursor-pointer transition-all"
        style={{
          background: "#fffdf8",
          borderRadius: 18,
          padding: 18,
          height: "100%",
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

        {/* Address */}
        {cafe.address && (
          <p style={{ fontSize: 12.5, color: "#585e4d", margin: 0, lineHeight: 1.5 }}>
            {cafe.address}
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
          <span
            style={{
              fontSize: 12,
              color: "#8c8a78",
              fontWeight: 600,
            }}
          >
            See drinks →
          </span>
        </div>
      </div>
    </Link>
  );
}
