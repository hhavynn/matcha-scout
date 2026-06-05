import DrinkDetailClient from "./DrinkDetailClient";
import ErrorState from "@/components/ErrorState";
import { getDrink, getTasteProfile, getReviews } from "@/lib/api";
import type { Drink, TasteProfile, Review } from "@/lib/types";

// Next.js 16: params is a Promise — must await
// Data is fetched server-side; no JSX inside try/catch (react-hooks/error-boundaries rule)
export default async function DrinkDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  let drink: Drink | null = null;
  let profile: TasteProfile | null = null;
  let reviews: Review[] = [];
  let errorMsg: string | null = null;

  try {
    const results = await Promise.all([getDrink(id), getTasteProfile(id), getReviews(id)]);
    drink = results[0];
    profile = results[1];
    reviews = results[2];
  } catch (err) {
    errorMsg = err instanceof Error ? err.message : "Could not load drink.";
  }

  if (errorMsg || !drink || !profile) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-10">
        <ErrorState message={errorMsg ?? "Drink not found."} />
        <p className="text-center text-sm text-gray-400 mt-2">Refresh the page to try again.</p>
      </div>
    );
  }

  return (
    <DrinkDetailClient
      drinkId={id}
      initialDrink={drink}
      initialProfile={profile}
      initialReviews={reviews}
    />
  );
}
