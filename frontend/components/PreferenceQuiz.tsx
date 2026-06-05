"use client";

import { useState } from "react";
import type { RecommendationParams } from "@/lib/types";

const SLIDERS = [
  { key: "matcha_strength" as const, label: "Matcha Strength", low: "Mild", high: "Intense" },
  { key: "sweetness"       as const, label: "Sweetness",       low: "Not sweet", high: "Very sweet" },
  { key: "creaminess"      as const, label: "Creaminess",      low: "Thin/watery", high: "Very creamy" },
  { key: "earthiness"      as const, label: "Earthiness",      low: "Clean", high: "Grassy/earthy" },
  { key: "bitterness"      as const, label: "Bitterness",      low: "Mellow", high: "Bitter" },
];

const MILK_OPTIONS = ["any", "oat", "whole", "almond", "coconut", "none"];

interface Props {
  onSubmit: (params: RecommendationParams) => void;
  loading: boolean;
}

export default function PreferenceQuiz({ onSubmit, loading }: Props) {
  const [prefs, setPrefs] = useState<RecommendationParams>({
    matcha_strength: 3,
    sweetness: 3,
    creaminess: 3,
    earthiness: 3,
    bitterness: 3,
    limit: 8,
  });
  const [priceMax, setPriceMax] = useState("");
  const [milkType, setMilkType] = useState("any");

  function handleSlider(key: keyof RecommendationParams, value: number) {
    setPrefs((p) => ({ ...p, [key]: value }));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const params: RecommendationParams = { ...prefs };
    if (priceMax && parseFloat(priceMax) > 0) {
      params.price_max = parseFloat(priceMax);
    }
    if (milkType !== "any") {
      params.milk_type = milkType;
    }
    onSubmit(params);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {SLIDERS.map(({ key, label, low, high }) => (
        <div key={key}>
          <div className="flex justify-between items-center mb-1">
            <label className="text-sm font-medium text-green-900">{label}</label>
            <span className="text-sm font-semibold text-green-700 bg-green-50 rounded-full px-2 py-0.5">
              {prefs[key]}
            </span>
          </div>
          <input
            type="range"
            min={1}
            max={5}
            step={1}
            value={prefs[key] as number}
            onChange={(e) => handleSlider(key, parseInt(e.target.value))}
            className="w-full accent-green-600"
          />
          <div className="flex justify-between text-xs text-gray-400 mt-0.5">
            <span>{low}</span>
            <span>{high}</span>
          </div>
        </div>
      ))}

      <div className="grid grid-cols-2 gap-4 pt-2 border-t border-green-100">
        <div>
          <label className="block text-sm font-medium text-green-900 mb-1">
            Max price (optional)
          </label>
          <input
            type="number"
            min="0"
            step="0.50"
            placeholder="e.g. 8.00"
            value={priceMax}
            onChange={(e) => setPriceMax(e.target.value)}
            className="w-full border border-green-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-green-900 mb-1">
            Milk preference
          </label>
          <select
            value={milkType}
            onChange={(e) => setMilkType(e.target.value)}
            className="w-full border border-green-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400 bg-white"
          >
            {MILK_OPTIONS.map((m) => (
              <option key={m} value={m}>
                {m === "any" ? "Any milk" : m.charAt(0).toUpperCase() + m.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-green-600 text-white py-3 rounded-xl font-semibold hover:bg-green-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? "Finding matches…" : "Find My Matcha"}
      </button>
    </form>
  );
}
