import ErrorState from "@/components/ErrorState";
import CafeCard from "@/components/CafeCard";
import { getCafes } from "@/lib/api";
import type { Cafe } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function CafesPage() {
  let cafes: Cafe[] = [];
  let errorMsg: string | null = null;

  try {
    cafes = await getCafes();
  } catch (err) {
    errorMsg = err instanceof Error ? err.message : "Could not load cafes.";
  }

  if (errorMsg) {
    return (
      <div style={{ maxWidth: 1140, margin: "0 auto", padding: "30px 20px" }}>
        <ErrorState message={errorMsg} />
        <p className="text-center text-sm mt-2" style={{ color: "#8c8a78" }}>
          Refresh the page to try again.
        </p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 1140, margin: "0 auto", padding: "30px 20px 56px" }}>
      <div className="mb-7">
        <span className="ms-eyebrow">Where to find it</span>
        <h1
          className="ms-display"
          style={{ fontSize: "clamp(24px, 5vw, 34px)", margin: "6px 0 4px", color: "#2a3124" }}
        >
          Matcha cafes
        </h1>
        <p style={{ fontSize: 14.5, color: "#585e4d", margin: 0 }}>
          {cafes.length} {cafes.length === 1 ? "cafe" : "cafes"} — browse drinks and add ones you&apos;ve tried.
        </p>
      </div>

      {cafes.length === 0 ? (
        <div
          style={{
            background: "#fffdf8",
            borderRadius: 18,
            padding: "32px 24px",
            textAlign: "center",
            boxShadow: "inset 0 0 0 1px #e8e1d0",
          }}
        >
          <p style={{ color: "#8c8a78", fontSize: 14 }}>No cafes yet.</p>
        </div>
      ) : (
        <div
          className="grid gap-4"
          style={{ gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))" }}
        >
          {cafes.map((cafe: Cafe) => (
            <CafeCard key={cafe.id} cafe={cafe} />
          ))}
        </div>
      )}
    </div>
  );
}
