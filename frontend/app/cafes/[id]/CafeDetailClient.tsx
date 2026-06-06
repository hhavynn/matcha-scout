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
}

export default function CafeDetailClient({ cafe, initialDrinks, cafeMap }: Props) {
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
          </div>

          <div className="flex flex-col gap-2 items-start">
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
            {cafe.website && (
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
            <DrinkCard key={drink.id} drink={drink} cafeName={cafeMap[drink.cafe_id] ?? cafe.name} />
          ))}
        </div>
      )}
    </div>
  );
}
