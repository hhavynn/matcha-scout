/* Matcha Scout — shared primitives (exported to window) */
const { useState, useEffect, useRef } = React;

/* ---------- brand mark: matcha bowl from above ---------- */
function Mark({ size = 28, tone = 'var(--matcha)' }) {
  const s = size;
  return (
    <svg width={s} height={s} viewBox="0 0 32 32" fill="none" aria-hidden="true" style={{ display: 'block' }}>
      <circle cx="16" cy="16" r="14.2" stroke={tone} strokeWidth="1.6" opacity="0.45" />
      <circle cx="16" cy="16" r="9.4" fill={tone} />
      <circle cx="12.4" cy="12.6" r="3.1" fill="#fffdf8" opacity="0.42" />
    </svg>
  );
}

function Logo({ size = 28, mono = false }) {
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 10 }}>
      <Mark size={size} tone={mono ? 'currentColor' : 'var(--matcha)'} />
      <span style={{ display: 'inline-flex', flexDirection: 'column', lineHeight: 1 }}>
        <span className="serif" style={{ fontSize: size * 0.74, color: 'var(--ink)', letterSpacing: '-0.02em' }}>
          Matcha <span className="serif-i" style={{ color: 'var(--matcha-700)' }}>Scout</span>
        </span>
      </span>
    </span>
  );
}

/* ---------- icon set (simple geometric line icons) ---------- */
function Icon({ name, size = 18, stroke = 1.7, color = 'currentColor' }) {
  const p = { fill: 'none', stroke: color, strokeWidth: stroke, strokeLinecap: 'round', strokeLinejoin: 'round' };
  const paths = {
    search: <><circle cx="8" cy="8" r="5.2" {...p} /><line x1="12" y1="12" x2="16.5" y2="16.5" {...p} /></>,
    arrow: <><line x1="3" y1="10" x2="16" y2="10" {...p} /><path d="M11 5l5 5-5 5" {...p} /></>,
    back: <path d="M12 5l-5 5 5 5" {...p} />,
    check: <path d="M4 10.5l4 4 8-9" {...p} />,
    plus: <><line x1="10" y1="4" x2="10" y2="16" {...p} /><line x1="4" y1="10" x2="16" y2="10" {...p} /></>,
    close: <><line x1="5" y1="5" x2="15" y2="15" {...p} /><line x1="15" y1="5" x2="5" y2="15" {...p} /></>,
    spark: <path d="M10 3c.7 3.2 1.8 4.3 5 5-3.2.7-4.3 1.8-5 5-.7-3.2-1.8-4.3-5-5 3.2-.7 4.3-1.8 5-5z" {...p} />,
    filter: <><line x1="3" y1="6" x2="17" y2="6" {...p} /><line x1="6" y1="10" x2="14" y2="10" {...p} /><line x1="8.5" y1="14" x2="11.5" y2="14" {...p} /></>,
    grid: <><rect x="3.5" y="3.5" width="5.5" height="5.5" rx="1.4" {...p} /><rect x="11" y="3.5" width="5.5" height="5.5" rx="1.4" {...p} /><rect x="3.5" y="11" width="5.5" height="5.5" rx="1.4" {...p} /><rect x="11" y="11" width="5.5" height="5.5" rx="1.4" {...p} /></>,
    leaf: <path d="M16 4C8 4 4 8 4 16c8 0 12-4 12-12zM7 13c3-1 5-3 6-6" {...p} />,
    drop: <path d="M10 3.5s5 5.5 5 8.5a5 5 0 11-10 0c0-3 5-8.5 5-8.5z" {...p} />,
    snow: <><line x1="10" y1="3" x2="10" y2="17" {...p} /><line x1="3.5" y1="6.5" x2="16.5" y2="13.5" {...p} /><line x1="16.5" y1="6.5" x2="3.5" y2="13.5" {...p} /></>,
    flame: <path d="M10 3c1 3-2 4-2 7a2 2 0 004 0c0-1-.5-1.5-.5-2.5C13 9 13.5 12 13.5 13a3.5 3.5 0 11-7 0C6.5 9 9 7 10 3z" {...p} />,
    pin: <><path d="M10 17s5-4.6 5-9a5 5 0 10-10 0c0 4.4 5 9 5 9z" {...p} /><circle cx="10" cy="8" r="1.8" {...p} /></>,
    star: <path d="M10 3l2.1 4.4 4.9.6-3.6 3.3 1 4.7L10 13.8 5.6 16l1-4.7L3 8l4.9-.6L10 3z" {...p} />,
  };
  return <svg width={size} height={size} viewBox="0 0 20 20" style={{ display: 'block', flexShrink: 0 }}>{paths[name]}</svg>;
}

