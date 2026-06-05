"use client";

import { useState, useMemo } from "react";
import DrinkCard from "@/components/DrinkCard";
import EmptyState from "@/components/EmptyState";
import { IconSearch } from "@/components/Icons";
import type { Drink } from "@/lib/types";

const FILTERS = [
  { id: "all",     label: "All drinks",  test: () => true },
  { id: "iced",    label: "Iced",         test: (d: Drink) => d.is_iced },
  { id: "hot",     label: "Hot",          test: (d: Drink) => d.is_hot },
  { id: "oat",     label: "Oat milk",     test: (d: Drink) => d.milk_options.includes("oat") },
  { id: "noMilk",  label: "No dairy",     test: (d: Drink) => !d.milk_options.includes("whole") },
];

const SORTS = [
  { value: "curated",  label: "Curated" },
  { value: "priceLow", label: "Price ↑" },
  { value: "priceHigh",label: "Price ↓" },
];

interface Props {
  drinks: Drink[];
  cafeMap: Record<string, string>;
}

export default function DrinksClient({ drinks, cafeMap }: Props) {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("all");
  const [sort, setSort] = useState("curated");

  const filtered = useMemo(() => {
    const f = FILTERS.find((x) => x.id === filter);
    let list = drinks.filter((d) => {
      if (f && !f.test(d)) return false;
      if (query.trim()) {
        const s = (d.name + " " + (cafeMap[d.cafe_id] ?? "") + " " + d.description).toLowerCase();
        if (!s.includes(query.toLowerCase())) return false;
      }
      return true;
    });
    if (sort === "priceLow") list = [...list].sort((a, b) => a.price - b.price);
    if (sort === "priceHigh") list = [...list].sort((a, b) => b.price - a.price);
    return list;
  }, [drinks, filter, query, sort, cafeMap]);

  return (
    <div style={{ maxWidth: 1140, margin: "0 auto", padding: "30px 20px 56px" }}>
      {/* Page header */}
      <div className="flex flex-wrap items-end justify-between gap-4 mb-6">
        <div>
          <span className="ms-eyebrow">The menu</span>
          <h1 className="ms-display" style={{ fontSize: "clamp(24px, 5vw, 34px)", margin: "6px 0 4px", color: "#2a3124" }}>
            Browse drinks
          </h1>
          <p style={{ fontSize: 14.5, color: "#585e4d", margin: 0 }}>
            {drinks.length} matcha drinks from {Object.keys(cafeMap).length} cafes
          </p>
        </div>
        {/* Sort segmented control */}
        <div
          className="flex rounded-full p-1 gap-0.5"
          style={{ background: "#efe8d8", boxShadow: "inset 0 0 0 1px #ded5c1" }}
        >
          {SORTS.map(({ value, label }) => (
            <button
              key={value}
              onClick={() => setSort(value)}
              style={{
                border: "none", cursor: "pointer",
                background: sort === value ? "#fffdf8" : "transparent",
                color: sort === value ? "#2a3124" : "#8c8a78",
                fontWeight: 600, fontSize: 13,
                padding: "7px 14px", borderRadius: 999,
                boxShadow: sort === value ? "var(--shadow-xs)" : "none",
                transition: "all .15s ease",
              }}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Search */}
      <div style={{ position: "relative", marginBottom: 12 }}>
        <span
          style={{
            position: "absolute", left: 14, top: "50%",
            transform: "translateY(-50%)", color: "#aaa794",
            pointerEvents: "none",
          }}
        >
          <IconSearch size={17} />
        </span>
        <input
          className="ms-field"
          style={{ paddingLeft: 44 }}
          placeholder="Search a drink, cafe, or flavor…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>

      {/* Filter chips — horizontal scroll on mobile */}
      <div
        className="flex gap-2 mb-6 overflow-x-auto pb-2"
        style={{ scrollbarWidth: "none" }}
      >
        {FILTERS.map((f) => (
          <button
            key={f.id}
            onClick={() => setFilter(f.id)}
            style={{
              border: "none", cursor: "pointer", whiteSpace: "nowrap",
              background: filter === f.id ? "#56703f" : "#fffdf8",
              color: filter === f.id ? "#fff" : "#585e4d",
              boxShadow: filter === f.id
                ? "0 2px 6px -2px rgba(62,52,28,0.06)"
                : "inset 0 0 0 1px #ded5c1",
              fontWeight: 600, fontSize: 13,
              padding: "9px 16px", borderRadius: 999,
              transition: "all .15s ease",
            }}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Drink grid */}
      {filtered.length === 0 ? (
        <EmptyState
          icon="search"
          title="Nothing matches that yet"
          body="Try a different search or clear your filters to see the full menu."
          action={
            <button
              className="ms-btn ms-btn-ghost ms-btn-sm"
              onClick={() => { setQuery(""); setFilter("all"); }}
            >
              Clear filters
            </button>
          }
        />
      ) : (
        <div
          className="grid gap-4"
          style={{ gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))" }}
        >
          {filtered.map((drink) => (
            <DrinkCard key={drink.id} drink={drink} cafeName={cafeMap[drink.cafe_id]} />
          ))}
        </div>
      )}
    </div>
  );
}
