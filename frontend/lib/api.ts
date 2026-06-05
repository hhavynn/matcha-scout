import type {
  Cafe,
  Drink,
  DrinkCreate,
  TasteProfile,
  Review,
  ExternalReviewExcerpt,
  RecommendationResult,
  RecommendationParams,
} from "./types";

function getBaseUrl(): string {
  if (typeof window === "undefined") {
    return (
      process.env.SERVER_API_BASE_URL ??
      process.env.NEXT_PUBLIC_API_BASE_URL ??
      "http://localhost:8000"
    );
  }

  return process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${getBaseUrl()}${path}`, {
    cache: "no-store", // Never serve stale data from Next.js fetch cache
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail ?? JSON.stringify(body);
    } catch {
      // ignore parse error
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export async function getCafes(): Promise<Cafe[]> {
  return apiFetch<Cafe[]>("/cafes");
}

export async function getCafe(id: string): Promise<Cafe> {
  return apiFetch<Cafe>(`/cafes/${id}`);
}

export async function getDrinks(): Promise<Drink[]> {
  return apiFetch<Drink[]>("/drinks");
}

export async function getDrink(id: string): Promise<Drink> {
  return apiFetch<Drink>(`/drinks/${id}`);
}

export async function getTasteProfile(drinkId: string): Promise<TasteProfile> {
  return apiFetch<TasteProfile>(`/drinks/${drinkId}/taste-profile`);
}

export async function getReviews(drinkId: string): Promise<Review[]> {
  return apiFetch<Review[]>(`/drinks/${drinkId}/reviews`);
}

export async function submitReview(
  drinkId: string,
  rawText: string
): Promise<Review> {
  return apiFetch<Review>("/reviews", {
    method: "POST",
    body: JSON.stringify({ drink_id: drinkId, raw_text: rawText }),
  });
}

export async function getCafeDrinks(cafeId: string): Promise<Drink[]> {
  return apiFetch<Drink[]>(`/cafes/${cafeId}/drinks`);
}

export async function createDrink(
  cafeId: string,
  payload: DrinkCreate
): Promise<Drink> {
  return apiFetch<Drink>(`/cafes/${cafeId}/drinks`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getCafeExternalReviews(
  cafeId: string
): Promise<ExternalReviewExcerpt[]> {
  return apiFetch<ExternalReviewExcerpt[]>(`/cafes/${cafeId}/external-reviews`);
}

export async function getRecommendations(
  params: RecommendationParams
): Promise<RecommendationResult[]> {
  const qs = new URLSearchParams();
  qs.set("matcha_strength", String(params.matcha_strength));
  qs.set("sweetness", String(params.sweetness));
  qs.set("creaminess", String(params.creaminess));
  qs.set("earthiness", String(params.earthiness));
  qs.set("bitterness", String(params.bitterness));
  if (params.price_max != null) qs.set("price_max", String(params.price_max));
  if (params.milk_type) qs.set("milk_type", params.milk_type);
  if (params.limit != null) qs.set("limit", String(params.limit));
  return apiFetch<RecommendationResult[]>(`/recommendations?${qs.toString()}`);
}
