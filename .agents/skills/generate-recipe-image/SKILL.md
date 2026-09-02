---
name: generate-recipe-image
description: Create, replace, or review original CookiGram recipe illustrations from `.gram` recipes in the approved manga culinary style. Use for recipe images and catalogue visual consistency; do not use for logos, interface icons, or unrelated graphics.
---

# Generate a CookiGram recipe image

Create an original illustration that accurately represents a CookiGram recipe
without reproducing a photograph from its source. Read
[the CookiGram image style](references/cookigram-image-style.md) before writing
the prompt or generating an image.

## Establish the source of truth

Pull the repository with `git pull --ff-only` before making project changes,
then read the complete `.gram` recipe. Derive the subject from its title,
description, ingredients, preparation and final presentation. Do not infer a
visible garnish, accompaniment, branded appliance or serving vessel that the
recipe does not support.

For an image replacing third-party media, do not pass the existing photograph
to an image model, trace it, or imitate its composition. Generate from the
written culinary facts only. A user-provided image may be used as a reference
only when the user owns it or explicitly confirms sufficient reuse rights.

## Generate and review

Use an available image-generation capability. If the current agent cannot
generate an image, produce the final structured prompt and clearly report that
no asset was created; do not insert a placeholder or claim success.

Generate a landscape 16:9 draft suitable for responsive recipe cards. Review
the actual output before proposing it:

- the dish remains immediately identifiable and matches its key ingredients;
- the approved manga culinary treatment is visible without copying a named
  artist, studio, series or existing artwork;
- the useful subject survives both wide and tighter mobile crops;
- there is no text, watermark, logo, branded packaging or implausible utensil;
- hands, faces and characters are absent unless the user explicitly requests
  them;
- common generation defects do not make the food or serving dish impossible.

If a draft misses one of these points, iterate with one focused correction.

## Preview versus repository change

A request for a test or draft authorizes a preview only. Do not change the
recipe or overwrite its current image until the user approves the selected
illustration or explicitly asks for replacement.

For an approved project image:

1. save an optimized web asset under `static/images/` with a lowercase
   kebab-case name derived from the recipe slug;
2. update the recipe's `image` path;
3. replace third-party credit fields with factual generation metadata;
4. never label generated media `CC0`, Creative Commons, public domain or MIT
   unless a human has deliberately made and documented that legal decision;
5. when an old image is being replaced, remove it only when the user's request
   authorizes replacement and no recipe still references it.

Use this frontmatter shape, adapting the provider and terms URL to the tool
actually used:

```yaml
image: images/recipe-slug.webp
image_credit:
  author: CookiGram
  source: https://github.com/PierreCsn/cookigram
  license: Illustration générée par IA pour CookiGram
  license_url: https://example.com/provider-terms
  modifications: Illustration sélectionnée et intégrée par un humain.
image_generation:
  provider: Provider name
  model: Model name if known
  generated_at: YYYY-MM-DD
  prompt_file: image-prompts/recipe-slug.md
```

Save the final prompt and any material human art-direction notes in the declared
`image-prompts/<slug>.md`. Do not put prompt files in `static/images/`, whose
contents are validated as published recipe images.

## Validate

Check the final dimensions, aspect ratio and file weight. From the repository
root, run:

```bash
python -m pytest -q
python -m generator.build
```

Inspect the generated catalogue and recipe page when possible. Commit and push
only when the user authorizes repository publication. Pull again before
publishing if another agent may have updated `main`.
