import { Route, Routes } from "react-router-dom";
import { AppShell } from "@/layouts/AppShell";
import DesignSystemPage from "@/pages/DesignSystemPage";

function PlaceholderPage({ title }: { title: string }) {
  return (
    <div>
      <h1 className="text-2xl font-bold text-chrome-900">{title}</h1>
      <p className="mt-2 text-sm text-chrome-600">Implementation pending — coming in F2–F6.</p>
    </div>
  );
}

const TITLES: Record<string, string> = {
  "/": "Intent Dashboard",
  "/approvals": "Approval Queue",
  "/audit": "Audit Trail",
  "/topology": "Network Topology",
  "/governance": "Risk & Governance",
  "/design-system": "Design System",
};

function Shell({ path, children }: { path: string; children: React.ReactNode }) {
  return <AppShell pageTitle={TITLES[path] ?? "ANIF Platform"}>{children}</AppShell>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Shell path="/"><PlaceholderPage title="F2 Intent Dashboard" /></Shell>} />
      <Route path="/approvals" element={<Shell path="/approvals"><PlaceholderPage title="F3 Approval Queue" /></Shell>} />
      <Route path="/audit" element={<Shell path="/audit"><PlaceholderPage title="F4 Audit Trail" /></Shell>} />
      <Route path="/topology" element={<Shell path="/topology"><PlaceholderPage title="F5 Topology View" /></Shell>} />
      <Route path="/governance" element={<Shell path="/governance"><PlaceholderPage title="F6 Risk & Governance" /></Shell>} />
      <Route path="/design-system" element={<Shell path="/design-system"><DesignSystemPage /></Shell>} />
    </Routes>
  );
}
