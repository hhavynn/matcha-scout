/* Matcha Scout — screens part C: Drink detail + Review form
   (hooks declared once globally in primitives.jsx) */

function avgProfile(base, reviews) {
  // weight seed profile + parsed reviews into a fresh average
  const acc = { strength: base.strength, sweet: base.sweet, creamy: base.creamy, earthy: base.earthy, bitter: base.bitter };
  let n = 1;
  reviews.forEach((rv) => {
    acc.strength += rv.s; acc.sweet += rv.w; acc.creamy += rv.c; acc.earthy += rv.e; acc.bitter += rv.b; n++;
  });
  const round = (x) => Math.max(1, Math.min(5, Math.round((x / n) * 10) / 10));
  return { strength: round(acc.strength), sweet: round(acc.sweet), creamy: round(acc.creamy), earthy: round(acc.earthy), bitter: round(acc.bitter) };
}

function ReviewForm({ onSubmitted }) {
  const [text, setText] = useState('');
  const [state, setState] = useState('idle'); // idle | loading | error
  const [error, setError] = useState('');
  const min = 12;

  function submit(e) {
    e.preventDefault();
    if (text.trim().length < min) { setError(`A few more words, please — at least ${min} characters.`); return; }
    setError(''); setState('loading');
    setTimeout(() => {
      const parsed = MS_ENGINE.parseReview(text.trim());
      onSubmitted({
        id: 'u' + Date.now(), text: text.trim(),
        s: parsed.strength, w: parsed.sweet, c: parsed.creamy, e: parsed.earthy, b: parsed.bitter,
        conf: parsed.conf, tags: parsed.tags, when: new Date().toISOString().slice(0, 10), mine: true,
      });
      setText(''); setState('idle');
    }, 1100);
  }

  return (
    <form onSubmit={submit}>
      <div style={{ position: 'relative' }}>
        <textarea className="field" rows={4} value={text} disabled={state === 'loading'}
          onChange={(e) => setText(e.target.value)}
          placeholder="Describe what you tasted… “Bold and grassy with a creamy oat finish, barely sweet.” The AI turns your words into taste ratings." />
        <span className="mono" style={{ position: 'absolute', right: 12, bottom: 10, fontSize: 11, color: text.length < min ? 'var(--ink-4)' : 'var(--matcha)' }}>{text.length}</span>
      </div>
      {error && <p style={{ color: 'var(--danger)', fontSize: 12.5, margin: '8px 2px 0' }}>{error}</p>}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, marginTop: 12 }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: 7, fontSize: 12, color: 'var(--ink-3)' }}>
          <Icon name="leaf" size={14} color="var(--matcha)" /> Anonymous — no account needed
        </span>
        <button className="btn btn-primary btn-sm" type="submit" disabled={state === 'loading' || text.trim().length < min}
          style={{ opacity: text.trim().length < min ? 0.55 : 1 }}>
          {state === 'loading' ? (<><span style={{ width: 14, height: 14, borderRadius: 999, border: '2px solid rgba(255,255,255,0.5)', borderTopColor: '#fff', display: 'inline-block', animation: 'ms-spin .8s linear infinite' }} /> Reading…</>)
            : (<><Icon name="spark" size={14} color="#fcfdf8" /> Submit & parse</>)}
        </button>
      </div>
    </form>
  );
}

