import { NavLink } from "react-router-dom";

interface NavItem {
  to: string;
  label: string;
  icon: string;
}

const NAV_ITEMS: NavItem[] = [
  { to: "/", icon: "⊞", label: "Intent Dashboard" },
  { to: "/approvals", icon: "✓", label: "Approval Queue" },
  { to: "/audit", icon: "📋", label: "Audit Trail" },
  { to: "/topology", icon: "◈", label: "Topology" },
  { to: "/governance", icon: "⚖", label: "Governance" },
];

export function Sidebar() {
  return (
    <nav
      aria-label="Main navigation"
      className="w-56 shrink-0 bg-chrome-900 flex flex-col h-full"
    >
      {/* Logo */}
      <div className="px-4 py-5 border-b border-chrome-800">
        <span className="text-white font-bold text-sm tracking-wide">ANIF Platform</span>
      </div>

      {/* Nav links */}
      <ul className="flex-1 py-3 space-y-0.5 px-2" role="list">
        {NAV_ITEMS.map((item) => (
          <li key={item.to}>
            <NavLink
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                [
                  "flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors",
                  isActive
                    ? "bg-brand-600 text-white font-medium"
                    : "text-chrome-200 hover:bg-chrome-800 hover:text-white",
                ].join(" ")
              }
            >
              <span aria-hidden="true" className="text-base w-5 text-center">
                {item.icon}
              </span>
              {item.label}
            </NavLink>
          </li>
        ))}
      </ul>

      {/* Bottom: design system link (dev only) */}
      <div className="px-2 pb-3 border-t border-chrome-800 pt-3">
        <NavLink
          to="/design-system"
          className={({ isActive }) =>
            [
              "flex items-center gap-2.5 px-3 py-2 rounded-md text-xs transition-colors",
              isActive
                ? "bg-chrome-700 text-white"
                : "text-chrome-300 hover:bg-chrome-800 hover:text-white",
            ].join(" ")
          }
        >
          <span aria-hidden="true" className="w-5 text-center">🎨</span>
          Design System
        </NavLink>
      </div>
    </nav>
  );
}
