export interface Cafe {
  id: string;
  name: string;
  location: string;
  address?: string;
  website?: string;
  created_at: string;
}

export interface Drink {
  id: string;
  cafe_id: string;
  name: string;
  description: string;
  price: number;
  milk_options: string[];
  is_iced: boolean;
  is_hot: boolean;
  image_url?: string;
  created_at: string;
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
  };
  match_score: number;
  match_pct: number;
  reasons: string[];
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
}
