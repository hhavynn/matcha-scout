import DrinkCard from "@/components/DrinkCard";
import ErrorState from "@/components/ErrorState";
import { getDrinks, getCafes } from "@/lib/api";
import type { Cafe } from "@/lib/types";

// Always fetch fresh data on every request — drinks change as users add reviews
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
      <div className="max-w-5xl mx-auto px-4 py-10">
        <ErrorState message={errorMsg} />
        <p className="text-center text-sm text-gray-400 mt-2">Refresh the page to try again.</p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-green-900">Browse Drinks</h1>
        <p className="text-green-700 mt-1">
          {drinks.length} drinks from {Object.keys(cafeMap).length} cafes
        </p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {drinks.map((drink) => (
          <DrinkCard key={drink.id} drink={drink} cafeName={cafeMap[drink.cafe_id]} />
        ))}
      </div>
    </div>
  );
}
