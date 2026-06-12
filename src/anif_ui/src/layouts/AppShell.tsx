import type { ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";

interface AppShellProps {
  pageTitle: string;
  headerActions?: ReactNode;
  children: ReactNode;
}

export function AppShell({ pageTitle, headerActions, children }: AppShellProps) {
  return (
    <div className="flex h-screen bg-chrome-100 overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <TopBar title={pageTitle} actions={headerActions} />
        <main
          id="main-content"
          tabIndex={-1}
          className="flex-1 overflow-y-auto p-6 focus:outline-none"
        >
          {children}
        </main>
      </div>
    </div>
  );
}
