/* Matcha Scout — variation components for the design canvas
   (hooks declared globally in primitives.jsx) */

/* =====================================================================
   TASTE PROFILE VISUALIZATIONS
   ===================================================================== */

/* A · horizontal bars (the chosen primary) — reuses <TasteBars> */
function VizBars({ taste }) {
  return <div style={{ width: 300 }}><TasteBars taste={taste} /></div>;
}

/* B · radar / pentagon */
function VizRadar({ taste, size = 220 }) {
  const n = TASTE_DIMS.length;
  const cx = size / 2, cy = size / 2, R = size * 0.34;
  const ang = (i) => -Math.PI / 2 + (i * 2 * Math.PI) / n;
  const pt = (i, r) => [cx + Math.cos(ang(i)) * r, cy + Math.sin(ang(i)) * r];
  const ring = (f) => TASTE_DIMS.map((_, i) => pt(i, R * f).join(',')).join(' ');
  const valPoly = TASTE_DIMS.map((d, i) => pt(i, R * (taste[d.key] / 5)).join(',')).join(' ');
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      {[0.25, 0.5, 0.75, 1].map((f) => (
        <polygon key={f} points={ring(f)} fill="none" stroke="var(--line-2)" strokeWidth="1" />
      ))}
      {TASTE_DIMS.map((d, i) => {
        const [x, y] = pt(i, R);
        return <line key={d.key} x1={cx} y1={cy} x2={x} y2={y} stroke="var(--line-2)" strokeWidth="1" />;
      })}
      <polygon points={valPoly} fill="rgba(95,120,80,0.18)" stroke="var(--matcha)" strokeWidth="2" strokeLinejoin="round" />
      {TASTE_DIMS.map((d, i) => {
        const [x, y] = pt(i, R * (taste[d.key] / 5));
        return <circle key={d.key} cx={x} cy={y} r="3.2" fill="var(--matcha-700)" />;
      })}
      {TASTE_DIMS.map((d, i) => {
        const short = ['Strength', 'Sweet', 'Creamy', 'Earthy', 'Bitter'][i];
        const [x, y] = pt(i, R + 15);
        return <text key={d.key} x={x} y={y} fontSize="9.5" fontFamily="var(--ff-mono)" fill="var(--ink-3)"
          textAnchor="middle" dominantBaseline="middle">{short}</text>;
      })}
    </svg>
  );
}

