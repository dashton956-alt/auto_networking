/** Typed API calls for the F5 Topology View (ANIF-307). */

import { apiRequest } from "./client";

export interface TopologyInterface {
  name: string;
  ip_address: string | null;
  tags: string[];
}

export interface TopologyDevice {
  name: string;
  role: string;
  platform: string;
  primary_ip: string | null;
  tags: string[];
  custom_fields: Record<string, string>;
  interfaces: TopologyInterface[];
}

export interface TopologyResponse {
  site: string;
  devices: TopologyDevice[];
  connections: [string, string][];
}

export function getTopology(site?: string): Promise<TopologyResponse> {
  return apiRequest<TopologyResponse>("/topology", { params: { site } });
}

/** Intent write-back status for a device, if any (the F5 overlay key). */
export function intentStatus(device: TopologyDevice): string | undefined {
  return device.custom_fields.intent_status || undefined;
}
