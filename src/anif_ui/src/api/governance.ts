/** Typed API calls for the F3 Approval Queue (ANIF-404 §4.4–4.5). */

import { apiRequest } from "./client";

export interface TicketSummary {
  ticket_id: string;
  intent_id: string;
  requested_by: string;
  risk_score: number;
  decision_summary: string;
  created_at: string;
  expires_at: string;
}

export interface TicketListResponse {
  pending_count: number;
  tickets: TicketSummary[];
}

export interface ApproveResponse {
  ticket_id: string;
  status: string;
  approved_by: string;
  approved_at: string;
  audit_record_id: string;
}

export interface RejectResponse {
  ticket_id: string;
  status: string;
  rejected_by: string;
  rejected_at: string;
  audit_record_id: string;
}

/** Operator identity sent as X-Operator-* headers. RBAC is enforced server-side. */
export interface Operator {
  operatorId: string;
  role: string;
}

function operatorHeaders(operator: Operator): Record<string, string> {
  return {
    "X-Operator-Id": operator.operatorId,
    "X-Operator-Roles": operator.role,
  };
}

export function listTickets(): Promise<TicketListResponse> {
  return apiRequest<TicketListResponse>("/governance/tickets");
}

export function approveTicket(
  ticketId: string,
  operator: Operator,
  notes: string | null,
): Promise<ApproveResponse> {
  return apiRequest<ApproveResponse>(`/governance/approve/${ticketId}`, {
    method: "POST",
    body: { approver_role: operator.role, notes: notes || null },
    headers: operatorHeaders(operator),
  });
}

export function rejectTicket(
  ticketId: string,
  operator: Operator,
  reason: string,
): Promise<RejectResponse> {
  return apiRequest<RejectResponse>(`/governance/reject/${ticketId}`, {
    method: "POST",
    body: { reason },
    headers: operatorHeaders(operator),
  });
}
