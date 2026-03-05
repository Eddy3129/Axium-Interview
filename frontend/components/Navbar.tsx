"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="top-nav" aria-label="Main navigation">
      <div className="nav-inner">
        <Link href="/" className="brand">
          Smart Recipe Analyzer
        </Link>
        <div className="nav-links">
          <Link
            href="/"
            className={`nav-link ${pathname === "/" ? "active" : ""}`}
          >
            Chat
          </Link>
          <Link
            href="/recipes"
            className={`nav-link ${pathname.startsWith("/recipes") ? "active" : ""}`}
          >
            Recipes
          </Link>
        </div>
      </div>
    </nav>
  );
}
