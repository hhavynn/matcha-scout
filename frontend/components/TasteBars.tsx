const DIMENSIONS = [
  { key: "matcha_strength", label: "Matcha Strength", color: "bg-green-600" },
  { key: "sweetness",       label: "Sweetness",       color: "bg-yellow-400" },
  { key: "creaminess",      label: "Creaminess",      color: "bg-orange-300" },
  { key: "earthiness",      label: "Earthiness",      color: "bg-lime-600"   },
  { key: "bitterness",      label: "Bitterness",      color: "bg-emerald-800"},
] as const;

type ProfileLike = {
  matcha_strength: number;
  sweetness: number;
  creaminess: number;
  earthiness: number;
  bitterness: number;
};

export default function TasteBars({ profile }: { profile: ProfileLike }) {
  return (
    <div className="space-y-2">
      {DIMENSIONS.map(({ key, label, color }) => {
        const value = profile[key];
        const pct = ((value - 1) / 4) * 100;
        return (
          <div key={key} className="flex items-center gap-3">
            <span className="text-xs text-gray-500 w-28 shrink-0 text-right">{label}</span>
            <div className="flex-1 bg-gray-100 rounded-full h-2.5 overflow-hidden">
              <div
                className={`${color} h-full rounded-full transition-all`}
                style={{ width: `${pct}%` }}
              />
            </div>
            <span className="text-xs text-gray-500 w-4 shrink-0">{value}</span>
          </div>
        );
      })}
    </div>
  );
}
