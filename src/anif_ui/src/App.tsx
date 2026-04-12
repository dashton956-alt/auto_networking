import { Routes, Route } from "react-router-dom";

function PlaceholderPage({ title }: { title: string }) {
  return (
    <main className="p-8">
      <h1 className="text-2xl font-bold text-brand-900">{title}</h1>
      <p className="mt-2 text-gray-600">Implementation pending</p>
    </main>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<PlaceholderPage title="F2 Intent Dashboard" />} />
      <Route path="/approvals" element={<PlaceholderPage title="F3 Approval Queue" />} />
      <Route path="/audit" element={<PlaceholderPage title="F4 Audit Trail" />} />
      <Route path="/topology" element={<PlaceholderPage title="F5 Topology View" />} />
      <Route path="/governance" element={<PlaceholderPage title="F6 Risk & Governance" />} />
    </Routes>
  );
}
