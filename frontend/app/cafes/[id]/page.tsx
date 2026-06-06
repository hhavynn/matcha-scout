import CafeDetailClient from "./CafeDetailClient";
import ErrorState from "@/components/ErrorState";
import { getCafe, getCafeDrinks, getReviewTargets } from "@/lib/api";
import type { Cafe, Drink } from "@/lib/types";

// Next.js 16: params is a Promise — must await
export default async function CafeDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  let cafe: Cafe | null = null;
  let drinks: Drink[] = [];
  let reviewTargetIds: string[] = [];
  let errorMsg: string | null = null;

  try {
    const results = await Promise.all([getCafe(id), getCafeDrinks(id)]);
    cafe = results[0];
    drinks = results[1];
    try {
      const targets = await getReviewTargets(cafe.region_key, 100, 0);
      reviewTargetIds = targets
        .filter((target) => target.cafe_id === cafe?.id && target.review_count === 0)
        .map((target) => target.id);
    } catch {
      // Review CTAs are helpful but non-critical for the cafe page.
    }
  } catch (err) {
    errorMsg = err instanceof Error ? err.message : "Could not load cafe.";
  }

  if (errorMsg || !cafe) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-10">
        <ErrorState message={errorMsg ?? "Cafe not found."} />
        <p className="text-center text-sm mt-2" style={{ color: "#8c8a78" }}>
          Refresh the page to try again.
        </p>
      </div>
    );
  }

  const cafeMap: Record<string, string> = { [cafe.id]: cafe.name };

  return (
    <CafeDetailClient
      cafe={cafe}
      initialDrinks={drinks}
      cafeMap={cafeMap}
      reviewTargetIds={reviewTargetIds}
    />
  );
}
