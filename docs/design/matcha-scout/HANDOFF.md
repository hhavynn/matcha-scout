# Matcha Scout — Design Handoff

A premium "boutique matcha guide" redesign of the existing Next.js + Tailwind app.
Voice: *quiet luxury · calm sommelier · cozy matcha bar.* Mobile-first, no required image assets, low animation, solo-dev friendly.

**Prototype files (reference implementation, plain React/CSS):**
- `Matcha Scout.html` — full clickable prototype (mobile frame + desktop toggle, all 6 pages)
- `Matcha Scout — Variations.html` — side-by-side option canvas
- `styles/matcha.css` + `styles/app.css` — every token & component style is here; lift values directly.

---

## 1. Color palette

| Token | Hex | Use |
|---|---|---|
| `paper` | `#f6f1e7` | page background (warm cream) |
| `paper-2` | `#efe8d8` | inset tracks, alt fills |
| `card` | `#fffdf8` | card / panel surface |
| `card-2` | `#faf5ea` | quiet inputs, secondary cards |
| `ink` | `#2a3124` | primary text |
| `ink-2` | `#585e4d` | body / secondary text |
| `ink-3` | `#8c8a78` | meta, captions |
| `ink-4` | `#aaa794` | faint meta, placeholders |
| `line` | `#e8e1d0` | hairlines / card borders |
| `line-2` | `#ded5c1` | stronger borders, input rings |
| `matcha` | `#5f7850` | brand fill / bars |
| `matcha-600` | `#56703f` | primary buttons |
| `matcha-700` | `#44563a` | hover / active text |
| `matcha-800` | `#36442e` | deepest text on tint |
| `matcha-soft` | `#cdd9b8` | highlight ring on top match |
| `matcha-tint` | `#e7eddc` | chips, icon backplates |
| `hojicha` | `#a9774e` | warm accent (price/budget, "your target" marker) |
| `hojicha-tint` | `#f3e8d6` | warm chip background |
| `danger` | `#a64b3e` | validation errors |

Shadows are warm-tinted, never gray: `0 6px 20px -8px rgba(58,48,24,0.14)`. Paper grain = a 5%-opacity `feTurbulence` SVG tiled on the app background (optional; subtle).

## 2. Typography (all free Google Fonts)

```
Newsreader      → display / headings (serif, weights 400–600, has italic)
Hanken Grotesk  → UI / body (400–700)
IBM Plex Mono   → data accents only: match %, taste values, prices, eyebrows
```

- Headlines use Newsreader 500, `letter-spacing: -0.02em`. Italic Newsreader is the accent (e.g. *"you"* in the hero, review quotes).
- Eyebrows: IBM Plex Mono, 11px, uppercase, `0.18em` tracking, matcha-600.
- Never go below 13px for body on mobile; hit targets ≥ 44px.

## 3. Tailwind setup (drop into `app/globals.css`)

```css
@import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400;1,6..72,500&family=Hanken+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

@theme inline {
  --color-paper: #f6f1e7;
  --color-paper-2: #efe8d8;
  --color-card: #fffdf8;
  --color-ink: #2a3124;
  --color-ink-2: #585e4d;
  --color-ink-3: #8c8a78;
  --color-line: #e8e1d0;
  --color-matcha-500: #5f7850;
  --color-matcha-600: #56703f;
  --color-matcha-700: #44563a;
  --color-matcha-tint: #e7eddc;
  --color-hojicha: #a9774e;
  --font-display: 'Newsreader', Georgia, serif;
  --font-sans: 'Hanken Grotesk', system-ui, sans-serif;
  --font-mono: 'IBM Plex Mono', ui-monospace, monospace;
  --radius-card: 18px;
}
body { background: var(--color-paper); color: var(--color-ink); font-family: var(--font-sans); }
```

Then in `next/font`: load `Newsreader`, `Hanken_Grotesk`, `IBM_Plex_Mono` and wire the CSS variables in `layout.tsx`.

## 4. Component specs (map to your existing files)

- **Header / nav** (`layout.tsx`): cream blurred sticky bar. Geometric matcha-bowl mark (ring + filled circle + foam dot) + "Matcha *Scout*" wordmark (Scout in italic serif). Desktop: text links + pill CTA. **Mobile: replace links with a bottom tab bar** (Home / Browse / Match) — Match is a raised matcha FAB.
- **CTA button**: pill, `matcha-600`, 14×24px padding, weight 600, soft matcha shadow. Ghost variant = `card` bg + `line-2` inset ring.
- **Tag / pill**: matcha-tint (default), `pill-bare` (card-2 + border) for milk options, `pill-warm` (hojicha) for hot / budget. 6×11px, 12px.
- **Drink card** (`DrinkCard.tsx`): photo slot on top (rounded 12px, gradient placeholder + "drink photo" mono tag), then name (serif 18) + price (mono, matcha-700), cafe·area meta, 2-line blurb, milk/temp pills. Hover: lift 3px + larger shadow.
- **Taste profile bars** (`TasteBars.tsx`): grid `92px 1fr 18px`. Track = paper-2 with faint 5-segment ticks; fill = matcha gradient, animated width. Mono value at right. On recommendation cards, overlay a hojicha vertical marker at the user's target value (`compareTo`).
- **Slider input** (`PreferenceQuiz.tsx`): 8px paper-2 track, 26px circular thumb (card fill, 2px matcha inset ring).
- **Recommendation card**: match **ring** (SVG circle, mono % inside; matcha→ripe→hojicha by score), rank `#n`, "Top match" pill on #1 (inline, not a corner ribbon), name/cafe/price, ✓ reason list, taste bars w/ target marker, milk pills, Details button. #1 gets a `matcha-soft` highlight ring.
- **Review form** (`ReviewForm.tsx`): textarea (card, inset ring, focus = matcha ring + halo), live char count (mono), "Anonymous — no account needed" note, "Submit & parse" button with spinner → on success swap to the parsed-result panel.
- **Parsed result**: matcha-tint→card gradient panel, ✓ + confidence %, 5-cell grid (mono value + label), flavor tag pills. Should feel like a satisfying reveal.
- **Review card**: italic serif quote, tag pills, mono footer (S·Sw·Cr·E·B values · confidence · date). "your note" warm pill on the user's own.
- **Empty / Error / Loading states**: centered, circular tinted icon backplate, serif title, muted body. Loading = matcha ring spinner ("Steeping your matches…"). Error uses hojicha tint ("That pour didn't land").