/* ---------- pill ---------- */
function Pill({ children, kind = '', mono = false, icon = null, style = {} }) {
  const cls = 'pill' + (kind ? ' pill-' + kind : '') + (mono ? ' pill-mono' : '');
  return <span className={cls} style={style}>{icon}{children}</span>;
}

/* milk + temp pills derived from a drink */
function DrinkTags({ drink, max }) {
  const milk = max ? drink.milk.slice(0, max) : drink.milk;
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
      {milk.map((m) => <Pill key={m} kind="bare">{m}</Pill>)}
      {max && drink.milk.length > max && <Pill kind="bare">+{drink.milk.length - max}</Pill>}
      {drink.iced && <Pill kind="bare" icon={<Icon name="snow" size={12} />}>iced</Pill>}
      {drink.hot && <Pill kind="warm" icon={<Icon name="flame" size={12} />}>hot</Pill>}
    </div>
  );
}

/* ---------- drink image placeholder ---------- */
const TASTE_DIMS = [
  { key: 'strength', label: 'Strength' },
  { key: 'sweet', label: 'Sweetness' },
  { key: 'creamy', label: 'Creaminess' },
  { key: 'earthy', label: 'Earthiness' },
  { key: 'bitter', label: 'Bitterness' },
];

function DrinkImage({ drink, height = 150, label = true, radius, foam = true, children }) {
  return (
    <div className="drink-img" style={{
      height, ['--swatch']: drink.swatch,
      borderRadius: radius != null ? radius : undefined,
    }}>
      {foam && <div className="foam" style={{ width: height * 0.7, height: height * 0.7, top: -height * 0.22, right: -height * 0.12 }} />}
      {label && <span className="ph-tag">drink photo</span>}
      {children}
    </div>
  );
}

/* ---------- taste bars ---------- */
function TasteBars({ taste, animate = false, compareTo = null }) {
  return (
    <div className="flow" style={{ ['--gap']: '10px' }}>
      {TASTE_DIMS.map((d, i) => {
        const v = taste[d.key];
        const pct = ((v - 1) / 4) * 100;
        return (
          <div className="taste-row" key={d.key}>
            <span className="taste-label">{d.label}</span>
            <div className="taste-track">
              <div className="taste-fill" style={{
                width: pct + '%',
                transition: animate ? 'width .7s cubic-bezier(.2,.8,.2,1)' : 'none',
                transitionDelay: animate ? (i * 70) + 'ms' : '0ms',
              }} />
              {compareTo != null && (
                <div style={{
                  position: 'absolute', top: -3, bottom: -3,
                  left: `calc(${((compareTo[d.key] - 1) / 4) * 100}% - 1px)`, width: 2,
                  background: 'var(--hojicha)', borderRadius: 2, opacity: 0.85,
                }} title="your preference" />
              )}
            </div>
            <span className="taste-val">{v}</span>
          </div>
        );
      })}
    </div>
  );
}

