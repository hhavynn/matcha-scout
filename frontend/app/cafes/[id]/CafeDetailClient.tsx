"use client";

import { useState } from "react";
import Link from "next/link";
import DrinkCard from "@/components/DrinkCard";
import AddDrinkForm from "@/components/AddDrinkForm";
import { IconBack } from "@/components/Icons";
import type { Cafe, Drink } from "@/lib/types";

interface Props {
  cafe: Cafe;
  initialDrinks: Drink[];
  cafeMap: Record<string, string>;
  reviewTargetIds: string[];
}

export default function CafeDetailClient({ cafe, initialDrinks, cafeMap, reviewTargetIds }: Props) {
  const [drinks, setDrinks] = useState<Drink[]>(initialDrinks);
  const [showForm, setShowForm] = useState(false);

  function handleDrinkCreated(drink: Drink) {
    setDrinks((prev) => [drink, ...prev]);
    setShowForm(false);
  }

  return (
    <div style={{ maxWidth: 1140, margin: "0 auto", padding: "24px 20px 56px" }}>
      {/* Back */}
      <Link
        href="/cafes"
        className="ms-btn-quiet inline-flex items-center gap-1.5 mb-5"
        style={{ textDecoration: "none", marginLeft: -6 }}
      >
        <IconBack size={15} /> All cafes
      </Link>

      {/* Cafe header card */}
      <div
        style={{
          background: "#fffdf8",
          borderRadius: 18,
          padding: "22px 22px",
          marginBottom: 24,
          boxShadow: "inset 0 0 0 1px #e8e1d0, 0 2px 8px -4px rgba(62,52,28,0.08)",
        }}
      >
        <div className="flex flex-wrap justify-between items-start gap-4">
          <div>
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <h1 className="ms-display" style={{ fontSize: 28, margin: 0, color: "#2a3124" }}>
                {cafe.name}
              </h1>
              {cafe.beli_rating != null && (
                <span
                  style={{
                    fontSize: 10.5,
                    fontWeight: 600,
                    color: "#ffffff",
                    background: "#1e293b",
                    border: "1px solid #0f172a",
                    padding: "2px 8px",
                    borderRadius: 999,
                    flexShrink: 0,
                  }}
                >
                  Beli: {cafe.beli_rating.toFixed(1)}
                </span>
              )}
              {cafe.is_popup && (
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 600,
                    color: "#d97706",
                    background: "#fef3c7",
                    border: "1px solid #fde68a",
                    padding: "2px 8px",
                    borderRadius: 999,
                  }}
                >
                  Pop-up
                </span>
              )}
              {cafe.business_status && cafe.business_status !== "open" && (
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 600,
                    color: cafe.business_status === "upcoming" ? "#7c3aed" : "#9a3412",
                    background: cafe.business_status === "upcoming" ? "#f3e8ff" : "#fff7ed",
                    border: `1px solid ${cafe.business_status === "upcoming" ? "#e9d5ff" : "#fed7aa"}`,
                    padding: "2px 8px",
                    borderRadius: 999,
                    textTransform: "capitalize",
                  }}
                >
                  {cafe.business_status}
                </span>
              )}
              {cafe.ceremonial_matcha && (
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 600,
                    color: "#44563a",
                    background: "#edf3e5",
                    border: "1px solid #cdd9b8",
                    padding: "2px 8px",
                    borderRadius: 999,
                  }}
                >
                  Ceremonial matcha
                </span>
              )}
              {cafe.source === "yelp" && (
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 600,
                    color: "#d32323",
                    background: "#fef0f0",
                    border: "1px solid #f8d0d0",
                    padding: "2px 8px",
                    borderRadius: 999,
                  }}
                >
                  Yelp
                </span>
              )}
            </div>
            <p style={{ fontSize: 14, color: "#8c8a78", margin: "0 0 6px" }}>
              {cafe.location}
            </p>
            {cafe.address && (
              <p style={{ fontSize: 13.5, color: "#585e4d", margin: "0 0 6px" }}>
                {cafe.address}
              </p>
            )}
            {cafe.status_note && (
              <p style={{ fontSize: 12.5, color: "#8c5d35", margin: "0 0 6px", maxWidth: 680 }}>
                {cafe.status_note}
              </p>
            )}
            {(cafe.rating != null || cafe.review_count != null || cafe.price) && (
              <div
                className="flex flex-wrap gap-x-3 gap-y-1 items-center"
                style={{ fontSize: 13, color: "#8c8a78" }}
              >
                {cafe.rating != null && (
                  <span>
                    <span style={{ color: "#d4873a" }}>★</span> {cafe.rating.toFixed(1)} on Yelp
                  </span>
                )}
                {cafe.review_count != null && (
                  <span>{cafe.review_count.toLocaleString()} Yelp reviews</span>
                )}
                {cafe.price && <span>{cafe.price}</span>}
              </div>
            )}
            {cafe.menu_summary && (
              <div
                style={{
                  maxWidth: 680,
                  marginTop: 12,
                  padding: "11px 13px",
                  borderRadius: 13,
                  background: "#f5f2ea",
                  boxShadow: "inset 0 0 0 1px #e0dbc8",
                  color: "#585e4d",
                  fontSize: 13,
                  lineHeight: 1.55,
                }}
              >
                {cafe.menu_summary}
                {cafe.menu_verified_at && (
                  <div style={{ color: "#8c8a78", fontSize: 11.5, marginTop: 4 }}>
                    Menu research checked {new Date(cafe.menu_verified_at).toLocaleDateString()}.
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="flex flex-col gap-2 items-start">
            {cafe.menu_url && (
              <a
                href={cafe.menu_url}
                target="_blank"
                rel="noopener noreferrer"
                className="ms-btn ms-btn-primary ms-btn-sm"
                style={{ textDecoration: "none" }}
              >
                Official menu / source ↗
              </a>
            )}
            {cafe.external_url && (
              <a
                href={cafe.external_url}
                target="_blank"
                rel="noopener noreferrer"
                className="ms-btn ms-btn-ghost ms-btn-sm"
                style={{ textDecoration: "none" }}
              >
                View on Yelp ↗
              </a>
            )}
            {cafe.website && cafe.website !== cafe.menu_url && (
              <a
                href={cafe.website}
                target="_blank"
                rel="noopener noreferrer"
                className="ms-btn ms-btn-ghost ms-btn-sm"
                style={{ textDecoration: "none" }}
              >
                Website ↗
              </a>
            )}
          </div>
        </div>
      </div>

      {/* Drinks section */}
      <div className="flex items-center justify-between gap-4 mb-4">
        <div>
          <h2 className="ms-serif" style={{ fontSize: 22, margin: 0, color: "#2a3124" }}>
            Matcha drinks
          </h2>
          <p style={{ fontSize: 13, color: "#8c8a78", margin: "3px 0 0" }}>
            {drinks.length === 0
              ? "No drinks added yet."
              : `${drinks.length} ${drinks.length === 1 ? "drink" : "drinks"}`}
          </p>
        </div>
        {!showForm && (
          <button
            className="ms-btn ms-btn-primary ms-btn-sm"
            onClick={() => setShowForm(true)}
          >
            + Add a drink
          </button>
        )}
      </div>

      {/* Add drink form */}
      {showForm && (
        <div
          style={{
            background: "#fffdf8",
            borderRadius: 18,
            padding: "20px",
            marginBottom: 20,
            boxShadow: "inset 0 0 0 1px #cdd9b8, var(--shadow-sm)",
          }}
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="ms-serif" style={{ fontSize: 17, margin: 0, color: "#2a3124" }}>
              Add a drink you tried
            </h3>
            <button
              className="ms-btn-quiet"
              style={{ fontSize: 13, color: "#8c8a78" }}
              onClick={() => setShowForm(false)}
            >
              Cancel
            </button>
          </div>
          <AddDrinkForm cafeId={cafe.id} onCreated={handleDrinkCreated} />
        </div>
      )}

      {/* Empty state */}
      {drinks.length === 0 && !showForm && (
        <div
          style={{
            background: "#fffdf8",
            borderRadius: 18,
            padding: "36px 24px",
            textAlign: "center",
            boxShadow: "inset 0 0 0 1px #e8e1d0",
          }}
        >
          <p className="ms-serif" style={{ fontSize: 18, color: "#2a3124", margin: "0 0 6px" }}>
            Know their matcha?
          </p>
          <p style={{ fontSize: 14, color: "#8c8a78", margin: "0 0 4px" }}>
            Add the first verified drink and help others find their perfect pour.
          </p>
          <p style={{ fontSize: 12.5, color: "#aaa794", margin: "0 0 16px" }}>
            Only add drinks you&apos;ve personally seen on the menu or ordered yourself.
          </p>
          <button
            className="ms-btn ms-btn-primary ms-btn-sm"
            onClick={() => setShowForm(true)}
          >
            Add the first drink
          </button>
        </div>
      )}

      {/* Drinks grid */}
      {drinks.length > 0 && (
        <div
          className="grid gap-4"
          style={{ gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))" }}
        >
          {drinks.map((drink) => (
            <div key={drink.id} className="flex flex-col gap-2">
              <DrinkCard drink={drink} cafeName={cafeMap[drink.cafe_id] ?? cafe.name} />
              {reviewTargetIds.includes(drink.id) && (
                <Link
                  href={`/drinks/${drink.id}#review`}
                  className="ms-btn ms-btn-ghost ms-btn-sm"
                  style={{ textDecoration: "none", justifyContent: "center" }}
                >
                  Be the first to review
                </Link>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