function ParsedResult({ review }) {
  const cells = [['Strength', review.s], ['Sweet', review.w], ['Creamy', review.c], ['Earthy', review.e], ['Bitter', review.b]];
  return (
    <div className="anim-up" style={{ background: 'linear-gradient(180deg, var(--matcha-tint), var(--card))', borderRadius: 'var(--r)', padding: 18, boxShadow: 'inset 0 0 0 1px var(--matcha-soft)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 9, marginBottom: 14 }}>
        <span style={{ width: 26, height: 26, borderRadius: 999, background: 'var(--matcha-600)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Icon name="check" size={15} color="#fff" /></span>
        <div>
          <div style={{ fontWeight: 600, fontSize: 14, color: 'var(--matcha-800)' }}>Review parsed & added</div>
          <div className="mono" style={{ fontSize: 11, color: 'var(--matcha-700)' }}>{Math.round(review.conf * 100)}% confidence</div>
        </div>
      </div>
      <div className="parsed-grid">
        {cells.map(([l, v]) => (
          <div className="parsed-cell" key={l}><div className="pv">{v}</div><div className="pl">{l}</div></div>
        ))}
      </div>
      {review.tags && review.tags.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 12 }}>
          {review.tags.map((t) => <Pill key={t}>{t}</Pill>)}
        </div>
      )}
    </div>
  );
}

function Detail({ go, drinkId }) {
  const drink = DRINKS.find((d) => d.id === drinkId) || DRINKS[0];
  const [reviews, setReviews] = useState(drink.reviews);
  const [latest, setLatest] = useState(null);
  const profile = avgProfile(drink.taste, reviews);

  useEffect(() => { setReviews(drink.reviews); setLatest(null); }, [drinkId]);

  function onSubmitted(rv) {
    setReviews((rs) => [rv, ...rs]);
    setLatest(rv);
  }

  return (
    <div className="page page-narrow screen-enter">
      <button className="btn btn-quiet btn-sm" style={{ padding: '6px 8px', marginBottom: 12, marginLeft: -6 }} onClick={() => go('browse')}>
        <Icon name="back" size={15} /> All drinks
      </button>

      <div className="detail-layout">
        {/* LEFT — hero + profile */}
        <div className="detail-left">
          <div className="detail-hero">
            <DrinkImage drink={drink} height={210} radius={0} label={true}>
              <span style={{ position: 'absolute', top: 12, right: 12, display: 'flex', gap: 6 }}>
                {drink.iced && <Pill kind="bare" style={{ background: 'rgba(255,253,248,0.85)' }} icon={<Icon name="snow" size={12} />}>iced</Pill>}
                {drink.hot && <Pill kind="warm" style={{ background: 'rgba(255,253,248,0.9)' }} icon={<Icon name="flame" size={12} />}>hot</Pill>}
              </span>
            </DrinkImage>
            <div className="detail-body">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12 }}>
                <div>
                  <h1 className="display" style={{ fontSize: 27 }}>{drink.name}</h1>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, color: 'var(--ink-3)', marginTop: 5 }}>
                    <Icon name="pin" size={14} color="var(--ink-4)" /> {cafeName(drink.cafe)} · {CAFES[drink.cafe].area}
                  </div>
                </div>
                <span className="mono" style={{ fontSize: 19, color: 'var(--matcha-700)', fontWeight: 500 }}>${drink.price.toFixed(2)}</span>
              </div>
              <p className="lead" style={{ fontSize: 14.5, marginTop: 14 }}>{drink.desc}</p>
              <div style={{ marginTop: 14 }}><DrinkTags drink={drink} /></div>
            </div>
          </div>

          <div className="panel">
            <div className="panel-h">
              <h2>Taste profile</h2>
              <span className="mono" style={{ fontSize: 11, color: 'var(--ink-4)' }}>{reviews.length} {reviews.length === 1 ? 'review' : 'reviews'}</span>
            </div>
            <TasteBars taste={profile} animate />
            <p style={{ fontSize: 12, color: 'var(--ink-3)', marginTop: 14, lineHeight: 1.5 }}>
              Averaged from every parsed review. Values shift as the community pours in more notes.
            </p>
          </div>
        </div>

        {/* RIGHT — review form + reviews */}
        <div className="detail-right">
          <div className="panel">
            <div className="panel-h"><h2>Leave a tasting note</h2></div>
            {latest ? (
              <div className="flow" style={{ ['--gap']: '14px' }}>
                <ParsedResult review={latest} />
                <button className="btn btn-quiet btn-sm" style={{ marginLeft: -6 }} onClick={() => setLatest(null)}>
                  <Icon name="plus" size={14} /> Write another
                </button>
              </div>
            ) : (
              <ReviewForm onSubmitted={onSubmitted} />
            )}
          </div>

          <div className="panel">
            <div className="panel-h">
              <h2>Community notes</h2>
              <span className="mono" style={{ fontSize: 11, color: 'var(--ink-4)' }}>{reviews.length}</span>
            </div>
            {reviews.length === 0 ? (
              <EmptyState icon="leaf" title="No notes yet" body="Be the first to describe this pour and start its taste profile." />
            ) : (
              <div>
                {reviews.map((rv) => (
                  <div className="review" key={rv.id}>
                    <p className="review-quote">“{rv.text}”</p>
                    <div className="review-meta">
                      {rv.mine && <Pill kind="warm" mono>your note</Pill>}
                      {(rv.tags || []).map((t) => <Pill key={t} kind="bare">{t}</Pill>)}
                    </div>
                    <div className="review-foot">
                      <span>S{rv.s} · Sw{rv.w} · Cr{rv.c} · E{rv.e} · B{rv.b}</span>
                      <span style={{ width: 3, height: 3, borderRadius: 9, background: 'var(--ink-4)' }} />
                      <span>{Math.round(rv.conf * 100)}% conf</span>
                      <span style={{ width: 3, height: 3, borderRadius: 9, background: 'var(--ink-4)' }} />
                      <span>{rv.when}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { Detail, ReviewForm, ParsedResult, avgProfile });