/* ---------- match meter (ring) ---------- */
function MatchRing({ pct, size = 56, stroke = 5 }) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const tone = pct >= 85 ? 'var(--matcha-600)' : pct >= 70 ? 'var(--ripe)' : 'var(--hojicha)';
  return (
    <div style={{ position: 'relative', width: size, height: size, flexShrink: 0 }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--paper-2)" strokeWidth={stroke} />
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={tone} strokeWidth={stroke}
          strokeLinecap="round" strokeDasharray={c} strokeDashoffset={c * (1 - pct / 100)}
          style={{ transition: 'stroke-dashoffset .8s cubic-bezier(.2,.8,.2,1)' }} />
      </svg>
      <div style={{
        position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center', lineHeight: 1,
      }}>
        <span className="mono" style={{ fontSize: size * 0.27, fontWeight: 500, color: 'var(--ink)' }}>{pct}</span>
        <span className="mono" style={{ fontSize: size * 0.14, color: 'var(--ink-3)', letterSpacing: '0.1em' }}>%</span>
      </div>
    </div>
  );
}

/* ---------- states ---------- */
function LoadingState({ label = 'Steeping your matches…' }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 18, padding: '64px 24px', textAlign: 'center' }}>
      <div style={{ position: 'relative', width: 52, height: 52 }}>
        <div style={{ position: 'absolute', inset: 0, borderRadius: 999, border: '3px solid var(--matcha-tint)', borderTopColor: 'var(--matcha-600)', animation: 'ms-spin 0.9s linear infinite' }} />
        <div style={{ position: 'absolute', inset: 16, borderRadius: 999, background: 'var(--matcha)', opacity: 0.5 }} />
      </div>
      <p className="lead" style={{ fontSize: 14.5, margin: 0 }}>{label}</p>
    </div>
  );
}

function EmptyState({ title, body, action, icon = 'leaf' }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 14, padding: '52px 28px', textAlign: 'center' }}>
      <div style={{ width: 60, height: 60, borderRadius: 999, background: 'var(--matcha-tint)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--matcha-600)', boxShadow: 'inset 0 0 0 1px rgba(95,120,80,0.18)' }}>
        <Icon name={icon} size={26} />
      </div>
      <div className="serif" style={{ fontSize: 21, color: 'var(--ink)' }}>{title}</div>
      <p className="lead" style={{ fontSize: 14, margin: 0, maxWidth: 320 }}>{body}</p>
      {action}
    </div>
  );
}

function ErrorState({ title = 'That pour didn’t land', body, onRetry }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 14, padding: '52px 28px', textAlign: 'center' }}>
      <div style={{ width: 60, height: 60, borderRadius: 999, background: 'var(--hojicha-tint)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--hojicha-2)', boxShadow: 'inset 0 0 0 1px rgba(169,119,78,0.25)' }}>
        <Icon name="drop" size={26} />
      </div>
      <div className="serif" style={{ fontSize: 21, color: 'var(--ink)' }}>{title}</div>
      <p className="lead" style={{ fontSize: 14, margin: 0, maxWidth: 320 }}>{body}</p>
      {onRetry && <button className="btn btn-ghost btn-sm" onClick={onRetry}>Try again</button>}
    </div>
  );
}

/* segmented control */
function Segmented({ options, value, onChange, style = {} }) {
  return (
    <div style={{ display: 'inline-flex', background: 'var(--paper-2)', borderRadius: 999, padding: 4, boxShadow: 'inset 0 0 0 1px var(--line-2)', gap: 2, ...style }}>
      {options.map((o) => {
        const v = typeof o === 'string' ? o : o.value;
        const lbl = typeof o === 'string' ? o : o.label;
        const active = v === value;
        return (
          <button key={v} onClick={() => onChange(v)} style={{
            border: 'none', background: active ? 'var(--card)' : 'transparent',
            color: active ? 'var(--ink)' : 'var(--ink-3)', fontWeight: 600, fontSize: 13,
            padding: '7px 15px', borderRadius: 999, transition: 'all .15s ease',
            boxShadow: active ? 'var(--shadow-xs)' : 'none', display: 'inline-flex', alignItems: 'center', gap: 6,
          }}>{lbl}</button>
        );
      })}
    </div>
  );
}

Object.assign(window, {
  Mark, Logo, Icon, Pill, DrinkTags, DrinkImage, TasteBars, MatchRing,
  LoadingState, EmptyState, ErrorState, Segmented, TASTE_DIMS,
});
