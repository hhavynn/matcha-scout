"use client";

import { useState } from "react";
import Link from "next/link";
import { createDrink } from "@/lib/api";
import { IconCheck, IconLeaf } from "@/components/Icons";
import type { Drink } from "@/lib/types";

const MILK_OPTIONS = ["oat", "whole", "almond", "coconut", "soy", "none"];

interface Props {
  cafeId: string;
  onCreated: (drink: Drink) => void;
}

export default function AddDrinkForm({ cafeId, onCreated }: Props) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [milkOptions, setMilkOptions] = useState<string[]>([]);
  const [isIced, setIsIced] = useState(true);
  const [isHot, setIsHot] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [createdDrink, setCreatedDrink] = useState<Drink | null>(null);

  function toggleMilk(option: string) {
    setMilkOptions((prev) =>
      prev.includes(option) ? prev.filter((m) => m !== option) : [...prev, option]
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) {
      setError("Drink name is required.");
      return;
    }
    const parsedPrice = price.trim() ? parseFloat(price) : undefined;
    if (parsedPrice !== undefined && (isNaN(parsedPrice) || parsedPrice <= 0)) {
      setError("Price must be a positive number.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const drink = await createDrink(cafeId, {
        name: name.trim(),
        description: description.trim() || undefined,
        price: parsedPrice,
        milk_options: milkOptions.length > 0 ? milkOptions : undefined,
        is_iced: isIced,
        is_hot: isHot,
      });
      setCreatedDrink(drink);
      onCreated(drink);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add drink.");
    } finally {
      setLoading(false);
    }
  }

  if (createdDrink) {
    return (
      <div
        className="ms-anim-up"
        style={{
          background: "linear-gradient(180deg, #e7eddc, #fffdf8)",
          borderRadius: 14,
          padding: 18,
          boxShadow: "inset 0 0 0 1px #cdd9b8",
        }}
      >
        <div className="flex items-center gap-2.5 mb-3">
          <span
            style={{
              width: 28, height: 28, borderRadius: 999,
              background: "#56703f", color: "#fff",
              display: "flex", alignItems: "center", justifyContent: "center",
              flexShrink: 0,
            }}
          >
            <IconCheck size={15} color="#fff" />
          </span>
          <div>
            <div style={{ fontWeight: 600, fontSize: 14, color: "#36442e" }}>
              {createdDrink.name} added
            </div>
            <div style={{ fontSize: 12, color: "#5f7850" }}>
              Now add a review to build its taste profile.
            </div>
          </div>
        </div>
        <Link
          href={`/drinks/${createdDrink.id}`}
          className="ms-btn ms-btn-primary ms-btn-sm"
          style={{ textDecoration: "none" }}
        >
          Review it now
        </Link>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      {/* Name */}
      <div className="flex flex-col gap-1.5">
        <label style={{ fontSize: 13, fontWeight: 600, color: "#2a3124" }}>
          Drink name <span style={{ color: "#a64b3e" }}>*</span>
        </label>
        <input
          className="ms-field"
          placeholder="e.g. Iced Oat Matcha Latte"
          value={name}
          onChange={(e) => setName(e.target.value)}
          disabled={loading}
          maxLength={120}
        />
      </div>

      {/* Description */}
      <div className="flex flex-col gap-1.5">
        <label style={{ fontSize: 13, fontWeight: 600, color: "#2a3124" }}>
          Description <span style={{ fontSize: 11, fontWeight: 400, color: "#8c8a78" }}>optional</span>
        </label>
        <textarea
          className="ms-field"
          placeholder="Brief description of the drink…"
          rows={2}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          disabled={loading}
          maxLength={500}
        />
      </div>

      {/* Price */}
      <div className="flex flex-col gap-1.5">
        <label style={{ fontSize: 13, fontWeight: 600, color: "#2a3124" }}>
          Price <span style={{ fontSize: 11, fontWeight: 400, color: "#8c8a78" }}>optional</span>
        </label>
        <input
          className="ms-field"
          style={{ maxWidth: 120 }}
          type="number"
          step="0.01"
          min="0.01"
          placeholder="7.50"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          disabled={loading}
        />
      </div>

      {/* Milk options */}
      <div className="flex flex-col gap-1.5">
        <label style={{ fontSize: 13, fontWeight: 600, color: "#2a3124" }}>
          Milk options <span style={{ fontSize: 11, fontWeight: 400, color: "#8c8a78" }}>optional</span>
        </label>
        <div className="flex flex-wrap gap-2">
          {MILK_OPTIONS.map((opt) => {
            const active = milkOptions.includes(opt);
            return (
              <button
                key={opt}
                type="button"
                onClick={() => toggleMilk(opt)}
                style={{
                  border: "none", cursor: "pointer",
                  background: active ? "#56703f" : "#fffdf8",
                  color: active ? "#fff" : "#585e4d",
                  boxShadow: active
                    ? "0 2px 6px -2px rgba(62,52,28,0.06)"
                    : "inset 0 0 0 1px #ded5c1",
                  fontWeight: 600, fontSize: 13,
                  padding: "7px 14px", borderRadius: 999,
                  transition: "all .15s ease",
                }}
              >
                {opt}
              </button>
            );
          })}
        </div>
      </div>

      {/* Iced / hot toggles */}
      <div className="flex flex-col gap-1.5">
        <label style={{ fontSize: 13, fontWeight: 600, color: "#2a3124" }}>Served as</label>
        <div className="flex gap-2">
          {[
            { label: "Iced", value: "iced" },
            { label: "Hot", value: "hot" },
          ].map(({ label, value }) => {
            const active = value === "iced" ? isIced : isHot;
            return (
              <button
                key={value}
                type="button"
                onClick={() => {
                  if (value === "iced") setIsIced((v) => !v);
                  else setIsHot((v) => !v);
                }}
                style={{
                  border: "none", cursor: "pointer",
                  background: active ? "#56703f" : "#fffdf8",
                  color: active ? "#fff" : "#585e4d",
                  boxShadow: active
                    ? "0 2px 6px -2px rgba(62,52,28,0.06)"
                    : "inset 0 0 0 1px #ded5c1",
                  fontWeight: 600, fontSize: 13,
                  padding: "7px 14px", borderRadius: 999,
                  transition: "all .15s ease",
                }}
              >
                {label}
              </button>
            );
          })}
        </div>
      </div>

      {error && (
        <p style={{ color: "#a64b3e", fontSize: 12.5, margin: 0 }}>{error}</p>
      )}

      <div className="flex items-center justify-between gap-3">
        <span className="flex items-center gap-1.5" style={{ fontSize: 12, color: "#8c8a78" }}>
          <IconLeaf size={13} color="#5f7850" /> Anonymous — no account needed
        </span>
        <button
          type="submit"
          className="ms-btn ms-btn-primary ms-btn-sm"
          disabled={loading || !name.trim()}
          style={{ opacity: !name.trim() ? 0.55 : 1 }}
        >
          {loading ? (
            <>
              <span
                style={{
                  width: 13, height: 13, borderRadius: 999,
                  border: "2px solid rgba(255,255,255,0.5)",
                  borderTopColor: "#fff",
                  display: "inline-block",
                  animation: "ms-spin .8s linear infinite",
                  flexShrink: 0,
                }}
              />
              Adding…
            </>
          ) : (
            "Add drink"
          )}
        </button>
      </div>
    </form>
  );
}
