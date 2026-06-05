/* Matcha Scout — screens part B: Browse, Quiz, Results, Detail, ReviewForm
   (useState/useEffect/useRef are declared once globally in primitives.jsx) */

/* ---------------- Browse ---------------- */
const BROWSE_FILTERS = [
  { id: 'all', label: 'All drinks', test: () => true },
  { id: 'iced', label: 'Iced', test: (d) => d.iced },
  { id: 'hot', label: 'Hot', test: (d) => d.hot },
  { id: 'oat', label: 'Oat milk', test: (d) => d.milk.includes('oat') },
  { id: 'dairyfree', label: 'Dairy-free', test: (d) => d.milk.every((m) => m !== 'whole') },
  { id: 'strong', label: 'Strong', test: (d) => d.taste.strength >= 4 },
  { id: 'sweet', label: 'Sweet', test: (d) => d.taste.sweet >= 4 },
];

function Browse({ go }) {
  const [q, setQ] = useState('');
  const [filter, setFilter] = useState('all');
  const [sort, setSort] = useState('curated');

  let list = DRINKS.filter((d) => {
    const f = BROWSE_FILTERS.find((x) => x.id === filter);
    if (f && !f.test(d)) return false;
    if (q.trim()) {
      const s = (d.name + ' ' + cafeName(d.cafe) + ' ' + d.blurb).toLowerCase();
      if (!s.includes(q.trim().toLowerCase())) return false;
    }
    return true;
  });
  if (sort === 'priceLow') list = list.slice().sort((a, b) => a.price - b.price);
  if (sort === 'priceHigh') list = list.slice().sort((a, b) => b.price - a.price);
  if (sort === 'strength') list = list.slice().sort((a, b) => b.taste.strength - a.taste.strength);

  return (
    <div className="page screen-enter">
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'flex-end', justifyContent: 'space-between', gap: 14, marginBottom: 18 }}>
        <div>
          <span className="eyebrow">The menu</span>
          <h1 className="page-title display" style={{ marginTop: 6 }}>Browse drinks</h1>
          <p className="page-sub">{DRINKS.length} matcha drinks from {Object.keys(CAFES).length} neighborhood cafes</p>
        </div>
        <Segmented options={[{ value: 'curated', label: 'Curated' }, { value: 'priceLow', label: 'Price ↑' }, { value: 'strength', label: 'Strongest' }]} value={sort} onChange={setSort} />
      </div>

      {/* search */}
      <div style={{ position: 'relative', marginBottom: 12 }}>
        <span style={{ position: 'absolute', left: 15, top: '50%', transform: 'translateY(-50%)', color: 'var(--ink-4)' }}><Icon name="search" size={18} /></span>
        <input className="field" style={{ paddingLeft: 42 }} placeholder="Search a drink, cafe, or flavor…" value={q} onChange={(e) => setQ(e.target.value)} />
      </div>

      {/* filter chips */}
      <div className="ms-scroll" style={{ display: 'flex', gap: 8, overflowX: 'auto', paddingBottom: 14, marginBottom: 6 }}>
        {BROWSE_FILTERS.map((f) => (
          <button key={f.id} onClick={() => setFilter(f.id)} style={{
            border: 'none', whiteSpace: 'nowrap', cursor: 'pointer',
            background: filter === f.id ? 'var(--matcha-600)' : 'var(--card)',
            color: filter === f.id ? '#fff' : 'var(--ink-2)',
            boxShadow: filter === f.id ? 'var(--shadow-sm)' : 'inset 0 0 0 1px var(--line-2)',
            fontWeight: 600, fontSize: 13, padding: '9px 15px', borderRadius: 999, transition: 'all .15s ease',
          }}>{f.label}</button>
        ))}
      </div>

      {list.length === 0 ? (
        <EmptyState icon="search" title="Nothing matches that yet"
          body="Try a different search or clear your filters to see the full menu."
          action={<button className="btn btn-ghost btn-sm" onClick={() => { setQ(''); setFilter('all'); }}>Clear filters</button>} />
      ) : (
        <div className="drink-grid">
          {list.map((d) => <DrinkCardItem key={d.id} drink={d} go={go} />)}
        </div>
      )}
    </div>
  );
}

