# Design Implementation Notes

Reference: `docs/design/matcha-scout/HANDOFF.md`

---

## What was implemented

### Design tokens
All tokens from HANDOFF.md §1 are live in `frontend/app/globals.css` under `@theme inline` (Tailwind v4):
- Full palette: paper, card, ink, line, matcha, hojicha, danger variants
- Shadows: `--shadow-xs`, `--shadow-sm`, `--shadow`, `--shadow-lg` (warm-tinted, never gray)
- Radius scale: `--r-xs` (8px) → `--r-xl` (32px)

### Typography
Three-font stack loaded via Google Fonts CSS `@import` (precedes `@import "tailwindcss"` as required):
- **Newsreader** — serif display/headings, via `.ms-display`, `.ms-serif`, `.ms-serif-i` CSS classes
- **Hanken Grotesk** — all body/UI text (default `font-family` on `body`)
- **IBM Plex Mono** — data accents via `.ms-mono`, `.ms-eyebrow` classes; used for: match %, prices, taste values, step counters, review metadata

### Components updated/created
| Component | Changes |
|---|---|
| `globals.css` | Full design system: tokens, typography, buttons, pills, taste bars, slider, field, drink-img placeholder, scale buttons, quiz progress, animations |
| `layout.tsx` | Matcha-bowl SVG mark, "Matcha *Scout*" serif+italic wordmark, blurred sticky header, mobile bottom tab bar with raised Match FAB |
| `app/page.tsx` | Hero with eyebrow + italic-accent display headline + proof stats + preview card; 3 feature cards; 3-step "how it works" card with CTA |
| `app/quiz/page.tsx` | Results use `RecCard` with `MatchRing`, `compareTo` taste bars, reasons list, rank ribbon, "Top match" pill |
| `PreferenceQuiz.tsx` | Guided one-question-at-a-time: segmented progress bar, mono step counter, 1–5 scale buttons with auto-advance (240ms), back/skip footer, price chips + milk chips on final step |
| `TasteBars.tsx` | Paper-2 track with 5-segment tick marks; matcha gradient fill; optional `compareTo` prop renders a hojicha (#a9774e) vertical marker at user's preference value |
| `DrinkCard.tsx` | Gradient photo placeholder with checkerboard overlay + foam bubble; serif name + mono price; hover lift effect |
| `ReviewForm.tsx` | Live char count (mono, turns matcha green at minimum); "Anonymous — no account needed" note with leaf icon; "Submit & parse" label; `ParsedResultPanel` exported — matcha-tint→card gradient, ✓ header with confidence %, 5-cell grid, flavor tag pills |
| `LoadingState.tsx` | "Steeping your matches…"; double-ring spinner (outer: matcha-tint track, matcha-600 sweep; inner: matcha dot) |
| `ErrorState.tsx` | "That pour didn't land"; hojicha-tint circular icon backplate |
| `Icons.tsx` | New shared SVG icon primitives (Spark, Check, Arrow, Back, Leaf, Drop, Search, Filter, Star) |
| `MatchRing.tsx` | New SVG ring component; tone: matcha-600 ≥85%, ripe ≥70%, hojicha <70% |
| `EmptyState.tsx` | New: circular tinted icon backplate + serif title + muted body + optional action |
| `app/drinks/page.tsx` | Split into server page + `DrinksClient` |
| `DrinksClient.tsx` | New: search input with icon, horizontal-scroll filter chips, sort segmented control, empty state |
| `DrinkDetailClient.tsx` | 2-col desktop layout via `detail-2col` CSS class; gradient image hero with foam; parsed result uses `ParsedResultPanel`; review quotes in italic serif; mono metadata footer |

---

## Design ideas intentionally deferred

| Item | Reason deferred |
|---|---|
| Paper grain SVG texture on app background | Very subtle; skipped to keep CSS clean and load fast |
| Results page "sticky Your Profile" summary sidebar | Adds state complexity; deferred to Phase 6 |
| Browse page `Segmented` sort with icon labels | Implemented as plain button group, not the exact prototype segmented control |
| Drink card photo swatch loaded from API | Backend doesn't serve images; gradient swatches hardcoded by ID |
| Horizontal-scroll recommendation card layout on desktop | Kept as vertical list; simpler and equally scannable |
| `detail-right` panel sticky on desktop | Deferred; adds scroll behavior complexity |
| Paper grain animation / feTurbulence SVG | Optional per HANDOFF; skipped |
| "Write another" action after review submit | Simple flow; panel replaces form only once |
| Hojicha-warm "your note" pill on user's own reviews | No user identity in anonymous MVP |

---

## Screenshots to take for README / resume

1. **Landing page desktop** — hero with 2-col layout, preview card, feature grid
2. **Landing page mobile** — stacked hero, bottom tab bar visible
3. **Quiz step** — single question card with 1–5 buttons and progress bar
4. **Quiz filter step** — price chips + milk chips
5. **Recommendations results** — match ring, rank ribbon, "Top match" pill, compareTo taste bar marker
6. **Browse page** — search/filter chips, card grid with gradient placeholders
7. **Drink detail** — 2-col desktop layout with hero card and review form
8. **Parsed result panel** — 5-cell grid, confidence %, flavor tags after review submission
