import DrinksClient from "./DrinksClient";
import ErrorState from "@/components/ErrorState";
import { getDrinks, getCafes } from "@/lib/api";
import type { Cafe } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function DrinksPage() {
  let errorMsg: string | null = null;
  let drinks = [] as Awaited<ReturnType<typeof getDrinks>>;
  let cafeMap: Record<string, string> = {};

  try {
    const [drinksData, cafesData] = await Promise.all([getDrinks(), getCafes()]);
    drinks = drinksData;
    cafeMap = Object.fromEntries(cafesData.map((c: Cafe) => [c.id, c.name]));
  } catch (err) {
    errorMsg = err instanceof Error ? err.message : "Could not load drinks. Is the backend running?";
  }

  if (errorMsg) {
    return (
      <div style={{ maxWidth: 1140, margin: "0 auto", padding: "30px 20px" }}>
        <ErrorState message={errorMsg} />
        <p className="text-center text-sm mt-2" style={{ color: "#8c8a78" }}>Refresh the page to try again.</p>
      </div>
    );
  }

  return <DrinksClient drinks={drinks} cafeMap={cafeMap} />;
}
