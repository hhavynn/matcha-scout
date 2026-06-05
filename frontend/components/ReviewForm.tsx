"use client";

import { useState } from "react";
import { submitReview } from "@/lib/api";
import { IconSpark, IconCheck, IconLeaf } from "@/components/Icons";
import type { Review } from "@/lib/types";

interface Props {
  drinkId: string;
  onSubmitted: (review: Review) => void;
}

const MIN_CHARS = 12;

export default function ReviewForm({ drinkId, onSubmitted }: Props) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (text.trim().length < MIN_CHARS) {
      setError(`A few more words, please — at least ${MIN_CHARS} characters.`);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const review = await submitReview(drinkId, text.trim());
      setText("");
      onSubmitted(review);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit review.");
    } finally {
      setLoading(false);
    }
  }

  const ready = text.trim().length >= MIN_CHARS;

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      {/* Textarea with live char count */}
      <div style={{ position: "relative" }}>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={'Describe what you tasted… "Bold and grassy with a creamy oat finish, barely sweet." The AI turns your words into taste ratings.'}
          rows={4}
          className="ms-field"
          disabled={loading}
        />
        <span
          className="ms-mono"
          style={{
            position: "absolute", right: 12, bottom: 10,
            fontSize: 11,
            color: text.length < MIN_CHARS ? "#aaa794" : "#5f7850",
          }}
        >
          {text.length}
        </span>
      </div>

      {error && (
        <p style={{ color: "#a64b3e", fontSize: 12.5, margin: 0 }}>{error}</p>
      )}

      <div className="flex items-center justify-between gap-3">
        {/* Anonymous note */}
        <span className="flex items-center gap-1.5" style={{ fontSize: 12, color: "#8c8a78" }}>
          <IconLeaf size={13} color="#5f7850" /> Anonymous — no account needed
        </span>

        <button
          type="submit"
          className="ms-btn ms-btn-primary ms-btn-sm"
          disabled={loading || !ready}
          style={{ opacity: !ready ? 0.55 : 1 }}
        >
          {loading ? (
            <>
              <span
                style={{
                  width: 13, height: 13, borderRadius: 999,
                  border: "2px solid rgba(255,255,255,0.5)",
                  borderTopColor: "#fff",
                  display: "inline-block",
                  animation: "ms-spin .8s linear infinite",
                  flexShrink: 0,
                }}
              />
              Reading…
            </>
          ) : (
            <>
              <IconSpark size={13} color="#fcfdf8" /> Submit &amp; parse
            </>
          )}
        </button>
      </div>
    </form>
  );
}

/* ── Parsed result panel ─────────────────────────────────────────────── */
export function ParsedResultPanel({ review }: { review: Review }) {
  const cells: [string, number][] = [
    ["Strength", review.parsed_strength],
    ["Sweetness", review.parsed_sweetness],
    ["Creaminess", review.parsed_creaminess],
    ["Earthiness", review.parsed_earthiness],
    ["Bitterness", review.parsed_bitterness],
  ];

  return (
    <div
      className="ms-anim-up"
      style={{
        background: "linear-gradient(180deg, #e7eddc, #fffdf8)",
        borderRadius: 18,
        padding: 18,
        boxShadow: "inset 0 0 0 1px #cdd9b8",
      }}
    >
      {/* Header */}
      <div className="flex items-center gap-2.5 mb-4">
        <span
          style={{
            width: 28, height: 28, borderRadius: 999,
            background: "#56703f", color: "#fff",
            display: "flex", alignItems: "center", justifyContent: "center",
            flexShrink: 0,
          }}
        >
          <IconCheck size={15} color="#fff" />
        </span>
        <div>
          <div style={{ fontWeight: 600, fontSize: 14, color: "#36442e" }}>
            Review parsed &amp; added
          </div>
          {review.confidence != null && (
            <div className="ms-mono" style={{ fontSize: 11, color: "#44563a" }}>
              {(review.confidence * 100).toFixed(0)}% confidence
            </div>
          )}
        </div>
      </div>

      {/* 5-cell grid */}
      <div className="grid grid-cols-5 gap-2">
        {cells.map(([label, val]) => (
          <div
            key={label}
            style={{
              background: "#fffdf8",
              borderRadius: 8,
              padding: "11px 6px",
              textAlign: "center",
              boxShadow: "inset 0 0 0 1px #e8e1d0",
            }}
          >
            <div className="ms-mono" style={{ fontSize: 20, color: "#44563a" }}>{val}</div>
            <div style={{ fontSize: 10, color: "#8c8a78", marginTop: 2, letterSpacing: "0.02em" }}>
              {label}
            </div>
          </div>
        ))}
      </div>

      {/* Tags */}
      {review.tags && review.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-3">
          {review.tags.map((t) => (
            <span key={t} className="ms-pill ms-pill-sm">{t}</span>
          ))}
        </div>
      )}
    </div>
  );
}
