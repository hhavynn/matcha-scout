export interface Cafe {
  id: string;
  name: string;
  location: string;
  address?: string;
  website?: string;
  created_at: string;
  source?: string;
  external_id?: string;
  external_url?: string;
  rating?: number;
  review_count?: number;
  image_url?: string;
  categories?: string[];
  phone?: string;
  price?: string;
  last_ingested_at?: string;
  region_key?: string;
  region_label?: string;
}

export interface Drink {
  id: string;
  cafe_id: string;
  name: string;
  description: string;
  price: number;
  milk_options: string[];
  is_iced: boolean | null;
  is_hot: boolean | null;
  image_url?: string;
  created_at: string;
  source?: string;
  verification_status?: string;
  submitted_at?: string;
  submitted_by_session?: string;
}

export interface ReviewTargetDrink extends Drink {
  cafe_name: string;
  cafe_location?: string;
  region_key?: string;
  region_label?: string;
  review_count: number;
  confidence_label: string;
  confidence_score: number;
}

export interface DrinkCreate {
  name: string;
  description?: string;
  price?: number;
  milk_options?: string[];
  is_iced?: boolean | null;
  is_hot?: boolean | null;
}

export interface TasteProfile {
  drink_id: string;
  matcha_strength: number;
  sweetness: number;
  creaminess: number;
  earthiness: number;
  bitterness: number;
  review_count: number;
  last_updated: string;
  confidence_label?: string;
  confidence_score?: number;
}

export interface Review {
  id: string;
  drink_id: string;
  raw_text: string;
  parsed_strength: number;
  parsed_sweetness: number;
  parsed_creaminess: number;
  parsed_earthiness: number;
  parsed_bitterness: number;
  confidence: number;
  summary?: string;
  tags?: string[];
  submitted_at: string;
}

export interface ExternalReviewExcerpt {
  id: string;
  cafe_id: string;
  source: string;
  excerpt: string;
  rating?: number;
  author_name?: string;
  time_created?: string;
  external_url?: string;
  ingested_at: string;
}

export interface RecommendationResult {
  drink_id: string;
  drink_name: string;
  cafe_id: string;
  cafe_name?: string;
  price: number;
  milk_options: string[];
  taste_profile: {
    matcha_strength: number;
    sweetness: number;
    creaminess: number;
    earthiness: number;
    bitterness: number;
    review_count: number;
    confidence_label?: string;
    confidence_score?: number;
  };
  match_score: number;
  match_pct: number;
  reasons: string[];
  confidence_label?: string;
  confidence_score?: number;
}

export interface RecommendationParams {
  matcha_strength: number;
  sweetness: number;
  creaminess: number;
  earthiness: number;
  bitterness: number;
  price_max?: number;
  milk_type?: string;
  limit?: number;
  region_key?: string;
}

export type RegionKey = "all" | "san-diego" | "orange-county";

export const REGIONS: { key: RegionKey; label: string }[] = [
  { key: "all", label: "All Regions" },
  { key: "san-diego", label: "San Diego" },
  { key: "orange-county", label: "Orange County" },
];
