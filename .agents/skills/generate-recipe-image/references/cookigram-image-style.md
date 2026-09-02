# CookiGram image style

## Art direction

CookiGram uses warm, contemporary manga-inspired culinary illustrations. Food
must remain believable and appetizing: elegant fine ink contours, hand-painted
watercolour texture and soft cel shading, with enough detail to recognize the
recipe. This is a generic visual language, never an imitation of a named artist,
studio, manga, anime or existing image.

The approved balance is **semi-realistic food with manga illustration
rendering**, not photorealism and not a comic scene.

## Composition

- Landscape 16:9, designed for both desktop heroes and mobile card crops.
- Three-quarter view around 45 degrees by default; use top-down only when it
  explains the dish better.
- Main dish centred with generous safe margins.
- Simple, softly suggested home-kitchen tabletop.
- Warm natural light and a welcoming everyday-cooking mood.
- No text, letters, watermark, logo, people or branded packaging.

Prefer colours that come from the food. Keep the background quieter than the
dish. Garnishes must appear in the recipe or be removed.

## Prompt template

```text
Use case: illustration-story
Asset type: horizontal 16:9 hero illustration for a responsive recipe website
Primary request: Create an entirely original manga-inspired culinary
illustration of "<recipe title>" based only on this written dish description,
not on any existing photograph.
Scene/backdrop: A simple warm home-kitchen tabletop, softly suggested and
uncluttered.
Subject: <faithful description of the cooked dish, visible layers/components,
texture and only recipe-supported garnish>.
Style/medium: polished contemporary manga food illustration, elegant fine ink
contours, hand-painted watercolour and soft cel shading, appetizing but
believable food textures, a distinctive original CookiGram visual identity;
generic manga aesthetic, not imitating any named artist, studio, series or
existing artwork.
Composition/framing: landscape 16:9, three-quarter view at about 45 degrees,
dish centred with safe crop margins for mobile and desktop cards, no human
figures.
Lighting/mood: warm late-afternoon kitchen light, welcoming and homely.
Colour palette: <colours derived from the recipe>.
Constraints: visually faithful to the recipe; fully original composition;
suitable as a website recipe illustration.
Avoid: text, letters, logos, brand marks, watermarks, product packaging,
characters, faces, third-party image imitation, photorealism.
```

Replace the variables with facts from the `.gram` file. Do not include the
source site's photograph or describe its layout.

## Acceptance checklist

Approve an image only if all answers are yes:

1. Would someone recognize the intended dish without reading its title?
2. Are the defining ingredients and cooking result visually plausible?
3. Is the composition original and independent from third-party photography?
4. Does the image still work after a central mobile crop?
5. Is it free of text, brands, watermarks and anatomy/rendering defects?
6. Does it look consistent with a warm CookiGram manga cookbook?
