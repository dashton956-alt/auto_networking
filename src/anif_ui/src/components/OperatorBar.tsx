import type { Operator } from "@/api/governance";
import { Input, Select } from "@/components";

const ROLES = [
  { value: "network_engineer", label: "network_engineer (can reject)" },
  { value: "senior_engineer", label: "senior_engineer (can approve + reject)" },
];

interface OperatorBarProps {
  operator: Operator;
  onChange: (operator: Operator) => void;
}

/**
 * "Acting as" identity control. Sent as X-Operator-Id / X-Operator-Roles;
 * the server enforces RBAC regardless of what is claimed here (placeholder
 * until X.509 auth supplies identity).
 */
export function OperatorBar({ operator, onChange }: OperatorBarProps) {
  return (
    <fieldset className="rounded-lg border border-chrome-200 bg-chrome-50 px-4 py-3">
      <legend className="px-1 text-xs font-semibold uppercase tracking-wide text-chrome-600">
        Acting as
      </legend>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <Input
          label="Operator ID"
          id="operator-id"
          value={operator.operatorId}
          onChange={(e) => onChange({ ...operator, operatorId: e.target.value })}
        />
        <Select
          label="Role"
          id="operator-role"
          options={ROLES}
          value={operator.role}
          onChange={(e) => onChange({ ...operator, role: e.target.value })}
          helperText="Verified server-side on every request"
        />
      </div>
    </fieldset>
  );
}
