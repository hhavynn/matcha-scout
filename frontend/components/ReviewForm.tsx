"use client";

import { useState } from "react";
import { submitReview } from "@/lib/api";
import type { Review } from "@/lib/types";

interface Props {
  drinkId: string;
  onSubmitted: (review: Review) => void;
}

export default function ReviewForm({ drinkId, onSubmitted }: Props) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (text.trim().length < 10) {
      setError("Review must be at least 10 characters.");
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

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Describe the taste — strong? earthy? creamy? sweet? The AI will parse your words into taste ratings."
        rows={3}
        className="w-full border border-green-200 rounded-xl px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-green-400"
        disabled={loading}
      />
      {error && <p className="text-red-500 text-xs">{error}</p>}
      <button
        type="submit"
        disabled={loading || text.trim().length < 10}
        className="bg-green-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? "Analyzing…" : "Submit Review"}
      </button>
    </form>
  );
}