## 5. Page layout notes

1. **Landing** — hero (eyebrow + serif headline w/ italic accent + lead + two CTAs + proof stats). Desktop = 2-col with a live "Top Match" preview card; mobile stacks. Then 3 numbered feature cards, then a 3-step "how it works" card with CTA.
2. **Quiz** — guided, **one question at a time** (segmented progress bar, mono step counter, big 1–5 scale buttons that auto-advance, lo/hi end labels). Final optional step: max-price chips + milk chips. Back/skip footer.
3. **Recommendations** — desktop 2-col: sticky "Your profile" summary (taste bars + active filters + Edit) and a ranked card list; mobile single column. Empty state when filters exclude all.
4. **Browse** — title + sort segmented, search field, horizontally-scrollable filter chips, responsive grid (1 → 3 col).
5. **Drink detail** — desktop 2-col (hero card + taste profile | review form + community notes), mobile single col (max 760px). Profile is the average of parsed reviews and updates live on submit.
6. **Review submit** — inline parse → reveal parsed result, with "Write another".

## 6. Responsive behavior
Mobile-first. Bottom tab bar on phones, top links on desktop. All grids collapse to 1 column. Recommendation cards stay skimmable (ring + reasons read top-down). Use container/`md:` breakpoints — the prototype switches layouts at ~720px container width.

## 7. UI copy
- Hero: **"Find the matcha that tastes like *you*."** / sub: "Tell us how you like it — strong, sweet, creamy, earthy — and we'll rank real cafe drinks against your taste, using community reviews our AI reads for you."
- CTAs: **Find my matcha** · Browse drinks · Start the tasting → · See my matches
- Quiz prompts: "How strong should the matcha be?" · "How sweet do you like it?" · "How creamy should it feel?" · "How grassy and earthy?" · "How much bitter edge?"
- Results: **"Poured just for your taste"** / "Ranked by how closely each drink fits the profile you set — with the reasons in plain sight."
- Reason chips: "Bold matcha strength — right where you wanted it" · "Available with oat milk" · "$5.75 — under your $8 budget"
- Empty (no matches): **"No drinks fit those filters"** / "Loosen them and we'll find your closest pours." → Adjust preferences
- Empty (browse search): **"Nothing matches that yet"** / "Try a different search or clear your filters."
- Error: **"That pour didn't land"** + Try again
- Review placeholder: *"Describe what you tasted… 'Bold and grassy with a creamy oat finish, barely sweet.' The AI turns your words into taste ratings."*
- Review success: **"Review parsed & added"** + "NN% confidence"

## 8. Paste-into-Claude-Code prompt

> Restyle my Next.js + Tailwind "Matcha Scout" app to a premium boutique-matcha-cafe aesthetic. Use this palette: paper `#f6f1e7`, card `#fffdf8`, ink `#2a3124`/`#585e4d`/`#8c8a78`, hairline `#e8e1d0`, matcha `#5f7850`/`#56703f`/`#44563a`, matcha-tint `#e7eddc`, warm accent hojicha `#a9774e`. Fonts: Newsreader (serif) for headings + italic accents, Hanken Grotesk for UI, IBM Plex Mono for data (match %, taste values, prices, eyebrows). Add the @theme tokens and font imports to `globals.css`/`layout.tsx`.
>
> Then update each component to match these specs (see full spec in HANDOFF.md): cream blurred sticky header with a geometric matcha-bowl mark + "Matcha *Scout*" wordmark and a mobile bottom tab bar; pill buttons; drink cards with a rounded gradient photo slot, serif name + mono price + milk pills; taste profile as horizontal bars (paper-2 track w/ segment ticks, matcha gradient fill, mono value) with an optional hojicha "your target" marker; recommendation cards with an SVG match ring, inline "Top match" pill, ✓ reason list, and target-marked taste bars; a guided one-question-at-a-time quiz with a segmented progress bar and 1–5 scale buttons; a review form whose success state reveals a parsed 5-cell result panel with confidence and flavor tags; warm empty/error/loading states. Keep my data model, API calls, and routes exactly as they are — this is styling + layout only. Mobile-first, Tailwind-only, no new image assets, minimal animation.

Keep the deterministic ranking and AI-parse logic unchanged — the redesign is presentation only.
