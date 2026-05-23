export type ProfileGender = 'woman' | 'man' | 'nonbinary'
export type SwipeDirection = 'smash' | 'pass'
export type Hobby =
  | 'hiking' | 'gaming' | 'cooking' | 'reading' | 'travel'
  | 'music' | 'sports' | 'art' | 'fitness' | 'photography'
  | 'yoga' | 'dancing' | 'movies' | 'pets'

export const ALL_HOBBIES: Hobby[] = [
  'hiking', 'gaming', 'cooking', 'reading', 'travel',
  'music', 'sports', 'art', 'fitness', 'photography',
  'yoga', 'dancing', 'movies', 'pets',
]

export const ALL_GENDERS: ProfileGender[] = ['woman', 'man', 'nonbinary']

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface ProfileOut {
  user_id: number
  display_name: string
  bio: string | null
  birth_date: string | null
  city: string | null
  gender: ProfileGender | null
  height_cm: number | null
  hobbies: Hobby[]
  updated_at: string
}

export interface ProfileUpdateRequest {
  display_name?: string
  bio?: string
  birth_date?: string
  city?: string
  gender?: ProfileGender
  height_cm?: number
  hobbies?: Hobby[]
}

export interface DatingPreferencesOut {
  partner_age_min: number | null
  partner_age_max: number | null
  prefer_same_city: boolean
  partner_genders: ProfileGender[]
  partner_hobbies: Hobby[]
}

export interface DatingPreferencesUpdateRequest {
  partner_age_min?: number | null
  partner_age_max?: number | null
  prefer_same_city?: boolean
  partner_genders?: ProfileGender[]
  partner_hobbies?: Hobby[]
}

export interface DiscoveryBatch {
  profiles: ProfileOut[]
}

export interface SwipeResult {
  swipe_id: number
  match_created: boolean
  match_id: number | null
}

export interface MatchOut {
  id: number
  other_user_id: number
  other_display_name: string | null
  created_at: string
}

export interface MessageOut {
  id: number
  match_id: number
  sender_user_id: number
  body: string
  created_at: string
}

export interface StatsOut {
  total_swipes_made: number
  smashes_received: number
  total_matches: number
  avg_messages_per_match: number | null
}
