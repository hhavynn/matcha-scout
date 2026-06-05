"use client";

import { useState } from "react";
import { IconBack, IconArrow, IconSpark, IconFilter } from "@/components/Icons";
import type { RecommendationParams } from "@/lib/types";

const STEPS = [
  {
    key: "matcha_strength" as const,
    q: "How strong should the matcha be?",
    help: "The backbone of the drink — faint green or full ceremonial punch.",
    lo: "Mild",
    hi: "Intense",
  },
  {
    key: "sweetness" as const,
    q: "How sweet do you like it?",
    help: "From bone-dry and grown-up to full dessert territory.",
    lo: "Not sweet",
    hi: "Dessert",
  },
  {
    key: "creaminess" as const,
    q: "How creamy should it feel?",
    help: "Light and clean on the palate, or rich and velvety.",
    lo: "Light",
    hi: "Velvety",
  },
  {
    key: "earthiness" as const,
    q: "How grassy and earthy?",
    help: "That fresh-cut, vegetal 'green' character matcha is known for.",
    lo: "Clean",
    hi: "Garden",
  },
  {
    key: "bitterness" as const,
    q: "How much bitter edge?",
    help: "A little astringency can add depth — or you can skip it entirely.",
    lo: "Mellow",
    hi: "Bold",
  },
] as const;

const TOTAL_STEPS = STEPS.length + 1; // 5 taste + 1 filter
const MILKS = ["any", "oat", "whole", "almond", "coconut", "none"];
const PRICE_CHIPS = [
  { label: "Any", value: "" },
  { label: "≤ $6", value: "6" },
  { label: "≤ $7", value: "7" },
  { label: "≤ $8", value: "8" },
];

interface Props {
  onSubmit: (params: RecommendationParams) => void;
  loading: boolean;
}

