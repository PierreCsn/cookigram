# CookiGram Ingredient Icon Style & Prompt Guide

## Purpose

CookiGram uses warm, contemporary manga-inspired culinary spot icons (stickers) for key ingredients in recipe checklists, shopping modals, and in-step cooking cards.

## Art direction & Scale

- **Scale of display**: 24×24 px (standard) to 32×32 px (cooking mode).
- **Format**: Clean SVG or WebP 64×64 px @2x (< 2 KB), transparent background.
- **Graphic treatment**:
  - Clear, instantly recognizable silhouette.
  - Distinct, dark, fine ink outline (no blurry edges).
  - Restricted palette of 2–3 vibrant, warm colors natural to the food item.
  - Soft cel-shading: one clear highlight, one soft shadow.
  - **NO micro-textures, complex gradients, or photorealism** that turns into a muddy blob at 24 px.
  - Centered within a square viewBox (`0 0 32 32`), with comfortable margins.

## Prompt template for Codex / Image Generation

```text
Asset type: single isolated culinary spot icon / sticker for recipe ingredient
Subject: <ingredient name, e.g. fresh yellow onion / peeled garlic clove / slice of butter>
Style/medium: clean contemporary Japanese manga food illustration, fine crisp ink outline, warm appetizing colors, soft cel shading, flat clean look, minimalist sticker design; not photorealistic, not 3D render.
Composition: centered single food item on pure transparent background, no shadow beneath, comfortable padding within square framing, highly legible when scaled down to 24x24 pixels.
Avoid: text, letters, watermarks, dish, plate, utensil, packaging, multiple items, complex background, blurry gradients, 3D emoji look.
```

## Approved File Location & Naming

Save approved assets under:
`static/icons/ingredients/<ingredient_id>.svg` (or `.webp`)

Where `<ingredient_id>` exactly matches the canonical key in `.gram/ingredients.yaml` (e.g. `oignon`, `ail`, `huile_olive`, `beurre`, `sel`, `parmesan`, `saumon`, `poulet`).
