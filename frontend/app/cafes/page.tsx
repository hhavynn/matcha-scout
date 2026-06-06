import ErrorState from "@/components/ErrorState";
import CafesClient from "./CafesClient";
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

  return <CafesClient cafes={cafes} />;
}
