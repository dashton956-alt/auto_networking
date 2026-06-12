/** Typed API calls for the F6 Risk & Governance Dashboard. */

import { apiRequest } from "./client";

export interface CouncilSession {
  council_id: string;
  council_type: string; // build_time | runtime | review
  decision: string;
  triggered_by: string;
  trigger_timestamp: string;
  session_close_timestamp: string | null;
  decision_rationale: string | null;
  intent_id: string | null;
}

export interface CouncilSessionsResponse {
  total: number;
  sessions: CouncilSession[];
}

export interface StrikeRecord {
  strike_id: string;
  agent_id: string;
  intent_id: string;
  reason: string;
  recorded_at: string;
}

export interface StrikesResponse {
  total: number;
  strikes: StrikeRecord[];
}

export function getCouncilSessions(limit = 20): Promise<CouncilSessionsResponse> {
  return apiRequest<CouncilSessionsResponse>("/council/sessions", { params: { limit } });
}

export function getStrikes(limit = 50): Promise<StrikesResponse> {
  return apiRequest<StrikesResponse>("/ethics/strikes", { params: { limit } });
}
