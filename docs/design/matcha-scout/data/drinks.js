/* Matcha Scout — sample data (all cafes & drinks fictional)
   taste scale 1..5: strength, sweet, creamy, earthy, bitter */
window.MS_DATA = (function () {
  const cafes = {
    kettle:   { id: 'kettle',   name: 'Kettle & Stone',   area: 'Hayes Valley' },
    aoba:     { id: 'aoba',     name: 'Aoba Tea Bar',     area: 'Mission' },
    quiet:    { id: 'quiet',    name: 'The Quiet Cup',    area: 'Nob Hill' },
    moss:     { id: 'moss',     name: 'Mossbloom',        area: 'Outer Sunset' },
    riverstone:{ id: 'riverstone', name: 'Riverstone Matcha', area: 'North Beach' },
  };

  // swatch = the "drink color" gradient used in the photo placeholder
  const drinks = [
    {
      id: 'd-usucha', cafe: 'kettle', name: 'Ceremonial Usucha', price: 6.50,
      milk: ['none'], iced: false, hot: true,
      swatch: 'linear-gradient(160deg,#9bb36a,#6f8a44)',
      blurb: 'Single-origin Uji tencha, stone-ground and whisked thin. No milk, no sugar — just the leaf.',
      desc: 'A bowl of pure ceremonial-grade matcha, whisked to a fine foam. Vegetal, bright, and faintly sweet on the finish. For drinkers who want the green, not the latte.',
      taste: { strength: 5, sweet: 1, creamy: 1, earthy: 5, bitter: 4 },
      reviewCount: 41,
      reviews: [
        { id: 'r1', text: 'Intense and grassy in the best way. Bracingly bitter up front, then this clean sweetness shows up at the end. Zero milk so the matcha has nowhere to hide.', s:5,w:1,c:1,e:5,b:4, conf:0.93, tags:['grassy','bracing','umami'], when:'2026-05-28' },
        { id: 'r2', text: 'Real ceremonial stuff. Thick foam, deep umami, a little astringent. Not for people who like sweet drinks.', s:5,w:1,c:2,e:4,b:4, conf:0.88, tags:['umami','astringent'], when:'2026-05-19' },
      ],
    },
    {
      id: 'd-oatvanilla', cafe: 'aoba', name: 'Vanilla Oat Matcha Latte', price: 6.75,
      milk: ['oat','whole','almond'], iced: true, hot: true,
      swatch: 'linear-gradient(160deg,#cdd9a3,#a7bd7e)',
      blurb: 'Everyday iced latte — creamy oat milk, a whisper of vanilla, balanced matcha.',
      desc: 'The crowd-pleaser. Smooth oat milk rounds out a mellow ceremonial blend, with just enough vanilla to feel like a treat. Easy, creamy, never bitter.',
      taste: { strength: 3, sweet: 3, creamy: 4, earthy: 2, bitter: 1 },
      reviewCount: 88,
      reviews: [
        { id: 'r1', text: 'My daily order. Creamy without being heavy, lightly sweet, matcha is present but gentle. Oat milk is the move here.', s:3,w:3,c:4,e:2,b:1, conf:0.9, tags:['creamy','balanced','everyday'], when:'2026-06-01' },
        { id: 'r2', text: 'Soft and comforting. The vanilla is subtle, not syrupy. Wish it were a touch stronger on the matcha but very drinkable.', s:2,w:3,c:4,e:2,b:1, conf:0.85, tags:['smooth','vanilla'], when:'2026-05-22' },
      ],
    },
    {
      id: 'd-strawberry', cafe: 'moss', name: 'Strawberry Matcha Latte', price: 7.25,
      milk: ['oat','whole','coconut'], iced: true, hot: false,
      swatch: 'linear-gradient(160deg,#e7b9c2,#bcae86 60%,#9fb178)',
      blurb: 'Layered iced latte — crushed strawberry, milk, and a bright matcha float.',
      desc: 'Sweet and photogenic: a layer of macerated strawberry under cold milk and a vivid matcha pour. Fruity and creamy, with the matcha mostly along for the ride.',
      taste: { strength: 2, sweet: 5, creamy: 4, earthy: 1, bitter: 1 },
      reviewCount: 63,
      reviews: [
        { id: 'r1', text: 'Basically a dessert. Very sweet, lots of strawberry, super creamy. The matcha is faint but it looks gorgeous.', s:2,w:5,c:4,e:1,b:1, conf:0.91, tags:['sweet','fruity','dessert'], when:'2026-05-30' },
        { id: 'r2', text: 'Cute and tasty but if you want actual matcha flavor look elsewhere. Strawberry dominates.', s:1,w:5,c:4,e:1,b:1, conf:0.82, tags:['sweet','strawberry'], when:'2026-05-12' },
      ],
    },
    {
      id: 'd-tonic', cafe: 'riverstone', name: 'Matcha Espresso Tonic', price: 7.50,
      milk: ['none'], iced: true, hot: false,
      swatch: 'linear-gradient(160deg,#b7cf86,#7f9a55 70%,#5d7a3f)',
      blurb: 'Sparkling tonic, a shot of matcha, no milk — crisp, herbal, lightly bitter.',
      desc: 'A non-dairy refresher: cold tonic water cut with a concentrated matcha shot. Effervescent, herbaceous, and dry — the quinine and the leaf play off each other.',
      taste: { strength: 4, sweet: 2, creamy: 1, earthy: 4, bitter: 4 },
      reviewCount: 29,
      reviews: [
        { id: 'r1', text: 'Fizzy and clean. Pretty strong matcha, a little bitter, almost no sweetness. Super refreshing on a hot day.', s:4,w:2,c:1,e:4,b:4, conf:0.87, tags:['fizzy','herbal','refreshing'], when:'2026-05-27' },
      ],
    },
    {
      id: 'd-brownsugar', cafe: 'aoba', name: 'Brown Sugar Matcha', price: 7.00,
      milk: ['whole','oat'], iced: true, hot: false,
      swatch: 'linear-gradient(160deg,#c4cf94,#9a9a5f 55%,#9c7b4e)',
      blurb: 'Caramelized brown-sugar syrup, milk, and a bold matcha pour.',
      desc: 'Rich and indulgent — dark brown-sugar syrup streaks the cup, balanced by a bolder matcha so it never tips into cloying. Creamy, toasty, sweet.',
      taste: { strength: 3, sweet: 5, creamy: 4, earthy: 2, bitter: 2 },
      reviewCount: 54,
      reviews: [
        { id: 'r1', text: 'Toasty caramel notes, very creamy, quite sweet. The matcha holds its own against the brown sugar which I appreciated.', s:3,w:5,c:4,e:2,b:2, conf:0.89, tags:['caramel','sweet','rich'], when:'2026-05-31' },
      ],
    },
    {
      id: 'd-coconut', cafe: 'moss', name: 'Coconut Cloud Matcha', price: 6.95,
      milk: ['coconut','oat'], iced: true, hot: true,
      swatch: 'linear-gradient(160deg,#d8e0bd,#aebd8c)',
      blurb: 'Whipped coconut cream over a smooth, lightly sweet matcha.',
      desc: 'Tropical and silky. A cap of whipped coconut cream melts into a gently sweet matcha base. Dairy-free, dreamy, and very easy to drink.',
      taste: { strength: 3, sweet: 3, creamy: 5, earthy: 2, bitter: 1 },
      reviewCount: 47,
      reviews: [
        { id: 'r1', text: 'So creamy it is basically a cloud. Coconut is forward, mild sweetness, matcha is balanced and smooth. Love that it is dairy free.', s:3,w:3,c:5,e:2,b:1, conf:0.9, tags:['creamy','coconut','dairy-free'], when:'2026-05-24' },
      ],
    },
    {
      id: 'd-hojiblend', cafe: 'kettle', name: 'Toasted Hojicha-Matcha', price: 6.25,
      milk: ['oat','whole','almond'], iced: false, hot: true,
      swatch: 'linear-gradient(160deg,#b6a878,#8c7349 60%,#6f7a4a)',
      blurb: 'Roasted hojicha folded into matcha — nutty, low-bitter, cozy.',
      desc: 'A house blend of roasted hojicha and ceremonial matcha. The roast tames the bitterness and adds a toasty, almost chocolatey warmth. Low caffeine, high comfort.',
      taste: { strength: 3, sweet: 2, creamy: 3, earthy: 3, bitter: 2 },
      reviewCount: 36,
      reviews: [
        { id: 'r1', text: 'Nutty and roasty, like a campfire version of matcha. Not very sweet, low bitterness, really cozy hot. Different but great.', s:3,w:2,c:3,e:3,b:2, conf:0.86, tags:['roasted','nutty','cozy'], when:'2026-05-20' },
      ],
    },
    {
      id: 'd-yuzu', cafe: 'riverstone', name: 'Yuzu Matcha Fizz', price: 7.75,
      milk: ['none'], iced: true, hot: false,
      swatch: 'linear-gradient(160deg,#d9d785,#a9bd5e 65%,#86a44a)',
      blurb: 'Citrusy yuzu, sparkling water, bright matcha — zero dairy.',
      desc: 'Tart and lifted: Japanese yuzu meets a clean matcha shot over soda. Bright, zippy, faintly bitter, and not very sweet. A palate-waker.',
      taste: { strength: 4, sweet: 2, creamy: 1, earthy: 3, bitter: 3 },
      reviewCount: 22,
      reviews: [
        { id: 'r1', text: 'Zingy citrus and a genuinely strong matcha backbone. Light sweetness, a bit of bitter edge. Feels fancy and clean.', s:4,w:2,c:1,e:3,b:3, conf:0.84, tags:['citrus','bright','clean'], when:'2026-05-29' },
      ],
    },
    {
      id: 'd-classic', cafe: 'quiet', name: 'Classic Iced Matcha Latte', price: 5.75,
      milk: ['whole','oat','almond','coconut'], iced: true, hot: true,
      swatch: 'linear-gradient(160deg,#bcd093,#94b06a)',
      blurb: 'The reference latte — clean milk, honest matcha, nothing fancy.',
      desc: 'No syrups, no theatrics. A well-pulled matcha over cold milk, lightly sweetened. The benchmark everything else gets measured against.',
      taste: { strength: 3, sweet: 2, creamy: 3, earthy: 3, bitter: 2 },
      reviewCount: 102,
      reviews: [
        { id: 'r1', text: 'Exactly what a matcha latte should be. Balanced, clean, not too sweet, you can actually taste the matcha. Reliable every time.', s:3,w:2,c:3,e:3,b:2, conf:0.92, tags:['balanced','clean','reliable'], when:'2026-06-02' },
        { id: 'r2', text: 'Solid baseline. Medium everything. Nothing to complain about, nothing flashy.', s:3,w:2,c:3,e:2,b:2, conf:0.8, tags:['balanced'], when:'2026-05-15' },
      ],
    },
    {
      id: 'd-blacksesame', cafe: 'quiet', name: 'Black Sesame Matcha', price: 7.50,
      milk: ['oat','whole'], iced: false, hot: true,
      swatch: 'linear-gradient(160deg,#9fa978,#6d7350 55%,#4d4a40)',
      blurb: 'Toasted black sesame paste, milk, and a deep, earthy matcha.',
      desc: 'Nutty and grown-up. Stone-ground black sesame brings a savory richness against an earthy, strong matcha. Lightly sweet, deeply creamy, unusual in the best way.',
      taste: { strength: 4, sweet: 2, creamy: 4, earthy: 4, bitter: 2 },
      reviewCount: 31,
      reviews: [
        { id: 'r1', text: 'Savory, nutty, super creamy. Strong earthy matcha underneath the sesame. Barely sweet which I loved. Tastes expensive.', s:4,w:2,c:4,e:4,b:2, conf:0.88, tags:['nutty','earthy','savory'], when:'2026-05-26' },
      ],
    },
  ];

  return { cafes, drinks };
})();
