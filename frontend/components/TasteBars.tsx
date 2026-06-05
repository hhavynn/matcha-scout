const DIMENSIONS = [
  { key: "matcha_strength", label: "Strength" },
  { key: "sweetness",       label: "Sweetness" },
  { key: "creaminess",      label: "Creaminess" },
  { key: "earthiness",      label: "Earthiness" },
  { key: "bitterness",      label: "Bitterness" },
] as const;

type ProfileLike = {
  matcha_strength: number;
  sweetness: number;
  creaminess: number;
  earthiness: number;
  bitterness: number;
};

interface Props {
  profile: ProfileLike;
  /** When provided, shows a hojicha vertical marker at the user's preference value */
  compareTo?: ProfileLike;
  animate?: boolean;
}

export default function TasteBars({ profile, compareTo, animate = false }: Props) {
  return (
    <div className="flex flex-col" style={{ gap: 10 }}>
      {DIMENSIONS.map(({ key, label }, i) => {
        const value = profile[key];
        const pct = ((value - 1) / 4) * 100;
        const comparePct = compareTo ? ((compareTo[key] - 1) / 4) * 100 : null;

        return (
          <div key={key} className="ms-taste-row">
            <span className="ms-taste-label">{label}</span>
            <div className="ms-taste-track" style={{ overflow: "visible" }}>
              <div
                className="ms-taste-fill"
                style={{
                  width: `${pct}%`,
                  transition: animate ? `width .7s cubic-bezier(.2,.8,.2,1) ${i * 70}ms` : "none",
                }}
              />
              {/* Hojicha "your target" marker */}
              {comparePct !== null && (
                <div
                  title="your preference"
                  style={{
                    position: "absolute",
                    top: -3, bottom: -3,
                    left: `calc(${comparePct}% - 1px)`,
                    width: 2,
                    background: "#a9774e",
                    borderRadius: 2,
                    opacity: 0.85,
                    zIndex: 3,
                  }}
                />
              )}
            </div>
            <span className="ms-taste-val">{value}</span>
          </div>
        );
      })}
    </div>
  );
}
