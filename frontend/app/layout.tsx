import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://matcha-scout.vercel.app"),
  title: {
    default: "Matcha Scout",
    template: "%s | Matcha Scout",
  },
  description:
    "Find matcha drinks ranked by your taste preferences with AI-parsed reviews and transparent scoring.",
  openGraph: {
    title: "Matcha Scout",
    description:
      "AI-powered matcha discovery with taste profiles, explainable recommendations, and community reviews.",
    url: "https://matcha-scout.vercel.app",
    siteName: "Matcha Scout",
    type: "website",
  },
};

/* ── Geometric matcha-bowl mark ───────────────────────────────────────── */
function MatchaMark({ size = 28 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      aria-hidden="true"
      style={{ display: "block", flexShrink: 0 }}
    >
      <circle cx="16" cy="16" r="14.2" stroke="#5f7850" strokeWidth="1.6" opacity="0.45" />
      <circle cx="16" cy="16" r="9.4" fill="#5f7850" />
      <circle cx="12.4" cy="12.6" r="3.1" fill="#fffdf8" opacity="0.42" />
    </svg>
  );
}

/* ── Icons ────────────────────────────────────────────────────────────── */
function IconLeaf({ size = 20 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" style={{ display: "block" }}>
      <path d="M16 4C8 4 4 8 4 16c8 0 12-4 12-12zM7 13c3-1 5-3 6-6" />
    </svg>
  );
}
function IconGrid({ size = 20 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" style={{ display: "block" }}>
      <rect x="3.5" y="3.5" width="5.5" height="5.5" rx="1.4" />
      <rect x="11" y="3.5" width="5.5" height="5.5" rx="1.4" />
      <rect x="3.5" y="11" width="5.5" height="5.5" rx="1.4" />
      <rect x="11" y="11" width="5.5" height="5.5" rx="1.4" />
    </svg>
  );
}
function IconSpark({ size = 16, color = "currentColor" }: { size?: number; color?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 20 20" fill="none" stroke={color} strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" style={{ display: "block", flexShrink: 0 }}>
      <path d="M10 3c.7 3.2 1.8 4.3 5 5-3.2.7-4.3 1.8-5 5-.7-3.2-1.8-4.3-5-5 3.2-.7 4.3-1.8 5-5z" />
    </svg>
  );
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full flex flex-col" style={{ background: "#f6f1e7" }}>
        {/* ── Desktop header ───────────────────────────────────────────── */}
        <header
          className="sticky top-0 z-30 border-b"
          style={{
            background: "color-mix(in srgb, #f6f1e7 82%, transparent)",
            backdropFilter: "blur(14px) saturate(1.1)",
            borderColor: "#e8e1d0",
          }}
        >
          <div
            className="flex items-center justify-between gap-4 mx-auto px-5"
            style={{ maxWidth: 1140, padding: "13px 20px" }}
          >
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2.5 no-underline">
              <MatchaMark size={26} />
              <span
                className="ms-serif"
                style={{ fontSize: 19, color: "#2a3124", lineHeight: 1 }}
              >
                Matcha{" "}
                <span className="ms-serif-i" style={{ color: "#44563a" }}>
                  Scout
                </span>
              </span>
            </Link>

            {/* Desktop nav — hidden on mobile, shown on md+ */}
            <nav className="hidden md:flex items-center gap-1">
              <Link
                href="/"
                className="text-sm font-medium rounded-full px-3.5 py-2 transition-colors"
                style={{ color: "#585e4d" }}
              >
                Home
              </Link>
              <Link
                href="/drinks"
                className="text-sm font-medium rounded-full px-3.5 py-2 transition-colors"
                style={{ color: "#585e4d" }}
              >
                Browse
              </Link>
            </nav>

            {/* Desktop CTA */}
            <Link
              href="/quiz"
              className="hidden md:inline-flex ms-btn ms-btn-primary ms-btn-sm"
            >
              <IconSpark size={14} color="#fcfdf8" /> Find my matcha
            </Link>
          </div>
        </header>

        {/* ── Main content ─────────────────────────────────────────────── */}
        <main className="flex-1 pb-20 md:pb-0">{children}</main>

        {/* ── Mobile bottom tab bar ────────────────────────────────────── */}
        <nav
          className="md:hidden fixed bottom-0 left-0 right-0 z-30 flex justify-around items-stretch border-t"
          style={{
            background: "color-mix(in srgb, #f6f1e7 88%, transparent)",
            backdropFilter: "blur(14px)",
            borderColor: "#e8e1d0",
            paddingBottom: "max(8px, env(safe-area-inset-bottom, 16px))",
          }}
        >
          <Link
            href="/"
            className="flex-1 flex flex-col items-center gap-1 pt-2 pb-1"
            style={{ color: "#8c8a78", fontSize: 10.5, fontWeight: 600 }}
          >
            <span className="flex items-center justify-center h-6"><IconLeaf size={20} /></span>
            Home
          </Link>
          <Link
            href="/drinks"
            className="flex-1 flex flex-col items-center gap-1 pt-2 pb-1"
            style={{ color: "#8c8a78", fontSize: 10.5, fontWeight: 600 }}
          >
            <span className="flex items-center justify-center h-6"><IconGrid size={20} /></span>
            Browse
          </Link>
          <Link
            href="/quiz"
            className="flex-1 flex flex-col items-center gap-1 pt-2 pb-1"
            style={{ color: "#8c8a78", fontSize: 10.5, fontWeight: 600 }}
          >
            <span
              className="flex items-center justify-center"
              style={{
                width: 40, height: 40, borderRadius: 14,
                background: "#56703f", color: "#fff",
                marginTop: -10,
                boxShadow: "0 6px 14px -5px rgba(68,86,58,0.7)",
              }}
            >
              <IconSpark size={20} color="#fff" />
            </span>
            Match
          </Link>
        </nav>
      </body>
    </html>
  );
}
