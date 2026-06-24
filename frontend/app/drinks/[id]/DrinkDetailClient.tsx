"use client";

import { useState } from "react";
import Link from "next/link";
import TasteBars from "@/components/TasteBars";
import ReviewForm, { ParsedResultPanel } from "@/components/ReviewForm";
import ConfidenceBadge from "@/components/ConfidenceBadge";
import { getTasteProfile, getReviews } from "@/lib/api";
import { IconBack } from "@/components/Icons";
import type { Drink, TasteProfile, Review } from "@/lib/types";

interface Props {
  drinkId: string;
  initialDrink: Drink;
  initialProfile: TasteProfile;
  initialReviews: Review[];
  cafeName?: string;
}

function temperatureLabel(drink: Drink): string | null {
  if (drink.is_iced === true && drink.is_hot === true) return "iced + hot";
  if (drink.is_iced === true && drink.is_hot === false) return "iced only";
  if (drink.is_hot === true && drink.is_iced === false) return "hot only";
  if (drink.is_iced === true) return "iced";
  if (drink.is_hot === true) return "hot";
  return null;
}

export default function DrinkDetailClient({
  drinkId,
  initialDrink: drink,
  initialProfile,
  initialReviews,
  cafeName,
}: Props) {
  const [profile, setProfile] = useState<TasteProfile>(initialProfile);
  const [reviews, setReviews] = useState<Review[]>(initialReviews);
  const [latestReview, setLatestReview] = useState<Review | null>(null);
  const tempLabel = temperatureLabel(drink);
  const isVerifiedDrink =
    drink.source === "admin_curated" ||
    drink.verification_status === "admin_curated" ||
    drink.verification_status === "admin_verified";

  async function handleReviewSubmitted(review: Review) {
    setLatestReview(review);
    try {
      const [updatedProfile, updatedReviews] = await Promise.all([
        getTasteProfile(drinkId),
        getReviews(drinkId),
      ]);
      setProfile(updatedProfile);
      setReviews(updatedReviews);
    } catch {
      // non-critical
    }
  }

  return (
    <div style={{ maxWidth: 860, margin: "0 auto", padding: "24px 20px 56px" }}>
      {/* Back link */}
      <Link
        href="/drinks"
        className="ms-btn-quiet inline-flex items-center gap-1.5 mb-5"
        style={{ textDecoration: "none", marginLeft: -6 }}
      >
        <IconBack size={15} /> All drinks
      </Link>

      {/* ── Desktop 2-column layout ──────────────────────────────────── */}
      <div
        className="grid gap-5 items-start detail-2col"
        style={{ gridTemplateColumns: "1fr" }}
      >
        {/* LEFT — hero + taste profile */}
        <div
          className="flex flex-col gap-5 detail-left"
        >
          {/* Hero card */}
          <div
            style={{
              background: "#fffdf8",
              borderRadius: 24,
              overflow: "hidden",
              boxShadow: "inset 0 0 0 1px #e8e1d0, 0 6px 20px -8px rgba(58,48,24,0.14)",
            }}
          >
            {/* Image placeholder */}
            <div
              style={{
                height: 200,
                background: "linear-gradient(160deg, #6e8c5a, #4d6e3a)",
                position: "relative", overflow: "hidden",
              }}
            >
              <div style={{ position: "absolute", inset: 0, background: "repeating-linear-gradient(135deg, rgba(255,255,255,0.16) 0 10px, transparent 10px 20px)" }} />
              <div
                style={{
                  position: "absolute", top: -50, right: -25,
                  width: 140, height: 140, borderRadius: 999,
                  background: "radial-gradient(circle at 38% 34%, rgba(255,255,255,0.55), rgba(255,255,255,0.06) 70%)",
                }}
              />
              {/* Temp pills on image */}
              <div className="flex gap-2" style={{ position: "absolute", top: 12, right: 12 }}>
                {tempLabel && (
                  <span className="ms-pill ms-pill-bare ms-pill-sm" style={{ background: "rgba(255,253,248,0.85)" }}>
                    {tempLabel}
                  </span>
                )}
              </div>
            </div>

            {/* Drink info */}
            <div style={{ padding: "20px 20px 22px" }}>
              <div className="flex justify-between items-start gap-4">
                <div>
                  <h1 className="ms-display" style={{ fontSize: 27, margin: 0, color: "#2a3124" }}>
                    {drink.name}
                  </h1>
                  {cafeName && (
                    <div style={{ fontSize: 13, color: "#8c8a78", marginTop: 5 }}>
                      📍 {cafeName}
                    </div>
                  )}
                </div>
                <div className="ms-mono" style={{ fontSize: 24, color: "#44563a", fontWeight: 500, flexShrink: 0 }}>
                  {drink.price == null ? "Price unavailable" : `$${drink.price.toFixed(2)}`}
                </div>
              </div>
              <p style={{ fontSize: 14.5, color: "#585e4d", lineHeight: 1.6, marginTop: 12, marginBottom: 14 }}>
                {drink.description}
              </p>
              <div className="flex flex-wrap gap-2">
                {drink.milk_options.map((m) => (
                  <span key={m} className="ms-pill ms-pill-bare ms-pill-sm">{m}</span>
                ))}
              </div>
              {(drink.verification_url || drink.verification_source) && (
                <div
                  style={{
                    marginTop: 14,
                    paddingTop: 12,
                    borderTop: "1px solid #e8e1d0",
                    fontSize: 12,
                    color: "#8c8a78",
                  }}
                >
                  Verified from{" "}
                  {drink.verification_url ? (
                    <a
                      href={drink.verification_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ color: "#5f7850", fontWeight: 600, textDecoration: "none" }}
                    >
                      {drink.verification_source || "official menu"} ↗
                    </a>
                  ) : (
                    drink.verification_source
                  )}
                  {drink.verified_at && (
                    <span> · checked {new Date(drink.verified_at).toLocaleDateString()}</span>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Taste profile panel */}
          <div
            style={{
              background: "#fffdf8",
              borderRadius: 18,
              padding: "20px",
              boxShadow: "inset 0 0 0 1px #e8e1d0, var(--shadow-sm)",
            }}
          >
            <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
              <h2 className="ms-serif" style={{ fontSize: 19, margin: 0, color: "#2a3124" }}>
                Taste Profile
              </h2>
              <ConfidenceBadge
                label={profile.confidence_label}
                reviewCount={profile.review_count}
              />
            </div>
            <TasteBars profile={profile} animate />
            {profile.confidence_label === "unrated" && (
              <p style={{ fontSize: 12, color: "#aaa794", marginTop: 10, lineHeight: 1.5 }}>
                Neutral values shown — confidence improves as Matcha Scout reviews come in.
              </p>
            )}
            <p style={{ fontSize: 11.5, color: "#c0bba8", marginTop: 6 }}>
              Confidence is based on Matcha Scout reviews, not Yelp ratings.
            </p>
          </div>
        </div>

        {/* RIGHT — reviews + review form */}
        <div
          className="flex flex-col gap-5 detail-right"
        >
          {/* Parsed result panel (shown after submission) */}
          {latestReview && (
            <ParsedResultPanel review={latestReview} />
          )}

          {/* Submit review */}
          <div
            id="review"
            style={{
              background: "#fffdf8",
              borderRadius: 18,
              padding: "20px",
              boxShadow: "inset 0 0 0 1px #e8e1d0, var(--shadow-sm)",
            }}
          >
            <h2 className="ms-serif" style={{ fontSize: 19, margin: "0 0 4px", color: "#2a3124" }}>
              Write a review
            </h2>
            <p style={{ fontSize: 13, color: "#8c8a78", marginBottom: 16 }}>
              {isVerifiedDrink && profile.review_count === 0
                ? "Be the first Matcha Scout reviewer for this verified drink."
                : "Describe what you tasted. The AI parses your words into structured taste ratings."}
            </p>
            {isVerifiedDrink && profile.review_count <= 1 && (
              <div
                style={{
                  background: "#f5f2ea",
                  borderRadius: 14,
                  padding: "10px 12px",
                  marginBottom: 14,
                  boxShadow: "inset 0 0 0 1px #e0dbc8",
                  color: "#585e4d",
                  fontSize: 12.5,
                  lineHeight: 1.5,
                }}
              >
                Reviews here improve recommendations for everyone. Yelp ratings and excerpts do not count toward this confidence score.
              </div>
            )}
            <ReviewForm drinkId={drinkId} onSubmitted={handleReviewSubmitted} />
          </div>

          {/* Community reviews */}
          <div
            style={{
              background: "#fffdf8",
              borderRadius: 18,
              padding: "20px",
              boxShadow: "inset 0 0 0 1px #e8e1d0, var(--shadow-sm)",
            }}
          >
            <h2 className="ms-serif" style={{ fontSize: 19, margin: "0 0 16px", color: "#2a3124" }}>
              Community Reviews{" "}
              <span className="ms-mono" style={{ fontSize: 14, color: "#8c8a78", fontWeight: 400 }}>
                ({reviews.length})
              </span>
            </h2>

            {reviews.length === 0 ? (
              <p style={{ fontSize: 14, color: "#8c8a78" }}>No reviews yet — be the first!</p>
            ) : (
              <div className="flex flex-col">
                {reviews.map((r, i) => (
                  <div
                    key={r.id}
                    style={{
                      paddingTop: i === 0 ? 0 : 16,
                      paddingBottom: 16,
                      borderTop: i === 0 ? "none" : "1px solid #e8e1d0",
                    }}
                  >
                    {/* Quote */}
                    <p
                      className="ms-serif-i"
                      style={{ fontSize: 15.5, color: "#2a3124", lineHeight: 1.55, margin: "0 0 10px" }}
                    >
                      &ldquo;{r.raw_text}&rdquo;
                    </p>

                    {/* Tags */}
                    {r.tags && r.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mb-2">
                        {r.tags.map((t) => (
                          <span key={t} className="ms-pill ms-pill-sm">{t}</span>
                        ))}
                      </div>
                    )}

                    {/* Meta footer */}
                    <div
                      className="ms-mono flex flex-wrap gap-x-2 gap-y-1 items-center"
                      style={{ fontSize: 11, color: "#aaa794" }}
                    >
                      <span>S·{r.parsed_strength}</span>
                      <span>Sw·{r.parsed_sweetness}</span>
                      <span>Cr·{r.parsed_creaminess}</span>
                      <span>E·{r.parsed_earthiness}</span>
                      <span>B·{r.parsed_bitterness}</span>
                      {r.confidence != null && (
                        <>
                          <span>·</span>
                          <span>{(r.confidence * 100).toFixed(0)}% conf</span>
                        </>
                      )}
                      <span>·</span>
                      <span>{new Date(r.submitted_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
