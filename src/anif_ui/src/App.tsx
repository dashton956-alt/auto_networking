import { Route, Routes } from "react-router-dom";
import { AppShell } from "@/layouts/AppShell";
import ApprovalQueuePage from "@/pages/ApprovalQueuePage";
import AuditTrailPage from "@/pages/AuditTrailPage";
import DesignSystemPage from "@/pages/DesignSystemPage";
import IntentDetailPage from "@/pages/IntentDetailPage";
import IntentListPage from "@/pages/IntentListPage";
import IntentSubmitPage from "@/pages/IntentSubmitPage";
import IntentTimelinePage from "@/pages/IntentTimelinePage";
import TicketReviewPage from "@/pages/TicketReviewPage";
import TopologyPage from "@/pages/TopologyPage";

function PlaceholderPage({ title }: { title: string }) {
  return (
    <div>
      <h1 className="text-2xl font-bold text-chrome-900">{title}</h1>
      <p className="mt-2 text-sm text-chrome-600">Implementation pending — coming in F6.</p>
    </div>
  );
}

function Shell({ title, children }: { title: string; children: React.ReactNode }) {
  return <AppShell pageTitle={title}>{children}</AppShell>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Shell title="Intent Dashboard"><IntentListPage /></Shell>} />
      <Route
        path="/intents/new"
        element={<Shell title="New Intent"><IntentSubmitPage /></Shell>}
      />
      <Route
        path="/intents/:intentId"
        element={<Shell title="Intent Detail"><IntentDetailPage /></Shell>}
      />
      <Route
        path="/approvals"
        element={<Shell title="Approval Queue"><ApprovalQueuePage /></Shell>}
      />
      <Route
        path="/approvals/:ticketId"
        element={<Shell title="Ticket Review"><TicketReviewPage /></Shell>}
      />
      <Route
        path="/audit"
        element={<Shell title="Audit Trail"><AuditTrailPage /></Shell>}
      />
      <Route
        path="/audit/:intentId"
        element={<Shell title="Intent Timeline"><IntentTimelinePage /></Shell>}
      />
      <Route
        path="/topology"
        element={<Shell title="Network Topology"><TopologyPage /></Shell>}
      />
      <Route
        path="/governance"
        element={
          <Shell title="Risk & Governance"><PlaceholderPage title="F6 Risk & Governance" /></Shell>
        }
      />
      <Route
        path="/design-system"
        element={<Shell title="Design System"><DesignSystemPage /></Shell>}
      />
    </Routes>
  );
}
