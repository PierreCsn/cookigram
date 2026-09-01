---
name: import-recipe-gram
description: Research a recipe on the web and add or improve a sourced `.gram` recipe in CookGram. Use when an agent is asked to import, adapt, translate, or create a recipe from an online page or video; do not use for purely local recipe edits that need no external research.
---

# Import a web recipe into CookGram

Produce a practical, traceable recipe in `recipes/` that compiles with the current CookGram generator. Preserve the culinary facts while rewriting the directions concisely; do not copy a source's introduction, anecdotes, photographs, or distinctive prose.

## Research

Browse the web because recipe contents and URLs are external facts. Prefer, in order:

1. the original author or publisher;
2. an authoritative manufacturer or culinary institution for appliance-specific methods;
3. a complete recipe page exposing Schema.org `Recipe` data;
4. a video only when it gives enough quantities and timings.

Use one primary source. Consult another reliable source when the primary source omits a safety-critical temperature, pressure-release method, doneness criterion, or other information needed to cook safely. Never silently invent a missing quantity or duration: leave it unquantified, mark the uncertainty in `description`, or ask the user when it materially affects the result.

Record the exact primary URL in frontmatter as `source:` and the displayed author or channel as `author:`. Do not invent an author. Keep a short source note in the final response.

## Convert

Read [CookGram Gram profile](references/cookgram-gram-profile.md) before writing or modifying a recipe.

When the official Gram CLI is installed and configured, prefer its structured importer for a compatible page or YouTube URL:

```bash
gram import "SOURCE_URL" -o recipes/slug.gram
```

Review the output rather than accepting it blindly. Otherwise convert manually from the researched facts. Normalize the result to French unless the user requests another language.

Make each actionable paragraph one Gram step. Ensure that:

- every ingredient first appears with its total useful quantity;
- preparation details such as “émincé” or “à température ambiante” remain explicit;
- timers and temperatures are annotations, not prose-only values;
- equipment is annotated where it changes the method;
- doneness cues accompany timing when timing alone is unreliable;
- appliance instructions name the compatible model or capability without pretending to control the device.

Choose a lowercase kebab-case filename. Do not overwrite a similarly named recipe until its identity and intended replacement are clear.

## Validate

Run the repository checks from its root:

```bash
python -m pytest -q
python -m generator.build
```

If the official CLI is available, also run:

```bash
gram check recipes/<slug>.gram --skip-db
```

Fix parser or build errors before handing off. Inspect the generated recipe page and `recipes.json` when the change uses a new syntax construct. Do not commit or push unless the user's request authorizes repository changes.
