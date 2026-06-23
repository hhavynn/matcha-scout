# Launch QA Checklist

Use this checklist before sharing Matcha Scout for review collection.

## Production Links

- Homepage: https://matcha-scout.vercel.app
- Review queue: https://matcha-scout.vercel.app/review
- Drinks: https://matcha-scout.vercel.app/drinks
- Cafes: https://matcha-scout.vercel.app/cafes
- Quiz: https://matcha-scout.vercel.app/quiz
- API health: https://matcha-scout-api.vercel.app/health
- Review targets API: https://matcha-scout-api.vercel.app/drinks/review-targets

## Browser And Device Checks

- Desktop Chrome or Safari loads homepage and `/review`.
- Mobile Safari or Chrome loads homepage and `/review`.
- Header nav works on desktop.
- Mobile bottom nav works and includes Review.
- Text is readable without overlap on small screens.
- Review cards do not overflow or hide the review link.

## Review Flow Test

Do not create fake reviews during QA unless you intentionally coordinate a real test review for a drink someone actually tried.

- Open `/review`.
- Confirm the page explains what to do.
- Confirm users are told to review only drinks they actually tried.
- Open a review card.
- Confirm the drink detail page scrolls to or includes the review form.
- Confirm the review form says anonymous/no account needed.
- Confirm the submit button is disabled for very short text.
- Confirm the page explains that Yelp ratings/excerpts do not count toward confidence.

## Region Selector Checklist

- On `/review`, All Regions shows the current review targets.
- San Diego shows the first verified drink batch.
- Orange County empty state appears, because OC verified drinks have not been curated yet.
- Switching regions does not reload into an error state.

## Empty-State Checklist

- Orange County review queue says nothing needs reviews there right now.
- Empty state suggests trying another region or browsing all drinks.
- Empty state does not imply OC has no cafes.

## CORS And Runtime Error Checklist

- Browser console has no CORS errors.
- Browser console has no uncaught runtime errors.
- `curl -I https://matcha-scout.vercel.app/review` returns 200.
- `curl -I https://matcha-scout.vercel.app/` returns 200.
- `curl https://matcha-scout-api.vercel.app/drinks/review-targets` returns JSON.

## What To Screenshot

- Homepage hero with the review CTA visible.
- `/review` queue showing review target count and cards.
- Orange County empty state on `/review`.
- A drink detail page with the review form visible.
- A mobile view of `/review`.

## Feedback To Ask Testers For

- Did you understand that you should only review drinks you have tried?
- Could you find a drink you recognized?
- Was the review prompt clear enough?
- Did you know what kind of taste words to write?
- Did anything look broken on your device?
- Which cafes or drinks should be curated next?

## Known Limitations

- Only 24 verified drinks are live so far.
- Orange County cafes exist, but the OC verified drink batch has not been added yet.
- There is no auth; reviews are anonymous.
- There are no maps or browser geolocation.
- Recommendations improve as real reviews come in.

## Optional QR Code

QR target:

```text
https://matcha-scout.vercel.app/review
```

If needed, generate a QR code outside the repo with a trusted QR-code website or a local QR tool you already have installed. Do not add binary QR images to the repo unless there is a specific launch asset request.
