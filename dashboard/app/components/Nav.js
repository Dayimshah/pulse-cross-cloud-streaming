"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Nav() {
  const path = usePathname();
  return (
    <nav className="nav">
      <Link href="/" className="nav-brand">
        <span className="nav-logo">P</span>
        <span>
          Pulse <span className="mono" style={{ color: "var(--text-faint)", fontSize: 12 }}>/ cross-cloud streaming</span>
        </span>
      </Link>
      <div className="nav-links">
        <Link href="/" className={`nav-link ${path === "/" ? "active" : ""}`}>
          home
        </Link>
        <Link href="/dashboard" className={`nav-link ${path === "/dashboard" ? "active" : ""}`}>
          dashboard
        </Link>
        <Link
          href="/architecture"
          className={`nav-link ${path === "/architecture" ? "active" : ""}`}
        >
          architecture
        </Link>
      </div>
    </nav>
  );
}
