"use client";

import { useState } from "react";
import Link from "next/link";
import PreferenceQuiz from "@/components/PreferenceQuiz";
import TasteBars from "@/components/TasteBars";
import ErrorState from "@/components/ErrorState";
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
    <div className="max-w-5xl mx-auto px-4 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-green-900">Find Your Matcha Match</h1>
        <p className="text-green-700 mt-1">
          Rate your taste preferences and we will rank every drink against them.
        </p>
      </div>

      <div className="grid md:grid-cols-[1fr_1.5fr] gap-8 items-start">
        {/* Quiz form */}
        <div className="bg-white rounded-2xl border border-green-100 shadow-sm p-6 sticky top-6">
          <h2 className="font-semibold text-green-900 mb-5">Your Preferences</h2>
          <PreferenceQuiz onSubmit={handleSubmit} loading={loading} />
        </div>

        {/* Results */}
        <div>
          {loading && (
            <div className="flex flex-col items-center justify-center py-20 gap-3 text-green-700">
              <div className="w-8 h-8 border-2 border-green-300 border-t-green-600 rounded-full animate-spin" />
              <p className="text-sm">Finding your matches…</p>
            </div>
          )}

          {error && (
            <ErrorState
              message={error}
              onRetry={() => lastParams && handleSubmit(lastParams)}
            />
          )}

          {results && !loading && (
            <div>
              <h2 className="font-semibold text-green-900 mb-4">
                {results.length === 0
                  ? "No drinks matched your filters"
                  : `${results.length} match${results.length === 1 ? "" : "es"} found`}
              </h2>

              {results.length === 0 ? (
                <p className="text-sm text-gray-500">
                  Try relaxing your price or milk type filters.
                </p>
              ) : (
                <div className="space-y-4">
                  {results.map((r) => (
                    <RecommendationCard key={r.drink_id} result={r} />
                  ))}
                </div>
              )}
            </div>
          )}

          {!results && !loading && !error && (
            <div className="flex flex-col items-center justify-center py-20 text-center gap-3">
              <div className="text-5xl">🍵</div>
              <p className="text-green-700 font-medium">Set your preferences and hit the button</p>
              <p className="text-sm text-gray-500">Results will appear here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function RecommendationCard({ result }: { result: RecommendationResult }) {
  return (
    <div className="bg-white rounded-2xl border border-green-100 shadow-sm p-5">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-block bg-green-600 text-white text-xs font-bold px-2 py-0.5 rounded-full">
              {result.match_pct}% match
            </span>
            <h3 className="font-semibold text-green-900">{result.drink_name}</h3>
          </div>
          {result.cafe_name && (
            <p className="text-xs text-green-600 mt-0.5">{result.cafe_name}</p>
          )}
        </div>
        <span className="text-green-700 font-semibold shrink-0">${result.price.toFixed(2)}</span>
      </div>

      {/* Match score bar */}
      <div className="mb-3">
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-green-500 rounded-full"
            style={{ width: `${result.match_pct}%` }}
          />
        </div>
      </div>

      {/* Reasons */}
      {result.reasons.length > 0 && (
        <ul className="mb-3 space-y-0.5">
          {result.reasons.map((r, i) => (
            <li key={i} className="text-xs text-gray-600 flex items-start gap-1.5">
              <span className="text-green-500 mt-0.5">✓</span>
              {r}
            </li>
          ))}
        </ul>
      )}

      {/* Taste bars */}
      <div className="border-t border-green-50 pt-3 mb-3">
        <TasteBars profile={result.taste_profile} />
      </div>

      {/* Milk options */}
      <div className="flex flex-wrap gap-1.5 mb-3">
        {result.milk_options.map((m) => (
          <span key={m} className="text-xs bg-green-50 text-green-700 border border-green-100 rounded-full px-2 py-0.5">
            {m}
          </span>
        ))}
      </div>

      <Link
        href={`/drinks/${result.drink_id}`}
        className="text-xs text-green-700 hover:text-green-900 underline"
      >
        View details →
      </Link>
    </div>
  );
}
