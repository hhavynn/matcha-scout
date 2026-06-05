import Link from "next/link";
import { IconSpark } from "@/components/Icons";

const FEATURES = [
  {
    n: "01",
    icon: "✦",
    title: "AI reads the reviews",
    body: "Members describe a drink in plain words. Our parser turns 'grassy, barely sweet, super creamy' into structured taste ratings.",
  },
  {
    n: "02",
    icon: "◎",
    title: "Matched to your palate",
    body: "A transparent similarity score ranks every drink against your tasting profile — no black-box guessing, just math you can see.",
  },
  {
    n: "03",
    icon: "◑",
    title: "Grown by the community",
    body: "Each anonymous review sharpens a drink's profile. The more people pour in, the better every match gets.",
  },
];

const STEPS = [
  {
    title: "Rate your preferences",
    desc: "Answer five quick taste questions — strength, sweetness, creaminess, earthiness, bitterness.",
  },
  {
    title: "See your ranked matches",
    desc: "Every drink is scored against your profile. Match percentage and plain-language reasons are shown for each.",
  },
  {
    title: "Explore and review",
    desc: "Read community taste profiles, then write a review. The AI parses your words and sharpens the data.",
  },
];

export default function HomePage() {
  return (
    <div style={{ maxWidth: 1140, margin: "0 auto", padding: "0 20px" }}>
      {/* ── Hero ──────────────────────────────────────────────────────── */}
      <section style={{ padding: "40px 0 28px" }}>
        <div
          className="grid gap-8"
          style={{
            gridTemplateColumns: "1fr",
          }}
        >
          {/* Left column */}
          <div className="ms-anim-up">
            <span className="ms-eyebrow">A boutique matcha guide</span>
            <h1
              className="ms-display"
              style={{
                fontSize: "clamp(38px, 8vw, 58px)",
                margin: "14px 0 16px",
                color: "#2a3124",
              }}
            >
              Find the matcha<br />
              that tastes like{" "}
              <span className="ms-serif-i" style={{ color: "#44563a" }}>
                you
              </span>
              .
            </h1>
            <p style={{ fontSize: 16, color: "#585e4d", lineHeight: 1.6, maxWidth: "32em", margin: 0 }}>
              Tell us how you like it — strong, sweet, creamy, earthy — and
              we&apos;ll rank real cafe drinks against your taste, using community
              reviews our AI reads for you.
            </p>
            <div className="flex flex-wrap gap-3 mt-6">
              <Link href="/quiz" className="ms-btn ms-btn-primary ms-btn-lg" style={{ textDecoration: "none" }}>
                <IconSpark size={16} color="#fcfdf8" /> Find my matcha
              </Link>
              <Link href="/drinks" className="ms-btn ms-btn-ghost ms-btn-lg" style={{ textDecoration: "none" }}>
                Browse drinks
              </Link>
            </div>
            {/* Proof stats */}
            <div
              className="flex items-center gap-4 mt-7 flex-wrap"
              style={{ fontSize: 12.5, color: "#8c8a78" }}
            >
              <span>
                <strong style={{ color: "#585e4d" }}>10</strong> drinks
              </span>
              <span style={{ width: 4, height: 4, borderRadius: 9, background: "#aaa794", display: "inline-block" }} />
              <span>
                <strong style={{ color: "#585e4d" }}>5</strong> cafes
              </span>
              <span style={{ width: 4, height: 4, borderRadius: 9, background: "#aaa794", display: "inline-block" }} />
              <span>5-dimension taste profiles</span>
            </div>
          </div>

          {/* Right column — preview card (hidden on mobile) */}
          <div
            className="ms-anim-up hidden md:block"
            style={{ animationDelay: "0.08s" }}
          >
            <PreviewCard />
          </div>
        </div>
      </section>

      {/* ── Features ──────────────────────────────────────────────────── */}
      <section style={{ paddingBottom: 28, borderTop: "1px solid #e8e1d0", paddingTop: 36 }}>
        <div className="grid gap-4" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
          {FEATURES.map((f) => (
            <div
              key={f.n}
              style={{
                background: "#fffdf8",
                borderRadius: 18,
                padding: "22px 20px",
                boxShadow: "inset 0 0 0 1px #e8e1d0, 0 1px 2px rgba(62,52,28,0.05), 0 2px 6px -2px rgba(62,52,28,0.06)",
              }}
            >
              <span
                className="ms-mono"
                style={{ fontSize: 12, color: "#5f7850", display: "block", marginBottom: 14 }}
              >
                {f.n}
              </span>
              <div
                style={{
                  width: 42, height: 42, borderRadius: 13,
                  background: "#e7eddc", color: "#44563a",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  marginBottom: 14, fontSize: 20,
                  boxShadow: "inset 0 0 0 1px rgba(95,120,80,0.16)",
                }}
              >
                {f.icon}
              </div>
              <h3 className="ms-serif" style={{ fontSize: 20, margin: "0 0 6px", color: "#2a3124" }}>
                {f.title}
              </h3>
              <p style={{ color: "#585e4d", fontSize: 13.5, lineHeight: 1.6, margin: 0 }}>
                {f.body}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* ── How it works ──────────────────────────────────────────────── */}
      <section style={{ paddingBottom: 48, borderTop: "1px solid #e8e1d0", paddingTop: 36 }}>
        <div
          style={{
            background: "#fffdf8",
            borderRadius: 18,
            padding: "28px 24px",
            boxShadow: "inset 0 0 0 1px #e8e1d0, 0 1px 2px rgba(62,52,28,0.05)",
          }}
        >
          <span className="ms-eyebrow" style={{ display: "block", marginBottom: 8 }}>
            Three steps
          </span>
          <h2
            className="ms-serif"
            style={{ fontSize: 26, color: "#2a3124", margin: "0 0 22px" }}
          >
            From preferences to perfect pour
          </h2>
          <div
            className="grid gap-5"
            style={{ gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))" }}
          >
            {STEPS.map((s, i) => (
              <div key={i} className="flex gap-4 items-start">
                <span
                  className="ms-mono"
                  style={{
                    flexShrink: 0,
                    width: 34, height: 34, borderRadius: 999,
                    background: "#56703f", color: "#fff",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: 14,
                    boxShadow: "0 4px 10px -4px rgba(68,86,58,0.6)",
                  }}
                >
                  {i + 1}
                </span>
                <div>
                  <p style={{ fontWeight: 600, color: "#2a3124", margin: "0 0 3px", fontSize: 15 }}>
                    {s.title}
                  </p>
                  <p style={{ fontSize: 13.5, color: "#585e4d", margin: 0, lineHeight: 1.55 }}>
                    {s.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-7">
            <Link href="/quiz" className="ms-btn ms-btn-primary" style={{ textDecoration: "none" }}>
              <IconSpark size={15} color="#fcfdf8" /> Start the tasting
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

/* ── Preview card (top-match teaser, right column) ──────────────────── */
function PreviewCard() {
  return (
    <div
      style={{
        background: "#fffdf8",
        borderRadius: 24,
        overflow: "hidden",
        boxShadow: "inset 0 0 0 1.5px #cdd9b8, 0 22px 48px -16px rgba(52,44,22,0.18), 0 6px 16px -8px rgba(52,44,22,0.10)",
      }}
    >
      {/* Gradient image slot */}
      <div
        style={{
          height: 180,
          background: "linear-gradient(160deg, #6e8c5a, #4d6e3a)",
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Foam bubble */}
        <div
          style={{
            position: "absolute", top: -35, right: -20,
            width: 126, height: 126, borderRadius: 999,
            background: "radial-gradient(circle at 38% 34%, rgba(255,255,255,0.55), rgba(255,255,255,0.06) 70%)",
          }}
        />
        <div style={{ position: "absolute", inset: 0, background: "repeating-linear-gradient(135deg, rgba(255,255,255,0.16) 0 10px, transparent 10px 20px)" }} />
        {/* Labels */}
        <div
          style={{
            position: "absolute", top: 10, left: 12,
            background: "#56703f", color: "#fff",
            fontFamily: "'IBM Plex Mono', monospace",
            fontSize: 10.5, fontWeight: 500,
            padding: "4px 10px 5px", borderRadius: "0 0 9px 9px",
            letterSpacing: "0.04em",
          }}
        >
          #1
        </div>
        <span
          style={{
            position: "absolute", bottom: 8, left: 10,
            fontFamily: "'IBM Plex Mono', monospace",
            fontSize: 9.5, letterSpacing: "0.08em", textTransform: "uppercase",
            color: "rgba(40,46,30,0.55)", background: "rgba(255,253,248,0.72)",
            padding: "3px 7px", borderRadius: 999,
          }}
        >
          drink photo
        </span>
      </div>

      {/* Body */}
      <div style={{ padding: "16px 18px 18px" }}>
        <div className="flex items-center gap-2 mb-1">
          <span className="ms-pill ms-pill-sm">
            <span className="ms-mono">★</span> Top match
          </span>
        </div>
        <div className="flex justify-between items-start gap-2 mt-2">
          <div>
            <div className="ms-serif" style={{ fontSize: 20, color: "#2a3124", lineHeight: 1.1 }}>
              Stone Garden Ceremonial
            </div>
            <div style={{ fontSize: 12.5, color: "#8c8a78", marginTop: 4 }}>
              Verdant Cup · Portland, OR
            </div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div className="ms-mono" style={{ fontSize: 22, fontWeight: 500, color: "#44563a" }}>94</div>
            <div className="ms-mono" style={{ fontSize: 10, color: "#8c8a78" }}>%</div>
          </div>
        </div>

        {/* Mini taste bars */}
        <div className="flex flex-col mt-4" style={{ gap: 7 }}>
          {[
            { label: "Strength", val: 5 },
            { label: "Earthiness", val: 5 },
            { label: "Bitterness", val: 4.5 },
          ].map(({ label, val }) => (
            <div key={label} style={{ display: "grid", gridTemplateColumns: "76px 1fr 18px", alignItems: "center", gap: 10 }}>
              <span style={{ fontSize: 12, color: "#585e4d", fontWeight: 500 }}>{label}</span>
              <div style={{ height: 7, borderRadius: 999, background: "#efe8d8", boxShadow: "inset 0 0 0 1px #ded5c1", position: "relative", overflow: "hidden" }}>
                <div style={{ position: "absolute", left: 0, inset: 0, width: `${((val - 1) / 4) * 100}%`, background: "linear-gradient(90deg, #5f7850, #6f8a57)", borderRadius: 999 }} />
              </div>
              <span className="ms-mono" style={{ fontSize: 11, color: "#8c8a78", textAlign: "right" }}>{val}</span>
            </div>
          ))}
        </div>

        <Link
          href="/quiz"
          className="ms-btn ms-btn-primary ms-btn-block mt-5"
          style={{ textDecoration: "none", fontSize: 14 }}
        >
          See your matches
        </Link>
      </div>
    </div>
  );
}
