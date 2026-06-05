interface Props {
  pct: number;
  size?: number;
  stroke?: number;
}

export default function MatchRing({ pct, size = 58, stroke = 5 }: Props) {
  const r = (size - stroke) / 2;
  const circumference = 2 * Math.PI * r;
  const offset = circumference * (1 - pct / 100);
  const tone =
    pct >= 85 ? "#56703f" :
    pct >= 70 ? "#7a8f4a" :
    "#a9774e";

  return (
    <div style={{ position: "relative", width: size, height: size, flexShrink: 0 }}>
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        {/* Track */}
        <circle
          cx={size / 2} cy={size / 2} r={r}
          fill="none" stroke="#efe8d8" strokeWidth={stroke}
        />
        {/* Fill */}
        <circle
          cx={size / 2} cy={size / 2} r={r}
          fill="none" stroke={tone} strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
        />
      </svg>
      <div
        style={{
          position: "absolute", inset: 0,
          display: "flex", flexDirection: "column",
          alignItems: "center", justifyContent: "center",
          lineHeight: 1,
        }}
      >
        <span
          className="ms-mono"
          style={{ fontSize: size * 0.27, fontWeight: 500, color: "#2a3124" }}
        >
          {pct}
        </span>
        <span
          className="ms-mono"
          style={{ fontSize: size * 0.14, color: "#8c8a78", letterSpacing: "0.1em" }}
        >
          %
        </span>
      </div>
    </div>
  );
}
