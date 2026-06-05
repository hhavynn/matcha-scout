"use client";

import { useState } from "react";
import Link from "next/link";
import PreferenceQuiz from "@/components/PreferenceQuiz";
import TasteBars from "@/components/TasteBars";
import MatchRing from "@/components/MatchRing";
import ErrorState from "@/components/ErrorState";
import EmptyState from "@/components/EmptyState";
import LoadingState from "@/components/LoadingState";
import { IconCheck, IconArrow } from "@/components/Icons";
import { getRecommendations } from "@/lib/api";
import type { RecommendationParams, RecommendationResult } from "@/lib/types";

export default function QuizPage() {
  const [results, setResults] = useState<RecommendationResult[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastParams, setLastParams] = useState<RecommendationParams | null>(null);

  async function handleSubmit(params: RecommendationParams) {
    setLoading(true);
    setError(null);
    setLastParams(params);
    try {
      const data = await getRecommendations(params);
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load recommendations.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 1140, margin: "0 auto", padding: "30px 20px 56px" }}>
      {/* Header */}
      <div className="mb-8">
        <span className="ms-eyebrow">Your tasting profile</span>
        <h1 className="ms-display" style={{ fontSize: "clamp(26px, 5vw, 36px)", margin: "8px 0 4px", color: "#2a3124" }}>
          Find your matcha match
        </h1>
        <p style={{ fontSize: 14.5, color: "#585e4d" }}>
          Answer five quick taste questions and we&apos;ll rank every drink against your preferences.
        </p>
      </div>

      <div
        className="grid gap-8 items-start"
        style={{ gridTemplateColumns: results ? "minmax(0,1fr) minmax(0,1.6fr)" : "1fr" }}
      >
        {/* Quiz panel */}
        <div>
          <PreferenceQuiz onSubmit={handleSubmit} loading={loading} />
        </div>

        {/* Results panel — only shown after submission */}
        {(results !== null || loading || error) && (
          <div>
            {loading && (
              <div
                className="ms-card-quiet"
                style={{ padding: 8 }}
              >
                <LoadingState />
              </div>
            )}

            {error && !loading && (
              <ErrorState
                message={error}
                onRetry={() => lastParams && handleSubmit(lastParams)}
              />
            )}

            {results && !loading && !error && (
              <>
                {/* Results header */}
                <div className="mb-4">
                  <span className="ms-eyebrow">Your matches</span>
                  <h2 className="ms-serif" style={{ fontSize: 24, margin: "6px 0 4px", color: "#2a3124" }}>
                    Poured just for your taste
                  </h2>
                  <p style={{ fontSize: 13.5, color: "#585e4d", margin: 0 }}>
                    Ranked by how closely each drink fits your profile — with the reasons in plain sight.
                  </p>
                </div>

                {results.length === 0 ? (
                  <div className="ms-card-quiet" style={{ padding: 8 }}>
                    <EmptyState
                      icon="drop"
                      title="No drinks fit those filters"
                      body="Your price or milk filter ruled everything out. Loosen them and we'll find your closest pours."
                      action={
                        <button
                          className="ms-btn ms-btn-primary ms-btn-sm"
                          onClick={() => lastParams && handleSubmit({ ...lastParams, price_max: undefined, milk_type: undefined })}
                        >
                          Clear filters
                        </button>
                      }
                    />
                  </div>
                ) : (
                  <div className="flex flex-col gap-3.5">
                    {results.map((r, i) => (
                      <RecCard
                        key={r.drink_id}
                        result={r}
                        rank={i + 1}
                        prefs={lastParams}
                      />
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/* ── Recommendation card ──────────────────────────────────────────────── */
function RecCard({
  result,
  rank,
  prefs,
}: {
  result: RecommendationResult;
  rank: number;
  prefs: RecommendationParams | null;
}) {
  const isTop = rank === 1;

  // Convert prefs to the TasteProfile shape for compareTo
  const compareTo = prefs
    ? {
        matcha_strength: prefs.matcha_strength,
        sweetness: prefs.sweetness,
        creaminess: prefs.creaminess,
        earthiness: prefs.earthiness,
        bitterness: prefs.bitterness,
      }
    : undefined;

  return (
    <div
      className="ms-anim-up"
      style={{
        background: "#fffdf8",
        borderRadius: 24,
        padding: "16px",
        boxShadow: isTop
          ? "inset 0 0 0 1.5px #cdd9b8, 0 6px 20px -8px rgba(58,48,24,0.14)"
          : "inset 0 0 0 1px #e8e1d0, 0 2px 6px -2px rgba(62,52,28,0.06)",
        animationDelay: `${rank * 0.05}s`,
        position: "relative",
      }}
    >
      {/* Rank ribbon */}
      <div
        className="ms-mono"
        style={{
          position: "absolute", top: 0, left: 16,
          background: "#56703f", color: "#fff",
          fontSize: 11, fontWeight: 500,
          padding: "4px 10px 5px",
          borderRadius: "0 0 9px 9px",
          letterSpacing: "0.04em",
        }}
      >
        #{rank}
      </div>

      {/* Header row */}
      <div className="flex gap-3 items-start mt-3 mb-3">
        {/* Image placeholder */}
        <div
          style={{
            width: 72, height: 72, borderRadius: 14, flexShrink: 0,
            background: "linear-gradient(160deg, #c9d6ad, #91a978)",
            position: "relative", overflow: "hidden",
          }}
        >
          <div style={{ position: "absolute", inset: 0, background: "repeating-linear-gradient(135deg, rgba(255,255,255,0.16) 0 8px, transparent 8px 16px)" }} />
        </div>

        <div style={{ flex: 1, minWidth: 0 }}>
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            {isTop && (
              <span className="ms-pill ms-pill-sm">
                ★ Top match
              </span>
            )}
          </div>
          <div className="ms-serif" style={{ fontSize: 18, color: "#2a3124", lineHeight: 1.1 }}>
            {result.drink_name}
          </div>
          {result.cafe_name && (
            <div style={{ fontSize: 12.5, color: "#8c8a78", marginTop: 3 }}>{result.cafe_name}</div>
          )}
          <div className="ms-mono" style={{ fontSize: 13, color: "#44563a", marginTop: 5, fontWeight: 500 }}>
            ${result.price.toFixed(2)}
          </div>
        </div>

        <MatchRing pct={result.match_pct} size={58} />
      </div>

      {/* Reasons */}
      {result.reasons.length > 0 && (
        <div className="flex flex-col gap-1.5 mb-3">
          {result.reasons.map((reason, i) => (
            <div key={i} className="flex gap-2 items-start" style={{ fontSize: 13, color: "#585e4d", lineHeight: 1.4 }}>
              <span
                style={{
                  flexShrink: 0, width: 18, height: 18, borderRadius: 999,
                  background: "#e7eddc", color: "#44563a",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  marginTop: 1,
                }}
              >
                <IconCheck size={11} color="#44563a" />
              </span>
              {reason}
            </div>
          ))}
        </div>
      )}

      {/* Taste bars with compareTo marker */}
      <div style={{ borderTop: "1px solid #e8e1d0", paddingTop: 14, marginBottom: 14 }}>
        <TasteBars
          profile={result.taste_profile}
          compareTo={compareTo}
          animate
        />
        {compareTo && (
          <p style={{ fontSize: 11, color: "#8c8a78", marginTop: 8, display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ display: "inline-block", width: 8, height: 8, background: "#a9774e", borderRadius: 2 }} />
            marker shows your preference
          </p>
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between gap-3">
        <div className="flex flex-wrap gap-1.5">
          {result.milk_options.slice(0, 3).map((m) => (
            <span key={m} className="ms-pill ms-pill-bare ms-pill-sm">{m}</span>
          ))}
        </div>
        <Link
          href={`/drinks/${result.drink_id}`}
          className="ms-btn ms-btn-ghost ms-btn-sm flex items-center gap-1.5"
          style={{ textDecoration: "none", flexShrink: 0 }}
        >
          Details <IconArrow size={13} />
        </Link>
      </div>
    </div>
  );
}
