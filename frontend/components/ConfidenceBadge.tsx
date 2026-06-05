interface Props {
  label?: string;
  reviewCount: number;
  showHint?: boolean;
}

const LABEL_STYLES: Record<string, { color: string; bg: string; border: string }> = {
  high:     { color: "#2d5a27", bg: "#e7f0e2", border: "#b8d8b0" },
  medium:   { color: "#4a5e1e", bg: "#eef1d8", border: "#cdd9a8" },
  low:      { color: "#7a5a1e", bg: "#f4eed8", border: "#ddd0a8" },
  unrated:  { color: "#8c8a78", bg: "#f5f2ea", border: "#e0dbc8" },
};

export default function ConfidenceBadge({ label, reviewCount, showHint }: Props) {
  const resolved = label ?? "unrated";
  const style = LABEL_STYLES[resolved] ?? LABEL_STYLES.unrated;
  const displayLabel = resolved.charAt(0).toUpperCase() + resolved.slice(1);

  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center gap-2 flex-wrap">
        <span
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 5,
            fontSize: 12,
            fontWeight: 600,
            padding: "3px 9px",
            borderRadius: 999,
            background: style.bg,
            color: style.color,
            boxShadow: `inset 0 0 0 1px ${style.border}`,
          }}
        >
          <span
            style={{
              width: 6,
              height: 6,
              borderRadius: 999,
              background: style.color,
              display: "inline-block",
            }}
          />
          {displayLabel} confidence
        </span>
        <span style={{ fontSize: 12, color: "#8c8a78" }}>
          {reviewCount === 0
            ? "No reviews yet"
            : `${reviewCount} ${reviewCount === 1 ? "review" : "reviews"}`}
        </span>
      </div>
      {showHint && (
        <p style={{ fontSize: 11.5, color: "#aaa794", margin: 0, lineHeight: 1.4 }}>
          Confidence reflects Matcha Scout reviews, not Yelp ratings.
        </p>
      )}
    </div>
  );
}
