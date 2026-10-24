"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navigation = [
  { href: "/", label: "Command center", icon: "◈" },
  { href: "/monitor/aberdare", label: "Aberdare monitor", icon: "⌖" },
  { href: "/operations", label: "Case operations", icon: "▣" },
  { href: "/outcomes", label: "Outcome graph", icon: "↗" },
  { href: "/legal", label: "Legal context", icon: "§" },
  { href: "/sources", label: "Data sources", icon: "◌" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Primary navigation">
        <Link href="/" className="brand" aria-label="ForestProof command center">
          <span className="brand-mark" aria-hidden="true">⌁</span>
          <span>
            FORESTPROOF
            <span className="brand-sub">EVIDENCE TO ACTION</span>
          </span>
        </Link>
        <nav className="nav">
          <p className="nav-label">Operations</p>
          {navigation.map((item) => {
            const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            return (
              <Link className={`nav-item ${active ? "active" : ""}`} href={item.href} key={item.href}>
                <span className="nav-icon" aria-hidden="true">{item.icon}</span>
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="sidebar-bottom">
          <strong>DEMO ENVIRONMENT</strong>
          Synthetic, clearly labelled records only. Human review remains required for every substantive finding.
        </div>
      </aside>
      <main>{children}</main>
    </div>
  );
}
