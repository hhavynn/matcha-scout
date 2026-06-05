import Link from "next/link";

const FEATURES = [
  {
    icon: "🤖",
    title: "AI-Parsed Reviews",
    body: "Submit a free-text review. Gemini Flash reads it and extracts structured taste ratings — strength, sweetness, creaminess, earthiness, and bitterness.",
  },
  {
    icon: "🎯",
    title: "Deterministic Rankings",
    body: "No random AI guesses. A weighted similarity formula scores each drink against your preferences and returns a transparent match percentage.",
  },
  {
    icon: "🗺️",
    title: "Community-Powered",
    body: "Taste profiles grow with every review. The more users contribute, the more accurate the recommendations become.",
  },
];

export default function HomePage() {
  return (
    <div className="max-w-5xl mx-auto px-4">
      {/* Hero */}
      <section className="py-20 text-center">
        <div className="text-6xl mb-6">🍵</div>
        <h1 className="text-4xl md:text-5xl font-bold text-green-900 leading-tight mb-4">
          Find Your Perfect Matcha
        </h1>
        <p className="text-lg text-green-700 max-w-xl mx-auto mb-8">
          Tell us your taste preferences. We rank matcha drinks from real cafes
          using AI-parsed community reviews and transparent scoring.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/quiz"
            className="bg-green-600 text-white px-8 py-3 rounded-full font-semibold text-lg hover:bg-green-700 transition-colors"
          >
            Start the Quiz →
          </Link>
          <Link
            href="/drinks"
            className="bg-white text-green-700 border border-green-200 px-8 py-3 rounded-full font-semibold text-lg hover:bg-green-50 transition-colors"
          >
            Browse Drinks
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="py-12 border-t border-green-100">
        <h2 className="text-2xl font-bold text-green-900 text-center mb-10">How It Works</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {FEATURES.map((f) => (
            <div key={f.title} className="bg-white rounded-2xl border border-green-100 p-6 text-center shadow-sm">
              <div className="text-4xl mb-3">{f.icon}</div>
              <h3 className="font-semibold text-green-900 mb-2">{f.title}</h3>
              <p className="text-sm text-gray-600 leading-relaxed">{f.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Steps */}
      <section className="py-12 border-t border-green-100">
        <h2 className="text-2xl font-bold text-green-900 text-center mb-10">Three Steps to Your Match</h2>
        <ol className="max-w-lg mx-auto space-y-5">
          {[
            ["Rate your preferences", "Slide the dials for matcha strength, sweetness, creaminess, earthiness, and bitterness."],
            ["See your ranked matches", "We score every drink against your profile and show a transparent match percentage."],
            ["Explore and review", "Check community taste profiles and submit your own review to help others."],
          ].map(([title, desc], i) => (
            <li key={i} className="flex gap-4">
              <span className="flex-shrink-0 w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
                {i + 1}
              </span>
              <div>
                <p className="font-semibold text-green-900">{title}</p>
                <p className="text-sm text-gray-600 mt-0.5">{desc}</p>
              </div>
            </li>
          ))}
        </ol>
        <div className="text-center mt-10">
          <Link href="/quiz" className="bg-green-600 text-white px-8 py-3 rounded-full font-semibold hover:bg-green-700 transition-colors">
            Get Started
          </Link>
        </div>
      </section>
    </div>
  );
}