/* C · dot / lollipop scale */
function VizDots({ taste }) {
  return (
    <div className="flow" style={{ ['--gap']: '12px', width: 300 }}>
      {TASTE_DIMS.map((d) => (
        <div key={d.key} style={{ display: 'grid', gridTemplateColumns: '92px 1fr', alignItems: 'center', gap: 12 }}>
          <span className="taste-label">{d.label}</span>
          <div style={{ display: 'flex', gap: 7 }}>
            {[1, 2, 3, 4, 5].map((n) => (
              <span key={n} style={{
                width: 16, height: 16, borderRadius: 999,
                background: n <= taste[d.key] ? 'var(--matcha)' : 'var(--paper-2)',
                boxShadow: n <= taste[d.key] ? 'none' : 'inset 0 0 0 1px var(--line-2)',
                transform: n === taste[d.key] ? 'scale(1.15)' : 'none',
              }} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

/* =====================================================================
   RECOMMENDATION CARD LAYOUTS
   ===================================================================== */
const sampleRec = (() => {
  const d = window.MS_DATA.drinks.find((x) => x.id === 'd-classic');
  return { drink: d, pct: 92, reasons: ['Balanced strength that matches your profile', 'Available with oat milk', '$5.75 — under your $8 budget'] };
})();
const cn = (id) => window.MS_DATA.cafes[id].name;

/* A · detailed card (matches prototype) */
function RecDetailed({ r = sampleRec }) {
  const d = r.drink;
  return (
    <div className="rec-card rank-1" style={{ width: 360 }}>
      <div style={{ display: 'flex', gap: 14, alignItems: 'center', marginBottom: 14 }}>
        <DrinkImage drink={d} height={68} radius={14} label={false} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <Pill mono icon={<Icon name="star" size={11} />} style={{ marginBottom: 6 }}>Top match</Pill>
          <div className="serif" style={{ fontSize: 18 }}>{d.name}</div>
          <div style={{ fontSize: 12, color: 'var(--ink-3)', marginTop: 2 }}>{cn(d.cafe)}</div>
        </div>
        <MatchRing pct={r.pct} size={54} />
      </div>
      <div className="reasons" style={{ marginBottom: 14 }}>
        {r.reasons.map((x, i) => <div className="reason" key={i}><span className="rc"><Icon name="check" size={12} /></span>{x}</div>)}
      </div>
      <div style={{ borderTop: '1px solid var(--line)', paddingTop: 12 }}><TasteBars taste={d.taste} /></div>
    </div>
  );
}

/* B · compact list row */
function RecCompact({ r = sampleRec }) {
  const d = r.drink;
  return (
    <div className="rec-card" style={{ width: 360, display: 'flex', alignItems: 'center', gap: 14 }}>
      <MatchRing pct={r.pct} size={48} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div className="serif" style={{ fontSize: 17 }}>{d.name}</div>
        <div style={{ fontSize: 12, color: 'var(--ink-3)', marginTop: 2 }}>{cn(d.cafe)} · ${d.price.toFixed(2)}</div>
        <div style={{ display: 'flex', gap: 5, marginTop: 8 }}>
          {TASTE_DIMS.map((dim) => (
            <div key={dim.key} title={dim.label} style={{ flex: 1, height: 5, borderRadius: 999, background: 'var(--paper-2)', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: (d.taste[dim.key] / 5 * 100) + '%', background: 'var(--matcha)', borderRadius: 999 }} />
            </div>
          ))}
        </div>
      </div>
      <Icon name="arrow" size={16} color="var(--ink-4)" />
    </div>
  );
}

/* C · flavor-chip card */
function RecChips({ r = sampleRec }) {
  const d = r.drink;
  const top = [...TASTE_DIMS].sort((a, b) => d.taste[b.key] - d.taste[a.key]).slice(0, 3);
  return (
    <div className="rec-card" style={{ width: 360 }}>
      <DrinkImage drink={d} height={96} radius={14} label={false}>
        <span style={{ position: 'absolute', top: 10, right: 10 }}><Pill mono style={{ background: 'rgba(255,253,248,0.9)' }}>{r.pct}% match</Pill></span>
      </DrinkImage>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginTop: 12 }}>
        <div className="serif" style={{ fontSize: 18 }}>{d.name}</div>
        <span className="mono" style={{ fontSize: 13, color: 'var(--matcha-700)' }}>${d.price.toFixed(2)}</span>
      </div>
      <div style={{ fontSize: 12, color: 'var(--ink-3)', marginTop: 2, marginBottom: 12 }}>{cn(d.cafe)}</div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
        {top.map((dim) => <Pill key={dim.key}>{dim.label} {d.taste[dim.key]}/5</Pill>)}
        {d.milk.slice(0, 2).map((m) => <Pill key={m} kind="bare">{m}</Pill>)}
      </div>
    </div>
  );
}

/* =====================================================================
   QUIZ INTERACTION VARIANTS
   ===================================================================== */

/* A · guided one-at-a-time (matches prototype) */
function QuizGuided() {
  const [v, setV] = useState(4);
  return (
    <div className="quiz-card" style={{ width: 340 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
        <span style={{ width: 28, height: 28, borderRadius: 999, background: 'var(--matcha-tint)', color: 'var(--matcha-700)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Icon name="drop" size={15} /></span>
        <span className="mono" style={{ fontSize: 11, color: 'var(--ink-3)', textTransform: 'uppercase', letterSpacing: '0.12em' }}>strength</span>
      </div>
      <h2 className="display" style={{ fontSize: 22 }}>How strong should it be?</h2>
      <div className="scale-row">
        {[1, 2, 3, 4, 5].map((n) => <button key={n} className={'scale-btn' + (v === n ? ' sel' : '')} onClick={() => setV(n)}>{n}</button>)}
      </div>
      <div className="scale-ends"><span>Mild</span><span>Intense</span></div>
    </div>
  );
}

/* B · all sliders on one screen */
function QuizSliders() {
  const [p, setP] = useState({ strength: 4, sweet: 2, creamy: 4, earthy: 3, bitter: 2 });
  return (
    <div className="quiz-card" style={{ width: 340 }}>
      <h2 className="display" style={{ fontSize: 20, marginBottom: 4 }}>Your tasting profile</h2>
      <p className="lead" style={{ fontSize: 13, marginBottom: 8 }}>All five dials, one screen.</p>
      <div className="flow" style={{ ['--gap']: '14px' }}>
        {TASTE_DIMS.map((d) => (
          <div key={d.key}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 2 }}>
              <span className="taste-label">{d.label}</span>
              <span className="mono" style={{ fontSize: 12, color: 'var(--matcha-700)', background: 'var(--matcha-tint)', borderRadius: 999, padding: '1px 8px' }}>{p[d.key]}</span>
            </div>
            <input className="ms-range" type="range" min="1" max="5" value={p[d.key]} onChange={(e) => setP({ ...p, [d.key]: +e.target.value })} />
          </div>
        ))}
      </div>
    </div>
  );
}

/* C · emoji-free "tap a vibe" cards */
function QuizCards() {
  const opts = [
    { k: 'mild', t: 'Easy & smooth', d: 'Gentle, creamy, barely bitter' },
    { k: 'balanced', t: 'Balanced', d: 'A bit of everything' },
    { k: 'bold', t: 'Bold & grassy', d: 'Strong, earthy, ceremonial' },
  ];
  const [sel, setSel] = useState('bold');
  return (
    <div className="quiz-card" style={{ width: 340 }}>
      <span className="mono" style={{ fontSize: 11, color: 'var(--ink-3)', textTransform: 'uppercase', letterSpacing: '0.12em' }}>Quick start</span>
      <h2 className="display" style={{ fontSize: 21, margin: '6px 0 14px' }}>Pick your starting vibe</h2>
      <div className="flow" style={{ ['--gap']: '10px' }}>
        {opts.map((o) => (
          <button key={o.k} onClick={() => setSel(o.k)} style={{
            width: '100%', textAlign: 'left', border: 'none', cursor: 'pointer',
            background: sel === o.k ? 'var(--matcha-tint)' : 'var(--card-2)',
            boxShadow: sel === o.k ? 'inset 0 0 0 1.5px var(--matcha)' : 'inset 0 0 0 1px var(--line-2)',
            borderRadius: 'var(--r-sm)', padding: '13px 15px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10,
          }}>
            <span>
              <span style={{ display: 'block', fontWeight: 600, fontSize: 15, color: 'var(--ink)' }}>{o.t}</span>
              <span style={{ display: 'block', fontSize: 12.5, color: 'var(--ink-3)', marginTop: 2 }}>{o.d}</span>
            </span>
            <span style={{ width: 20, height: 20, borderRadius: 999, flexShrink: 0, background: sel === o.k ? 'var(--matcha-600)' : 'transparent', boxShadow: sel === o.k ? 'none' : 'inset 0 0 0 1.5px var(--line-2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {sel === o.k && <Icon name="check" size={12} color="#fff" />}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}

Object.assign(window, {
  VizBars, VizRadar, VizDots, RecDetailed, RecCompact, RecChips,
  QuizGuided, QuizSliders, QuizCards,
});
