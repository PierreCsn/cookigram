# CookGram Gram profile

CookGram currently reads the following stable subset of Gram. Stay within this profile unless the generator is extended in the same change.

## Frontmatter

```gram
---
title: Poulet rôti au citron
portions: 4
description: Poulet doré, jus court au citron et à l'ail.
tags: [poulet, four, familial]
source: https://example.org/recipe
author: Nom affiché sur la source
scaling:
  enabled: true
  min_portions: 2
  max_portions: 8
  step: 1
  note: Les temps de cuisson ne sont pas recalculés.
---
```

Required for a well-finished recipe: `title`, `portions`, `description`, and `tags`. Add `source` and `author` for an Internet import. Omit `author` when the source does not identify one.

Every recipe must also declare scaling. For a fixed appliance recipe:

```yaml
scaling:
  enabled: false
  reason: "Quantités calibrées pour le bol du Thermomix TM31 ; volume et chauffe non validés à une autre échelle."
```

## Steps, actions and sub-steps

Each line beginning with `[Action]` becomes one guided cooking step:

```gram
[Préchauffer] Préchauffer le #four{} à ^{180 C}.
```

Use a short imperative action label. Keep one main operation per step so that mobile cooking mode remains clear.

### Sub-steps (Sous-étapes interactives)

When a step involves several sequential gestures or ingredients to combine, decompose it with bullet lines (`- `):

```gram
[Préparer le panier]
- Verser l'@eau{800 g} et le @sel{1 c. à café} dans le #bol Thermomix{}.
- Peser le @riz basmati{200 g} dans le #panier cuisson{}.
- Insérer le panier dans le bol et fermer le couvercle.
```

CookGram renders sub-steps as interactive checklists in Cook Mode, allowing cooks to tick them off on their screen or validate them hands-free with the voice command *« Validé »* / *« Fait »* before advancing to the next step. Annotations (`@ingredient{}`, `#equipment{}`, `~{timer}`, `^{temperature}`) are fully supported on sub-step lines.

## Ingredients

```gram
@pommes de terre{800 g}
@œufs{3}
@sel{}
```

The first use should carry the useful quantity. An empty quantity means “au goût” or “quantité non fournie”, never a guessed value. Repeat an ingredient later without inventing an additional quantity.

## Equipment

```gram
#four{}
#cocotte{}
#Thermomix TM31{}
```

Annotate equipment when it is required or affects instructions. Ordinary utensils need not all be listed.

## Timers

CookGram recognizes seconds, minutes, and hours:

```gram
~{30 s}
~{8 min}
~{2 h}
```

Put the timer in the step that starts it. Prefer `min` over ambiguous abbreviations in new files.

## Temperatures

```gram
^{180 C}
^{63 C à cœur}
```

Use the value and meaning supplied by the source. For food safety, distinguish oven temperature from internal temperature.

## Thermomix and Cookomix conventions

For Thermomix recipes, declare the appliance in frontmatter:
```yaml
appliances:
  thermomix: [TM31, TM5, TM6]
source_appliances:
  thermomix: [TM5, TM6]
required_equipment:
  - Thermomix TM31, TM5 ou TM6
  - Varoma
tags: [..., thermomix]
```

`source_appliances` is the compatibility stated by the imported source;
`appliances` is CookiGram's supported set after any documented adaptations.
`required_equipment` is displayed before cooking. A model may be marked as
tested only after an explicit human report:

```yaml
appliance_validation:
  TM31:
    status: human-tested
    portions: 6
    note: Version 6 portions testée par le propriétaire du projet sur un TM31.
```

Do not invent a human validation or apply it to untested yields.

When formulating steps, specify:
- **Durée** : `~{10 s}`, `~{4 min}`, `~{16 min}`
- **Température** : `^{100 C}`, `^{120 C}`, `Varoma`
- **Sens inverse** : mentionner `sens inverse`
- **Vitesse** : `vitesse cuillère` (ou `vitesse mijotage`), `vitesse 1` à `10`, `turbo`, `pétrin`
- **Accessoires** : `#bol Thermomix{}`, `#gobelet doseur{}`, `#panier cuisson{}`, `#Varoma{}`, `#fouet papillon{}`, `#spatule{}`

CookGram automatically detects these parameters and displays a Cookomix-style badge with SVG icons:
- ⏱ Minuteur (chronomètre)
- 🌡 Température / Varoma (thermomètre)
- 🔄 Sens inverse (flèche circulaire antihoraire)
- 🥄 Vitesse cuillère (icône cuillère de mijotage)
- 🔪 Vitesse lames (icône lames de mixage)

## Complete example

```gram
---
title: Pommes de terre rôties
portions: 4
description: Quartiers croustillants et fondants.
tags: [accompagnement, four]
source: https://example.org/pommes-de-terre
---

## Pommes de terre rôties

[Préchauffer] Préchauffer le #four{} à ^{200 C}.

[Assaisonner] Mélanger les @pommes de terre{800 g} en quartiers avec l'@huile d'olive{2 c. à soupe} et le @sel{}.

[Rôtir] Étaler sur une #plaque{} et cuire ~{35 min}, en retournant à mi-cuisson, jusqu'à ce que les quartiers soient dorés et tendres.
```

## Current compatibility boundary

The official Gram language supports more constructs than CookGram's MVP parser. In particular, treat modules, intermediate variables, relative quantities, named timers, composite ingredients, and advanced calculations as unsupported unless the generator and its tests are updated together.

## Ingredient database matching

Before writing an `@ingredient{}`, inspect `.gram/ingredients.yaml`. Prefer the canonical French name already present in the database. Matching must consider:

- the YAML key, such as `magret-de-canard`;
- `name`, such as `Magret de canard`;
- every string in `aliases`.

For a missing ingredient, add a minimal entry alongside the recipe:

```yaml
ingredients:
  huile-olive:
    name: "Huile d'olive"
    aliases: ["huile d’olive"]
    category: "Huiles et matières grasses"
```

Do not add estimated `physical` or `nutrition` blocks merely to make the database look complete.
