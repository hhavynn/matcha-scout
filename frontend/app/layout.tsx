import type { Metadata } from "next";
import { Geist } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geist = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Matcha Scout",
  description:
    "Discover matcha drinks ranked by your taste preferences. AI-parsed community reviews, deterministic recommendations.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${geist.variable} h-full`}>
      <body className="min-h-full flex flex-col">
        <header className="bg-white border-b border-green-100 shadow-sm">
          <nav className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2 font-semibold text-green-800 text-lg">
              <span className="text-2xl">🍵</span>
              Matcha Scout
            </Link>
            <div className="flex items-center gap-6 text-sm font-medium">
              <Link href="/drinks" className="text-green-700 hover:text-green-900 transition-colors">
                Browse Drinks
              </Link>
              <Link
                href="/quiz"
                className="bg-green-600 text-white px-4 py-1.5 rounded-full hover:bg-green-700 transition-colors"
              >
                Find My Match
              </Link>
            </div>
          </nav>
        </header>

        <main className="flex-1">{children}</main>

        <footer className="border-t border-green-100 bg-white mt-12">
          <div className="max-w-5xl mx-auto px-4 py-6 text-sm text-green-700 text-center">
            Matcha Scout — sample data only, all cafes and drinks are fictional.
          </div>
        </footer>
      </body>
    </html>
  );
}