/* ---------------- Quiz (guided, one at a time) ---------------- */
const QUIZ_STEPS = [
  { key: 'strength', q: 'How strong should the matcha be?', help: 'The backbone of the drink — faint green or full ceremonial punch.', lo: 'Mild', hi: 'Intense' },
  { key: 'sweet', q: 'How sweet do you like it?', help: 'From bone-dry and grown-up to full dessert territory.', lo: 'Not sweet', hi: 'Dessert' },
  { key: 'creamy', q: 'How creamy should it feel?', help: 'Light and clean on the palate, or rich and velvety.', lo: 'Light', hi: 'Velvety' },
  { key: 'earthy', q: 'How grassy and earthy?', help: 'That fresh-cut, vegetal “green” character matcha is known for.', lo: 'Clean', hi: 'Garden' },
  { key: 'bitter', q: 'How much bitter edge?', help: 'A little astringency can add depth — or you can skip it entirely.', lo: 'Mellow', hi: 'Bold' },
];
const MILKS = ['any', 'oat', 'whole', 'almond', 'coconut', 'none'];

function Quiz({ go, initial }) {
  const [step, setStep] = useState(0);
  const [prefs, setPrefs] = useState(initial || { strength: 3, sweet: 3, creamy: 3, earthy: 3, bitter: 3 });
  const [priceMax, setPriceMax] = useState('');
  const [milk, setMilk] = useState('any');
  const total = QUIZ_STEPS.length + 1;
  const isFilter = step === QUIZ_STEPS.length;

  function choose(key, val) {
    setPrefs((p) => ({ ...p, [key]: val }));
    setTimeout(() => setStep((s) => Math.min(s + 1, QUIZ_STEPS.length)), 240);
  }
  function finish() {
    const out = { ...prefs };
    if (priceMax && parseFloat(priceMax) > 0) out.priceMax = parseFloat(priceMax);
    if (milk !== 'any') out.milk = milk;
    go('results', { prefs: out });
  }

  const cur = QUIZ_STEPS[step];
  return (
    <div className="page screen-enter">
      <div className="quiz-shell">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
          <span className="eyebrow">Your tasting profile</span>
          <span className="mono" style={{ fontSize: 12, color: 'var(--ink-3)' }}>{String(Math.min(step + 1, total)).padStart(2, '0')} / {String(total).padStart(2, '0')}</span>
        </div>
        <div className="quiz-progress">
          {Array.from({ length: total }).map((_, i) => (
            <div className="qp-seg" key={i}><div className="qp-fill" style={{ width: i < step ? '100%' : i === step ? '50%' : '0%' }} /></div>
          ))}
        </div>

        <div className="quiz-card" key={step} style={{ marginTop: 18, animation: 'ms-fade-up .35s ease both' }}>
          {!isFilter ? (
            <React.Fragment>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                <span style={{ width: 30, height: 30, borderRadius: 999, background: 'var(--matcha-tint)', color: 'var(--matcha-700)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Icon name="drop" size={16} /></span>
                <span className="mono" style={{ fontSize: 12, color: 'var(--ink-3)', textTransform: 'uppercase', letterSpacing: '0.12em' }}>{cur.key}</span>
              </div>
              <h2 className="display" style={{ fontSize: 26, lineHeight: 1.1 }}>{cur.q}</h2>
              <p className="lead" style={{ fontSize: 14, marginTop: 8 }}>{cur.help}</p>
              <div className="scale-row">
                {[1, 2, 3, 4, 5].map((n) => (
                  <button key={n} className={'scale-btn' + (prefs[cur.key] === n ? ' sel' : '')} onClick={() => choose(cur.key, n)}>{n}</button>
                ))}
              </div>
              <div className="scale-ends"><span>{cur.lo}</span><span>{cur.hi}</span></div>
            </React.Fragment>
          ) : (
            <React.Fragment>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                <span style={{ width: 30, height: 30, borderRadius: 999, background: 'var(--hojicha-tint)', color: 'var(--hojicha-2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Icon name="filter" size={16} /></span>
                <span className="mono" style={{ fontSize: 12, color: 'var(--ink-3)', textTransform: 'uppercase', letterSpacing: '0.12em' }}>Optional</span>
              </div>
              <h2 className="display" style={{ fontSize: 26, lineHeight: 1.1 }}>A couple of practicals</h2>
              <p className="lead" style={{ fontSize: 14, marginTop: 8 }}>Skip these if you’d rather see everything.</p>
              <div style={{ marginTop: 20 }}>
                <label className="taste-label" style={{ display: 'block', marginBottom: 8 }}>Max price</label>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  {['', '6', '7', '8'].map((v) => (
                    <button key={v || 'any'} onClick={() => setPriceMax(v)} style={{
                      border: 'none', cursor: 'pointer', fontFamily: 'var(--ff-mono)', fontSize: 14, fontWeight: 500,
                      padding: '11px 16px', borderRadius: 999,
                      background: priceMax === v ? 'var(--matcha-600)' : 'var(--card-2)', color: priceMax === v ? '#fff' : 'var(--ink-2)',
                      boxShadow: priceMax === v ? 'var(--shadow-sm)' : 'inset 0 0 0 1px var(--line-2)',
                    }}>{v ? '≤ $' + v : 'Any'}</button>
                  ))}
                </div>
              </div>
              <div style={{ marginTop: 20 }}>
                <label className="taste-label" style={{ display: 'block', marginBottom: 8 }}>Milk preference</label>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  {MILKS.map((m) => (
                    <button key={m} onClick={() => setMilk(m)} style={{
                      border: 'none', cursor: 'pointer', fontSize: 13.5, fontWeight: 600, textTransform: 'capitalize',
                      padding: '11px 16px', borderRadius: 999,
                      background: milk === m ? 'var(--matcha-600)' : 'var(--card-2)', color: milk === m ? '#fff' : 'var(--ink-2)',
                      boxShadow: milk === m ? 'var(--shadow-sm)' : 'inset 0 0 0 1px var(--line-2)',
                    }}>{m === 'any' ? 'Any milk' : m === 'none' ? 'No milk' : m}</button>
                  ))}
                </div>
              </div>
              <button className="btn btn-primary btn-lg btn-block" style={{ marginTop: 26 }} onClick={finish}>
                <Icon name="spark" size={16} color="#fcfdf8" /> See my matches
              </button>
            </React.Fragment>
          )}
        </div>

        {/* footer nav */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 16 }}>
          <button className="btn btn-quiet btn-sm" disabled={step === 0} style={{ opacity: step === 0 ? 0.4 : 1 }}
            onClick={() => setStep((s) => Math.max(0, s - 1))}>
            <Icon name="back" size={15} /> Back
          </button>
          {!isFilter && (
            <button className="btn btn-quiet btn-sm" onClick={() => setStep((s) => Math.min(s + 1, QUIZ_STEPS.length))}>
              {prefs[cur.key] ? 'Next' : 'Skip'} <Icon name="arrow" size={15} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

/* ---------------- Results ---------------- */
function Results({ go, prefs }) {
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    setLoading(true);
    const t = setTimeout(() => setLoading(false), 850);
    return () => clearTimeout(t);
  }, [prefs]);

  const recs = MS_ENGINE.recommend(prefs, DRINKS);

  return (
    <div className="page screen-enter">
      <div style={{ marginBottom: 18 }}>
        <span className="eyebrow">Your matches</span>
        <h1 className="page-title display" style={{ marginTop: 6 }}>Poured just for your taste</h1>
        <p className="page-sub">Ranked by how closely each drink fits the profile you set — with the reasons in plain sight.</p>
      </div>

      <div className="results-layout">
        {/* summary */}
        <aside className="rec-summary">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <span className="eyebrow">Your profile</span>
            <button className="btn btn-quiet btn-sm" style={{ padding: '4px 8px' }} onClick={() => go('quiz', { initial: prefs })}>Edit</button>
          </div>
          <TasteBars taste={prefs} />
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 14 }}>
            {prefs.priceMax && <Pill kind="warm" mono>≤ ${prefs.priceMax.toFixed(0)}</Pill>}
            {prefs.milk && <Pill kind="bare">{prefs.milk} milk</Pill>}
            {!prefs.priceMax && !prefs.milk && <span style={{ fontSize: 12.5, color: 'var(--ink-3)' }}>No filters applied</span>}
          </div>
          <hr className="hairline" style={{ margin: '16px 0' }} />
          <p style={{ fontSize: 12.5, color: 'var(--ink-3)', lineHeight: 1.5, margin: 0 }}>
            The <span style={{ display: 'inline-block', width: 8, height: 8, background: 'var(--hojicha)', borderRadius: 2, verticalAlign: 'middle' }} /> marker on each bar shows your target.
          </p>
        </aside>

        {/* list */}
        <div>
          {loading ? (
            <div className="card-quiet" style={{ padding: 8 }}><LoadingState /></div>
          ) : recs.length === 0 ? (
            <div className="card-quiet" style={{ padding: 8 }}>
              <EmptyState icon="drop" title="No drinks fit those filters"
                body="Your price or milk filter ruled everything out. Loosen them and we’ll find your closest pours."
                action={<button className="btn btn-primary btn-sm" onClick={() => go('quiz', { initial: prefs })}>Adjust preferences</button>} />
            </div>
          ) : (
            <div className="rec-list">
              {recs.map((r, i) => <RecCard key={r.drink.id} r={r} rank={i + 1} prefs={prefs} go={go} />)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function RecCard({ r, rank, prefs, go }) {
  const d = r.drink;
  return (
    <div className={'rec-card anim-up' + (rank === 1 ? ' rank-1' : '')} style={{ animationDelay: (rank * 0.05) + 's' }}>
      <div style={{ display: 'flex', gap: 14, alignItems: 'center', marginBottom: 14 }}>
        <DrinkImage drink={d} height={72} radius={14} label={false} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <span className="mono" style={{ fontSize: 11, color: 'var(--ink-4)' }}>#{rank}</span>
            {rank === 1 && <Pill mono icon={<Icon name="star" size={11} />}>Top match</Pill>}
          </div>
          <div style={{ fontFamily: 'var(--ff-display)', fontWeight: 500, fontSize: 19, lineHeight: 1.05 }}>{d.name}</div>
          <div style={{ fontSize: 12.5, color: 'var(--ink-3)', marginTop: 3 }}>{cafeName(d.cafe)} · {CAFES[d.cafe].area}</div>
          <div className="mono" style={{ fontSize: 13, color: 'var(--matcha-700)', marginTop: 5 }}>${d.price.toFixed(2)}</div>
        </div>
        <MatchRing pct={r.pct} size={58} />
      </div>
      <div className="reasons" style={{ marginBottom: 14 }}>
        {r.reasons.map((reason, i) => (
          <div className="reason" key={i}><span className="rc"><Icon name="check" size={12} /></span>{reason}</div>
        ))}
      </div>
      <div style={{ borderTop: '1px solid var(--line)', paddingTop: 14, marginBottom: 14 }}>
        <TasteBars taste={d.taste} compareTo={prefs} />
      </div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10 }}>
        <DrinkTags drink={d} max={3} />
        <button className="btn btn-ghost btn-sm" onClick={() => go('drink', { drinkId: d.id })} style={{ flexShrink: 0 }}>Details <Icon name="arrow" size={14} /></button>
      </div>
    </div>
  );
}

Object.assign(window, { Browse, Quiz, Results, RecCard, QUIZ_STEPS });