export default function PreferenceQuiz({ onSubmit, loading }: Props) {
  const [step, setStep] = useState(0);
  const [prefs, setPrefs] = useState<Record<string, number>>({
    matcha_strength: 3, sweetness: 3, creaminess: 3, earthiness: 3, bitterness: 3,
  });
  const [priceChip, setPriceChip] = useState("");
  const [milk, setMilk] = useState("any");

  const isTasteStep = step < STEPS.length;
  const isFilterStep = step === STEPS.length;
  const cur = isTasteStep ? STEPS[step] : null;

  function choose(key: string, val: number) {
    setPrefs((p) => ({ ...p, [key]: val }));
    // Auto-advance after short delay
    setTimeout(() => setStep((s) => Math.min(s + 1, STEPS.length)), 220);
  }

  function handleSubmit() {
    const params: RecommendationParams = {
      matcha_strength: prefs.matcha_strength,
      sweetness: prefs.sweetness,
      creaminess: prefs.creaminess,
      earthiness: prefs.earthiness,
      bitterness: prefs.bitterness,
      limit: 8,
    };
    if (priceChip && parseFloat(priceChip) > 0) params.price_max = parseFloat(priceChip);
    if (milk !== "any") params.milk_type = milk;
    onSubmit(params);
  }

  return (
    <div style={{ maxWidth: 560, margin: "0 auto" }}>
      {/* Header + progress */}
      <div className="flex items-center justify-between mb-3">
        <span className="ms-eyebrow">Your tasting profile</span>
        <span className="ms-mono" style={{ fontSize: 12, color: "#8c8a78" }}>
          {String(Math.min(step + 1, TOTAL_STEPS)).padStart(2, "0")} /{" "}
          {String(TOTAL_STEPS).padStart(2, "0")}
        </span>
      </div>

      {/* Segmented progress bar */}
      <div className="flex gap-1.5 mb-5">
        {Array.from({ length: TOTAL_STEPS }).map((_, i) => (
          <div key={i} className="ms-qp-seg">
            <div
              className="ms-qp-fill"
              style={{ width: i < step ? "100%" : i === step ? "50%" : "0%" }}
            />
          </div>
        ))}
      </div>

      {/* Question card */}
      <div
        key={step}
        className="ms-anim-up"
        style={{
          background: "#fffdf8",
          borderRadius: 24,
          padding: "26px 22px",
          boxShadow: "inset 0 0 0 1px #e8e1d0, 0 6px 20px -8px rgba(58,48,24,0.14)",
        }}
      >
        {isTasteStep && cur && (
          <>
            <div className="flex items-center gap-2.5 mb-2">
              <span
                style={{
                  width: 30, height: 30, borderRadius: 999,
                  background: "#e7eddc", color: "#44563a",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 13,
                }}
              >
                💧
              </span>
              <span className="ms-mono" style={{ fontSize: 11, color: "#8c8a78", textTransform: "uppercase", letterSpacing: "0.12em" }}>
                {cur.key.replace("_", " ")}
              </span>
            </div>
            <h2 className="ms-display" style={{ fontSize: 25, lineHeight: 1.1, margin: 0 }}>
              {cur.q}
            </h2>
            <p style={{ fontSize: 14, color: "#585e4d", marginTop: 8, lineHeight: 1.55 }}>
              {cur.help}
            </p>
            <div className="flex justify-between gap-2 mt-5">
              {[1, 2, 3, 4, 5].map((n) => (
                <button
                  key={n}
                  className={"ms-scale-btn" + (prefs[cur.key] === n ? " selected" : "")}
                  onClick={() => choose(cur.key, n)}
                >
                  {n}
                </button>
              ))}
            </div>
            <div className="flex justify-between mt-2.5" style={{ fontSize: 12, color: "#8c8a78" }}>
              <span>{cur.lo}</span>
              <span>{cur.hi}</span>
            </div>
          </>
        )}

        {isFilterStep && (
          <>
            <div className="flex items-center gap-2.5 mb-2">
              <span
                style={{
                  width: 30, height: 30, borderRadius: 999,
                  background: "#f3e8d6", color: "#93623c",
                  display: "flex", alignItems: "center", justifyContent: "center",
                }}
              >
                <IconFilter size={15} color="#93623c" />
              </span>
              <span className="ms-mono" style={{ fontSize: 11, color: "#8c8a78", textTransform: "uppercase", letterSpacing: "0.12em" }}>
                Optional
              </span>
            </div>
            <h2 className="ms-display" style={{ fontSize: 25, lineHeight: 1.1, margin: 0 }}>
              A couple of practicals
            </h2>
            <p style={{ fontSize: 14, color: "#585e4d", marginTop: 8, lineHeight: 1.55 }}>
              Skip these if you&apos;d rather see everything.
            </p>

            {/* Price chips */}
            <div className="mt-5">
              <div style={{ fontSize: 12.5, color: "#585e4d", fontWeight: 500, marginBottom: 10 }}>
                Max price
              </div>
              <div className="flex gap-2 flex-wrap">
                {PRICE_CHIPS.map(({ label, value }) => (
                  <button
                    key={label}
                    onClick={() => setPriceChip(value)}
                    className="ms-btn-quiet"
                    style={{
                      padding: "10px 16px",
                      borderRadius: 999,
                      fontFamily: "'IBM Plex Mono', monospace",
                      fontSize: 14,
                      fontWeight: 500,
                      background: priceChip === value ? "#56703f" : "#faf5ea",
                      color: priceChip === value ? "#fff" : "#585e4d",
                      boxShadow: priceChip === value
                        ? "0 1px 2px rgba(62,52,28,0.05), 0 2px 6px -2px rgba(62,52,28,0.06)"
                        : "inset 0 0 0 1px #ded5c1",
                      border: "none", cursor: "pointer",
                      transition: "all .14s ease",
                    }}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {/* Milk chips */}
            <div className="mt-5">
              <div style={{ fontSize: 12.5, color: "#585e4d", fontWeight: 500, marginBottom: 10 }}>
                Milk preference
              </div>
              <div className="flex gap-2 flex-wrap">
                {MILKS.map((m) => (
                  <button
                    key={m}
                    onClick={() => setMilk(m)}
                    style={{
                      padding: "10px 16px",
                      borderRadius: 999,
                      fontSize: 13.5,
                      fontWeight: 600,
                      textTransform: "capitalize",
                      background: milk === m ? "#56703f" : "#faf5ea",
                      color: milk === m ? "#fff" : "#585e4d",
                      boxShadow: milk === m
                        ? "0 1px 2px rgba(62,52,28,0.05)"
                        : "inset 0 0 0 1px #ded5c1",
                      border: "none", cursor: "pointer",
                      transition: "all .14s ease",
                    }}
                  >
                    {m === "any" ? "Any milk" : m === "none" ? "No milk" : m}
                  </button>
                ))}
              </div>
            </div>

            <button
              className="ms-btn ms-btn-primary ms-btn-lg ms-btn-block mt-6"
              onClick={handleSubmit}
              disabled={loading}
            >
              {loading ? (
                <>
                  <span
                    style={{
                      width: 14, height: 14, borderRadius: 999,
                      border: "2px solid rgba(255,255,255,0.5)",
                      borderTopColor: "#fff",
                      display: "inline-block",
                      animation: "ms-spin .8s linear infinite",
                    }}
                  />
                  Finding matches…
                </>
              ) : (
                <>
                  <IconSpark size={16} color="#fcfdf8" /> See my matches
                </>
              )}
            </button>
          </>
        )}
      </div>

      {/* Footer nav */}
      <div className="flex items-center justify-between mt-4">
        <button
          className="ms-btn-quiet"
          disabled={step === 0}
          onClick={() => setStep((s) => Math.max(0, s - 1))}
        >
          <IconBack size={15} /> Back
        </button>
        {isTasteStep && (
          <button
            className="ms-btn-quiet"
            onClick={() => setStep((s) => Math.min(s + 1, STEPS.length))}
          >
            {prefs[STEPS[step].key] ? "Next" : "Skip"} <IconArrow size={15} />
          </button>
        )}
      </div>
    </div>
  );
}
