/** Typed API calls for the F2 Intent Dashboard. */

import { apiRequest } from "./client";
import type {
  AuditRecord,
  IntentDraft,
  IntentListResponse,
  OrchestrateResponse,
  ValidatedIntent,
  ValidationResult,
} from "./types";

export function listIntents(params: {
  limit?: number;
  offset?: number;
  status?: string;
  service?: string;
}): Promise<IntentListResponse> {
  return apiRequest<IntentListResponse>("/intent/intents", { params });
}

export function getIntent(intentId: string): Promise<ValidatedIntent> {
  return apiRequest<ValidatedIntent>(`/intent/intent/${intentId}`);
}

export function validateIntent(intent: IntentDraft): Promise<ValidationResult> {
  return apiRequest<ValidationResult>("/intent/validate-intent", {
    method: "POST",
    body: { intent },
  });
}

export function orchestrate(intent: IntentDraft, dryRun: boolean): Promise<OrchestrateResponse> {
  return apiRequest<OrchestrateResponse>("/orchestrate", {
    method: "POST",
    body: { intent, dry_run: dryRun },
  });
}

export function getAuditRecords(intentId: string): Promise<AuditRecord[]> {
  return apiRequest<AuditRecord[]>(`/audit/${intentId}`);
}

export function getAuditWhy(intentId: string): Promise<string> {
  return apiRequest<string>(`/audit/${intentId}/why`);
}
