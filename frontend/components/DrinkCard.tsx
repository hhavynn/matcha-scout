import Link from "next/link";
import type { Drink } from "@/lib/types";

/* Deterministic colour swatch per drink based on its id */
const SWATCHES: Record<string, string> = {
  "drink-001": "linear-gradient(160deg, #6e8c5a, #4d6e3a)",
  "drink-002": "linear-gradient(160deg, #c9d6ad, #91a978)",
  "drink-003": "linear-gradient(160deg, #d4a0a0, #c97a7a)",
  "drink-004": "linear-gradient(160deg, #9aab7a, #7a8f5a)",
  "drink-005": "linear-gradient(160deg, #ccdfa8, #a2c47a)",
  "drink-006": "linear-gradient(160deg, #c4d4a0, #9ab87a)",
  "drink-007": "linear-gradient(160deg, #c4a07a, #a07850)",
  "drink-008": "linear-gradient(160deg, #5a7048, #3c5030)",
  "drink-009": "linear-gradient(160deg, #c0b0d8, #9080b0)",
  "drink-010": "linear-gradient(160deg, #b8d4a8, #8ab888)",
};

interface Props {
  drink: Drink;
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

export default function DrinkCard({ drink, cafeName }: Props) {
  const swatch = SWATCHES[drink.id] ?? "linear-gradient(160deg, #c9d6ad, #91a978)";
  const tempLabel = temperatureLabel(drink);

  return (
    <Link
      href={`/drinks/${drink.id}`}
      className="block no-underline"
      style={{ textDecoration: "none" }}
    >
      <div
        className="flex flex-col gap-3 cursor-pointer transition-all"
        style={{
          background: "#fffdf8",
          borderRadius: 18,
          padding: 12,
          boxShadow: "inset 0 0 0 1px #e8e1d0, 0 1px 2px rgba(62,52,28,0.05), 0 2px 6px -2px rgba(62,52,28,0.06)",
        }}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLDivElement).style.transform = "translateY(-3px)";
          (e.currentTarget as HTMLDivElement).style.boxShadow = "inset 0 0 0 1px #ded5c1, 0 22px 48px -16px rgba(52,44,22,0.22), 0 6px 16px -8px rgba(52,44,22,0.10)";
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLDivElement).style.transform = "";
          (e.currentTarget as HTMLDivElement).style.boxShadow = "inset 0 0 0 1px #e8e1d0, 0 1px 2px rgba(62,52,28,0.05), 0 2px 6px -2px rgba(62,52,28,0.06)";
        }}
      >
        {/* Image placeholder */}
        <div
          className="ms-drink-img"
          style={{ height: 130, ["--swatch" as string]: swatch, borderRadius: 12 }}
        >
          <div
            className="foam"
            style={{ width: 91, height: 91, top: -26, right: -13 }}
          />
          <span className="ph-tag">drink photo</span>
        </div>

        {/* Content */}
        <div className="flex flex-col gap-2 px-1 pb-1">
          <div className="flex justify-between items-start gap-2">
            <div>
              <div className="ms-serif" style={{ fontSize: 17, color: "#2a3124", lineHeight: 1.15 }}>
                {drink.name}
              </div>
              {cafeName && (
                <div style={{ fontSize: 12, color: "#8c8a78", marginTop: 2 }}>{cafeName}</div>
              )}
            </div>
            <span className="ms-mono" style={{ fontSize: 14, color: "#44563a", fontWeight: 500, flexShrink: 0 }}>
              {drink.price == null ? "Price unavailable" : `$${drink.price.toFixed(2)}`}
            </span>
          </div>

          <p
            style={{
              margin: 0, fontSize: 13, color: "#585e4d", lineHeight: 1.5,
              display: "-webkit-box",
              WebkitLineClamp: 2,
              WebkitBoxOrient: "vertical",
              overflow: "hidden",
            }}
          >
            {drink.description}
          </p>

          <div className="flex flex-wrap gap-1.5">
            {drink.milk_options.slice(0, 3).map((m) => (
              <span key={m} className="ms-pill ms-pill-bare ms-pill-sm">{m}</span>
            ))}
            {drink.milk_options.length > 3 && (
              <span className="ms-pill ms-pill-bare ms-pill-sm">+{drink.milk_options.length - 3}</span>
            )}
            {tempLabel && <span className="ms-pill ms-pill-bare ms-pill-sm">{tempLabel}</span>}
            {drink.source === "admin_curated" && (
              <span className="ms-pill ms-pill-sm" style={{ fontSize: 10, opacity: 0.75 }}>curated</span>
            )}
            {drink.source === "user_submitted" && (
              <span className="ms-pill ms-pill-bare ms-pill-sm" style={{ fontSize: 10, opacity: 0.75 }}>community</span>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}
