/* Matcha Scout — screens part A: Header, BottomNav, Landing, Browse */
const { cafes: CAFES, drinks: DRINKS } = window.MS_DATA;
const cafeName = (id) => (CAFES[id] ? CAFES[id].name : '');

/* ---------------- Header ---------------- */
function Header({ page, go }) {
  return (
    <header className="app-header">
      <div className="app-header-inner">
        <button onClick={() => go('home')} style={{ background: 'none', border: 'none', padding: 0, cursor: 'pointer' }}>
          <Logo size={26} />
        </button>
        <nav className="nav-links">
          <button className={'nav-link' + (page === 'browse' ? ' active' : '')} onClick={() => go('browse')}>Browse</button>
          <button className={'nav-link' + (page === 'home' ? ' active' : '')} onClick={() => go('home')}>How it works</button>
        </nav>
        <div className="header-cta">
          <button className="btn btn-primary btn-sm" onClick={() => go('quiz')}>
            <Icon name="spark" size={15} color="#fcfdf8" /> Find my matcha
          </button>
        </div>
      </div>
    </header>
  );
}

/* ---------------- Bottom tab bar (mobile) ---------------- */
function BottomNav({ page, go }) {
  const tab = (id, label, icon, target) => (
    <button className={'tab' + (page === id ? ' active' : '')} onClick={() => go(target)}>
      <span className="tab-ico"><Icon name={icon} size={20} /></span>{label}
    </button>
  );
  return (
    <nav className="tabbar">
      {tab('home', 'Home', 'leaf', 'home')}
      {tab('browse', 'Browse', 'grid', 'browse')}
      <button className={'tab tab-cta' + (page === 'quiz' || page === 'results' ? ' active' : '')} onClick={() => go('quiz')}>
        <span className="tab-ico"><Icon name="spark" size={20} color="#fff" /></span>Match
      </button>
    </nav>
  );
}

