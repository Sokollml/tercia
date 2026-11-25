export interface CardView {
  code: string;
  stamps: number;
  threshold: number;
  remaining: number;
  rewardsEarned: number;
  rewardsRedeemed: number;
}

export type Role = 'customer' | 'admin';

export interface MeResponse {
  role: Role;
  user: {
    id: number;
    firstName: string | null;
    username: string | null;
  };
  card: CardView;
}

export interface GrantStampResponse {
  card: CardView;
  rewardGranted: boolean;
  alreadyApplied: boolean;
  customer: {
    firstName: string | null;
    username: string | null;
  };
}

export interface StatsResponse {
  totalCustomers: number;
  activeCards: number;
  totalStamps: number;
  rewardsEarned: number;
  stampsToday: number;
}
