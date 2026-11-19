"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navigation = [
  { href: "/", label: "Command center", icon: "overview" },
  { href: "/monitor/aberdare", label: "Landscape explorer", icon: "monitor" },
  { href: "/operations", label: "Investigation desk", icon: "cases" },
  { href: "/outcomes", label: "Outcome graph", icon: "outcomes" },
  { href: "/legal", label: "Legal context", icon: "legal" },
  { href: "/sources", label: "Data sources", icon: "sources" },
];

function NavigationIcon({ name }: { name: string }) {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    {name === "overview" && <><rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" /><rect x="3" y="14" width="7" height="7" rx="1" /><rect x="14" y="14" width="7" height="7" rx="1" /></>}
    {name === "monitor" && <><path d="m3 5 6-2 6 2 6-2v16l-6 2-6-2-6 2V5Z" /><path d="M9 3v16m6-14v16" /><circle cx="15" cy="10" r="2.5" /></>}
    {name === "cases" && <><path d="M3 7h7l2 2h9v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z" /><path d="M3 7V5a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v2" /></>}
    {name === "outcomes" && <><circle cx="5" cy="12" r="2" /><circle cx="19" cy="5" r="2" /><circle cx="19" cy="19" r="2" /><path d="M7 12h4l6-7m-6 7 6 7" /></>}
    {name === "legal" && <><path d="M12 3v17m-5 1h10M4 7h16M7 7l-4 7h8L7 7Zm10 0-4 7h8l-4-7Z" /></>}
    {name === "sources" && <><ellipse cx="12" cy="5" rx="8" ry="3" /><path d="M4 5v7c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12v7c0 1.7 3.6 3 8 3s8-1.3 8-3v-7" /></>}
  </svg>;
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const currentPage = navigation.find((item) => item.href === "/" ? pathname === "/" : pathname.startsWith(item.href));
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">Skip to content</a>
      <aside className="sidebar" aria-label="Primary navigation">
        <Link href="/" className="brand" aria-label="ForestProof command center">
          <span className="brand-mark" aria-hidden="true"><svg viewBox="0 0 36 36" fill="none"><path d="M18 5 8 18h6L6 29h24l-8-11h6L18 5Z" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" /><path d="M18 22v10" stroke="currentColor" strokeWidth="1.7" /></svg></span>
          <span className="brand-wordmark">FORESTPROOF<span className="brand-sub">LIVING ATLAS</span></span>
        </Link>
        <nav className="nav">
          <p className="nav-label">Research workspace</p>
          {navigation.map((item) => {
            const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            return (
              <Link className={`nav-item ${active ? "active" : ""}`} href={item.href} key={item.href} aria-current={active ? "page" : undefined}>
                <span className="nav-icon"><NavigationIcon name={item.icon} /></span>
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="sidebar-bottom">
          <span className="environment-indicator" aria-hidden="true" />
          <strong>DEMO ENVIRONMENT</strong>
          Synthetic, clearly labelled records only. Human review remains required for every substantive finding.
        </div>
        <div className="sidebar-signature">Observe. Review. Respond.</div>
      </aside>
      <main id="main-content" tabIndex={-1}>
        <div className="workspace-bar"><span>Kenya <span aria-hidden="true">/</span> {currentPage?.label ?? "Evidence laboratory"}</span><a href="https://vmi3711898.contaboserver.net/welcome">Public observatory <span aria-hidden="true">↗</span></a></div>
        {children}
      </main>
    </div>
  );
}