/* ---------------- Drink card ---------------- */
function DrinkCardItem({ drink, go }) {
  return (
    <button className="drink-card" onClick={() => go('drink', { drinkId: drink.id })}>
      <DrinkImage drink={drink} height={132} radius={12} />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 9, padding: '0 4px 4px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, alignItems: 'flex-start' }}>
          <div>
            <div className="dc-title">{drink.name}</div>
            <div className="dc-cafe">{cafeName(drink.cafe)} · {CAFES[drink.cafe].area}</div>
          </div>
          <span className="dc-price">${drink.price.toFixed(2)}</span>
        </div>
        <p style={{ margin: 0, fontSize: 13, color: 'var(--ink-2)', lineHeight: 1.5, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>{drink.blurb}</p>
        <DrinkTags drink={drink} max={3} />
      </div>
    </button>
  );
}

/* ---------------- Landing ---------------- */
function Landing({ go }) {
  const featured = DRINKS.find((d) => d.id === 'd-classic');
  const FEATURES = [
    { n: '01', ic: 'spark', t: 'AI reads the reviews', b: 'Members describe a drink in plain words. Our parser turns “grassy, barely sweet, super creamy” into structured taste ratings.' },
    { n: '02', ic: 'drop', t: 'Matched to your palate', b: 'A transparent similarity score ranks every drink against your tasting profile — no black-box guessing, just math you can see.' },
    { n: '03', ic: 'leaf', t: 'Grown by the community', b: 'Each anonymous review sharpens a drink’s profile. The more people pour in, the better every match gets.' },
  ];
  return (
    <div className="page screen-enter">
      {/* hero */}
      <section className="hero">
        <div className="hero-grid">
          <div className="anim-up">
            <span className="eyebrow">A boutique matcha guide</span>
            <h1 className="display">Find the matcha<br/>that tastes like <span className="serif-i" style={{ color: 'var(--matcha-700)' }}>you</span>.</h1>
            <p className="lead">Tell us how you like it — strong, sweet, creamy, earthy — and we’ll rank real cafe drinks against your taste, using community reviews our AI reads for you.</p>
            <div className="hero-cta">
              <button className="btn btn-primary btn-lg" onClick={() => go('quiz')}>
                <Icon name="spark" size={16} color="#fcfdf8" /> Find my matcha
              </button>
              <button className="btn btn-ghost btn-lg" onClick={() => go('browse')}>Browse drinks</button>
            </div>
            <div className="hero-proof">
              <span><strong style={{ color: 'var(--ink-2)' }}>{DRINKS.length}</strong> drinks</span>
              <span style={{ width: 4, height: 4, borderRadius: 9, background: 'var(--ink-4)' }} />
              <span><strong style={{ color: 'var(--ink-2)' }}>{Object.keys(CAFES).length}</strong> cafes</span>
              <span style={{ width: 4, height: 4, borderRadius: 9, background: 'var(--ink-4)' }} />
              <span>5-dimension taste profiles</span>
            </div>
          </div>
          {/* preview card */}
          <div className="anim-up" style={{ animationDelay: '.08s' }}>
            <PreviewCard drink={featured} go={go} />
          </div>
        </div>
      </section>

      {/* features */}
      <section style={{ marginTop: 44 }}>
        <div style={{ textAlign: 'center', marginBottom: 22 }}>
          <span className="eyebrow">How it works</span>
          <h2 className="display" style={{ fontSize: 28, marginTop: 8 }}>Calm, honest matcha matching</h2>
        </div>
        <div className="feature-grid">
          {FEATURES.map((f) => (
            <div className="feature" key={f.n}>
              <div className="fic"><Icon name={f.ic} size={20} /></div>
              <div className="fnum">{f.n}</div>
              <h3>{f.t}</h3>
              <p>{f.b}</p>
            </div>
          ))}
        </div>
      </section>

      {/* steps + cta band */}
      <section style={{ marginTop: 40 }}>
        <div className="card" style={{ padding: '30px 24px', overflow: 'hidden', position: 'relative' }}>
          <div style={{ textAlign: 'center', marginBottom: 22 }}>
            <h2 className="display" style={{ fontSize: 24 }}>Three sips to your match</h2>
          </div>
          <div className="steps">
            {[['Pour your preferences', 'Slide through five taste dials in a guided, one-at-a-time flow.'],
              ['See ranked matches', 'Every drink scored against your profile, with the reasons spelled out.'],
              ['Taste & give back', 'Leave an anonymous review — the AI parses it and sharpens the profile.']].map(([t, b], i) => (
              <div className="step" key={i}>
                <div className="step-n">{i + 1}</div>
                <div>
                  <div style={{ fontFamily: 'var(--ff-display)', fontWeight: 500, fontSize: 17, color: 'var(--ink)' }}>{t}</div>
                  <p style={{ margin: '4px 0 0', fontSize: 13, color: 'var(--ink-2)', lineHeight: 1.5 }}>{b}</p>
                </div>
              </div>
            ))}
          </div>
          <div style={{ textAlign: 'center', marginTop: 26 }}>
            <button className="btn btn-primary btn-lg" onClick={() => go('quiz')}>Start the tasting →</button>
          </div>
        </div>
      </section>
    </div>
  );
}

function PreviewCard({ drink, go }) {
  return (
    <div className="rec-card rank-1" style={{ maxWidth: 380, margin: '0 auto' }}>
      <div style={{ display: 'flex', gap: 14, alignItems: 'center', marginBottom: 14 }}>
        <DrinkImage drink={drink} height={76} radius={14} label={false} foam={true} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <Pill mono icon={<Icon name="star" size={11} />} style={{ marginBottom: 6 }}>Top match</Pill>
          <div style={{ fontFamily: 'var(--ff-display)', fontWeight: 500, fontSize: 19, lineHeight: 1.1 }}>{drink.name}</div>
          <div style={{ fontSize: 12.5, color: 'var(--ink-3)', marginTop: 3 }}>{cafeName(drink.cafe)}</div>
          <div className="mono" style={{ fontSize: 13, color: 'var(--matcha-700)', marginTop: 6 }}>${drink.price.toFixed(2)}</div>
        </div>
        <MatchRing pct={94} size={58} />
      </div>
      <div className="reasons" style={{ marginBottom: 14 }}>
        {['Balanced strength that matches your profile', 'Available with oat milk', '$5.75 — under your $8 budget'].map((r, i) => (
          <div className="reason" key={i}><span className="rc"><Icon name="check" size={12} /></span>{r}</div>
        ))}
      </div>
      <div style={{ borderTop: '1px solid var(--line)', paddingTop: 14 }}>
        <TasteBars taste={drink.taste} />
      </div>
    </div>
  );
}

Object.assign(window, { Header, BottomNav, DrinkCardItem, Landing, PreviewCard, cafeName, CAFES, DRINKS });
