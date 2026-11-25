export type Urgency = 'low' | 'medium' | 'high';

export type OrderUserStatus = 'new' | 'interested' | 'hidden' | 'responded';

export type SortKey = 'new' | 'budget' | 'urgency';

export interface Order {
  id: number;
  source_chat: string;
  author_username: string | null;
  raw_text: string;
  service_type: string | null;
  summary: string | null;
  budget: number | null;
  urgency: Urgency;
  languages: string[];
  skills_required: string[];
  message_link: string | null;
  created_at: string;
  user_status: OrderUserStatus;
  user_note: string | null;
}

export interface UserSettings {
  skills: string[];
  keywords: string[];
  min_budget: number | null;
  languages: string[];
  service_types: string[];
}

export interface OrderFilters {
  service_type?: string;
  urgency?: Urgency;
  min_budget?: number;
  skills?: string[];
  languages?: string[];
  q?: string;
  sort?: SortKey;
}

export const EMPTY_SETTINGS: UserSettings = {
  skills: [],
  keywords: [],
  min_budget: null,
  languages: ['ru'],
  service_types: [],
};

export const SERVICE_TYPES: string[] = [
  'design',
  'dev',
  'copywriting',
  'smm',
  'video',
  'marketing',
  'audio',
  '3d',
  'other',
];

export const LANGUAGES: string[] = ['ru', 'en', 'uk', 'es', 'de'];
