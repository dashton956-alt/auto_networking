/** Typed API calls for the F4 Audit Trail Viewer (ANIF-107 §4.5). */

import { apiRequest } from "./client";
import type { AuditRecord } from "./types";

export interface AuditFilters {
  stage?: string;
  outcome?: string;
  environment?: string;
  operator_id?: string;
  date_from?: string;
  date_to?: string;
  limit?: number;
  offset?: number;
}

export interface ChainVerification {
  valid: boolean;
  broken_at: string | null;
  record_count: number;
}

export function listAuditRecords(filters: AuditFilters): Promise<AuditRecord[]> {
  return apiRequest<AuditRecord[]>("/audit", { params: { ...filters } });
}

export function verifyChain(intentId: string): Promise<ChainVerification> {
  return apiRequest<ChainVerification>(`/audit/${intentId}/verify`);
}
