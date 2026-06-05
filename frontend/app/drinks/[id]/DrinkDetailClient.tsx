"use client";

import { useState } from "react";
import Link from "next/link";
import TasteBars from "@/components/TasteBars";
import ReviewForm from "@/components/ReviewForm";
import { getTasteProfile, getReviews } from "@/lib/api";
import type { Drink, TasteProfile, Review } from "@/lib/types";

interface Props {
  drinkId: string;
  initialDrink: Drink;
  initialProfile: TasteProfile;
  initialReviews: Review[];
}

// Client component — handles only interactive state (review submission, local updates)
// Initial data is server-fetched and passed as props
export default function DrinkDetailClient({
  drinkId,
  initialDrink,
  initialProfile,
  initialReviews,
}: Props) {
  const [profile, setProfile] = useState<TasteProfile>(initialProfile);
  const [reviews, setReviews] = useState<Review[]>(initialReviews);
  const [latestReview, setLatestReview] = useState<Review | null>(null);

  async function handleReviewSubmitted(review: Review) {
    setLatestReview(review);
    // Refresh profile + reviews after aggregation update (triggered by user action, not an effect)
    try {
      const [updatedProfile, updatedReviews] = await Promise.all([
        getTasteProfile(drinkId),
        getReviews(drinkId),
      ]);
      setProfile(updatedProfile);
      setReviews(updatedReviews);
    } catch {
      // non-critical — the review was submitted; display update can fail silently
    }
  }

  const drink = initialDrink;

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      {/* Breadcrumb */}
      <div className="text-sm text-green-600 mb-6">
        <Link href="/drinks" className="hover:underline">Drinks</Link>
        <span className="mx-2">→</span>
        <span className="text-green-900">{drink.name}</span>
      </div>

      {/* Header */}
      <div className="bg-white rounded-2xl border border-green-100 shadow-sm p-6 mb-6">
        <div className="flex items-start justify-between gap-4 mb-3">
          <h1 className="text-2xl font-bold text-green-900">{drink.name}</h1>
          <span className="text-green-700 font-semibold text-xl shrink-0">
            ${drink.price.toFixed(2)}
          </span>
        </div>
        <p className="text-gray-600 leading-relaxed mb-4">{drink.description}</p>
        <div className="flex flex-wrap gap-2">
          {drink.milk_options.map((m) => (
            <span key={m} className="text-xs bg-green-50 text-green-700 border border-green-100 rounded-full px-2.5 py-1">
              {m}
            </span>
          ))}
          {drink.is_iced && (
            <span className="text-xs bg-blue-50 text-blue-600 border border-blue-100 rounded-full px-2.5 py-1">iced</span>
          )}
          {drink.is_hot && (
            <span className="text-xs bg-red-50 text-red-500 border border-red-100 rounded-full px-2.5 py-1">hot</span>
          )}
        </div>
      </div>

      {/* Taste profile */}
      <div className="bg-white rounded-2xl border border-green-100 shadow-sm p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-green-900">Taste Profile</h2>
          <span className="text-xs text-gray-400">
            Based on {profile.review_count} {profile.review_count === 1 ? "review" : "reviews"}
            {profile.review_count === 0 && " — seed data"}
          </span>
        </div>
        <TasteBars profile={profile} />
      </div>

      {/* Latest submission result */}
      {latestReview && (
        <div className="bg-green-50 border border-green-200 rounded-2xl p-5 mb-6">
          <p className="text-sm font-semibold text-green-800 mb-3">✓ Review submitted and parsed!</p>
          <div className="grid grid-cols-5 gap-2 text-center text-xs">
            {(
              [
                ["Strength", latestReview.parsed_strength],
                ["Sweetness", latestReview.parsed_sweetness],
                ["Creaminess", latestReview.parsed_creaminess],
                ["Earthiness", latestReview.parsed_earthiness],
                ["Bitterness", latestReview.parsed_bitterness],
              ] as [string, number][]
            ).map(([label, val]) => (
              <div key={label} className="bg-white rounded-lg py-2">
                <div className="font-bold text-green-700 text-base">{val}</div>
                <div className="text-gray-500">{label}</div>
              </div>
            ))}
          </div>
          {latestReview.tags && latestReview.tags.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {latestReview.tags.map((t) => (
                <span key={t} className="text-xs bg-green-100 text-green-800 rounded-full px-2 py-0.5">{t}</span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Submit review */}
      <div className="bg-white rounded-2xl border border-green-100 shadow-sm p-6 mb-6">
        <h2 className="font-semibold text-green-900 mb-1">Submit a Review</h2>
        <p className="text-xs text-gray-500 mb-4">
          Describe what you tasted. The AI will parse your words into taste ratings that update
          this drink&apos;s profile.
        </p>
        <ReviewForm drinkId={drinkId} onSubmitted={handleReviewSubmitted} />
      </div>

      {/* Reviews list */}
      <div className="bg-white rounded-2xl border border-green-100 shadow-sm p-6">
        <h2 className="font-semibold text-green-900 mb-4">
          Community Reviews ({reviews.length})
        </h2>
        {reviews.length === 0 ? (
          <p className="text-sm text-gray-500">No reviews yet. Be the first!</p>
        ) : (
          <div className="space-y-4">
            {reviews.map((r) => (
              <div key={r.id} className="border-b border-green-50 pb-4 last:border-0 last:pb-0">
                <p className="text-sm text-gray-700 mb-2 italic">&ldquo;{r.raw_text}&rdquo;</p>
                <div className="flex flex-wrap gap-2 text-xs text-gray-500">
                  <span>Strength: <strong>{r.parsed_strength}</strong></span>
                  <span>·</span>
                  <span>Sweetness: <strong>{r.parsed_sweetness}</strong></span>
                  <span>·</span>
                  <span>Creaminess: <strong>{r.parsed_creaminess}</strong></span>
                  <span>·</span>
                  <span>Earthiness: <strong>{r.parsed_earthiness}</strong></span>
                  <span>·</span>
                  <span>Bitterness: <strong>{r.parsed_bitterness}</strong></span>
                </div>
                {r.tags && r.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-1.5">
                    {r.tags.map((t) => (
                      <span key={t} className="text-xs bg-gray-100 text-gray-600 rounded-full px-2 py-0.5">{t}</span>
                    ))}
                  </div>
                )}
                <p className="text-xs text-gray-400 mt-1">
                  {new Date(r.submitted_at).toLocaleDateString()}
                  {r.confidence != null && ` · confidence ${(r.confidence * 100).toFixed(0)}%`}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
