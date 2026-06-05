/* Matcha Scout — deterministic recommendation engine.
   Transparent weighted-similarity scoring (no randomness). */
window.MS_ENGINE = (function () {
  const DIMS = ['strength', 'sweet', 'creamy', 'earthy', 'bitter'];
  // how much each dimension pulls the score
  const WEIGHTS = { strength: 1.3, sweet: 1.1, creamy: 1.0, earthy: 1.0, bitter: 1.0 };
  const LABEL = { strength: 'matcha strength', sweet: 'sweetness', creamy: 'creaminess', earthy: 'earthiness', bitter: 'bitterness' };

  function score(prefs, drink) {
    let dist = 0, wsum = 0;
    DIMS.forEach((k) => {
      const w = WEIGHTS[k];
      dist += w * Math.abs(prefs[k] - drink.taste[k]);
      wsum += w;
    });
    const maxDist = wsum * 4;
    const sim = 1 - dist / maxDist;            // 0..1
    const pct = Math.round(45 + sim * 54);     // map into a believable 45..99 band
    return { sim, pct };
  }

  function reasons(prefs, drink) {
    const out = [];
    // 1. closest-matching strong dimension
    const ranked = DIMS
      .map((k) => ({ k, gap: Math.abs(prefs[k] - drink.taste[k]), want: prefs[k], has: drink.taste[k] }))
      .sort((a, b) => a.gap - b.gap);
    const best = ranked[0];
    if (best.gap <= 1) {
      if (best.has >= 4) out.push(`Bold ${LABEL[best.k]} — right where you wanted it`);
      else if (best.has <= 2) out.push(`Gentle ${LABEL[best.k]}, just like your taste`);
      else out.push(`Balanced ${LABEL[best.k]} that matches your profile`);
    }
    // 2. milk preference
    if (prefs.milk && prefs.milk !== 'any' && drink.milk.includes(prefs.milk)) {
      out.push(`Available with ${prefs.milk} milk`);
    } else if (!prefs.milk || prefs.milk === 'any') {
      if (drink.milk.includes('oat')) out.push('Available with oat milk');
    }
    // 3. budget
    if (prefs.priceMax && drink.price <= prefs.priceMax) {
      out.push(`$${drink.price.toFixed(2)} — under your $${prefs.priceMax.toFixed(0)} budget`);
    }
    // 4. fallback flavor note
    if (out.length < 2) {
      const worst = ranked[ranked.length - 1];
      if (worst.gap >= 2) out.push(`A touch ${worst.has > worst.want ? 'more' : 'less'} ${LABEL[worst.k]} than your ideal`);
    }
    return out.slice(0, 3);
  }

  function recommend(prefs, drinks) {
    let pool = drinks.slice();
    // hard filters
    if (prefs.priceMax) pool = pool.filter((d) => d.price <= prefs.priceMax);
    if (prefs.milk && prefs.milk !== 'any') pool = pool.filter((d) => d.milk.includes(prefs.milk));
    return pool
      .map((d) => {
        const { sim, pct } = score(prefs, d);
        return { drink: d, pct, sim, reasons: reasons(prefs, d) };
      })
      .sort((a, b) => b.sim - a.sim);
  }

  // crude "AI" parse of a free-text review into 1..5 ratings (demo only)
  function parseReview(text) {
    const t = ' ' + text.toLowerCase() + ' ';
    const base = { strength: 3, sweet: 3, creamy: 3, earthy: 3, bitter: 3 };
    const bump = (k, n) => { base[k] = Math.max(1, Math.min(5, base[k] + n)); };
    const has = (...ws) => ws.some((w) => t.includes(w));
    if (has('strong', 'bold', 'intense', 'punchy', 'potent')) bump('strength', 2);
    if (has('weak', 'mild', 'faint', 'subtle', 'light matcha')) bump('strength', -2);
    if (has('sweet', 'sugary', 'dessert', 'caramel', 'vanilla', 'syrup')) bump('sweet', 2);
    if (has('not sweet', 'unsweet', 'bitter', 'dry')) bump('sweet', -1);
    if (has('creamy', 'smooth', 'velvety', 'rich', 'silky')) bump('creamy', 2);
    if (has('watery', 'thin', 'light')) bump('creamy', -1);
    if (has('grassy', 'earthy', 'vegetal', 'umami', 'green', 'herbal')) bump('earthy', 2);
    if (has('clean', 'bright', 'citrus')) bump('earthy', -1);
    if (has('bitter', 'astringent', 'sharp')) bump('bitter', 2);
    if (has('mellow', 'smooth', 'no bitterness')) bump('bitter', -1);
    const tags = [];
    [['creamy','creamy'],['grassy','grassy'],['sweet','sweet'],['umami','umami'],['nutty','nutty'],['bitter','bitter'],['balanced','balanced'],['refreshing','refreshing'],['citrus','citrus']]
      .forEach(([w, tag]) => { if (t.includes(w) && !tags.includes(tag)) tags.push(tag); });
    const conf = Math.min(0.95, 0.6 + Math.min(text.length, 220) / 600 + tags.length * 0.03);
    return { strength: base.strength, sweet: base.sweet, creamy: base.creamy, earthy: base.earthy, bitter: base.bitter, tags: tags.slice(0, 4), conf: Math.round(conf * 100) / 100 };
  }

  return { recommend, reasons, score, parseReview, DIMS, LABEL };
})();
