# CookiGram 🍳

[![Deploy GitHub Pages](https://github.com/PierreCsn/cookigram/actions/workflows/pages.yml/badge.svg)](https://github.com/PierreCsn/cookigram/actions/workflows/pages.yml)
[![Coverage](https://img.shields.io/badge/coverage-88%25-brightgreen.svg)](#testing-and-quality)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](pyproject.toml)
[![Gram Language](https://img.shields.io/badge/Gram-Gram%20Language-orange.svg)](https://gram-lang.org)

A modern, offline-first static recipe notebook and Progressive Web App (PWA) powered by [Gram language](https://gram-lang.org) files.

> 🌐 **Live Demo:** [https://pierrecsn.github.io/cookigram/](https://pierrecsn.github.io/cookigram/)  
> 🇫🇷 **Documentation en français :** [README.md](README.md) | 🤝 **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)

CookiGram is built on top of [Gram](https://gram-lang.org), an open-source culinary language engineered to make recipes structured, computable, and version-controllable with Git. Check out the [official Gram documentation](https://gram-lang.org/docs/) to explore the full syntax.

---

## Key Features

- 📱 **Offline-First PWA**: Installable on both mobile and desktop, works seamlessly without an active internet connection.
- 🍳 **Step-by-step Guided Cook Mode**: Distraction-free full-screen interface with checkable substeps.
- 🔍 **Instant Search & Advanced Filters**: Live filtering by title or ingredient, quick category chips (*poultry, fish, pork, stew, curry, pasta, bake, soup...*), and multi-tag advanced filters panel.
- 🎙️ **Hands-free Voice Commands**: Navigate through instructions ("*next*", "*previous*", "*timer*") using the Web Speech Recognition API without touching your screen.
- 🗣️ **Text-to-Speech (TTS)**: Built-in step audio reading using native browser voice synthesis.
- ⏱️ **Multiple Timers**: Visual countdowns with Web Audio sound alerts and local state resumption.
- 🛒 **Smart Shopping List**: Isolates pantry staples, organizes items by supermarket aisles, and exports seamlessly to **Google Keep** checkboxes.
- 📊 **Nutritional Analysis**: Automatic CIQUAL-based calculation of calories and macronutrients (proteins, carbs, fats) per serving with ingredient breakdown.
- 🧠 **LLM & AI-Powered Recipe Ingestion**: Proven methodology and agent tooling allowing Large Language Models to cleanly import web recipes and standardize them into robust, computable `.gram` format.
- 🤖 **Culinary Robot Settings (Thermomix)**: Sleek parameter badges for time, temperature, butterfly whisk, reverse mode, and blade speeds.
- 🌙 **Adaptive Dark / Light Theme**: Respects system preferences or toggles instantly with one tap.
- 🌐 **SEO & Structured Data**: Schema.org `Recipe` JSON-LD microdata, Open Graph / Twitter Cards metadata, `sitemap.xml`, `robots.txt`, and RSS feed (`feed.xml`).
- 🔒 **Screen Wake Lock**: Prevents your device display from turning off while cooking.

---

## LLM & AI-Assisted Recipe Ingestion

A cornerstone of CookiGram is its built-in architecture and methodology enabling AI agents (LLMs) to reliably import and standardize recipes from the web into clean, computable `.gram` format:

- **Dedicated Agent Skill** ([import-recipe-gram](.agents/skills/import-recipe-gram/SKILL.md)): Encapsulates extraction protocols (Gram syntax, atomic steps, appliance settings, CC-licensed imagery, and legal attributions);
- **Strict Canonical Validation** (`generator/schema.py`): Deterministic validation pipeline blocking incomplete, improperly typed, or contradictory recipes;
- **Automated Ingredient Reconciliation** (`.gram/ingredients.yaml` & `ingredient-provenance.yaml`): Alias resolution, nutrient matching, and origin verification;
- **Culinary Reliability Guardrails**: Precise units, durations, temperatures, and piece weights ready for immediate cooking execution and nutritional analysis.


---

## Quick Start & Development

```bash
# 1. Clone the repository and set up a virtual environment
git clone https://github.com/PierreCsn/cookigram.git
cd cookigram
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# 2. Install dependencies with development tools
pip install -e '.[dev]'

# 3. Build the static site
python -m generator.build

# 4. Preview locally
python -m http.server 8000 -d _site
```

Open [http://localhost:8000](http://localhost:8000) in your browser. Recipe files reside in the `recipes/` directory.

---

## Testing and Quality

CookiGram maintains a strict test suite across Python and JavaScript achieving **89% code coverage**.

> **Unified CI Environment:** Continuous integration (`ci.yml`) runs on a single **Python 3.12** runtime (aligned with Playwright E2E and GitHub Pages deployment jobs), speeding up build cycles threefold. Backward compatibility with Python 3.11+ remains strictly enforced via Ruff (`target-version = "py311"`) and Mypy (`python_version = "3.11"`).

```bash
# Python unit tests with coverage report
pytest --cov=generator --cov-report=term-missing

# JavaScript unit tests (pure functions, quantity parsing, speech normalization)
npm run test:unit

# End-to-end browser tests with Playwright (catalogue, cook mode, offline PWA)
npm run test:e2e

# Lint and check code formatting with Ruff
ruff check generator plugins tests
ruff format --check generator plugins tests

# Lint JavaScript with Biome
npm run lint

# Validate JavaScript syntax
node --check static/app.js
node --check static/sw.js
for f in static/js/modules/*.js; do node --check "$f"; done

# Validate ingredient database and provenance
pytest tests/test_ingredients_database.py
```

## Modular Frontend Architecture

The frontend is engineered with zero framework overhead, using native ES modules (`type="module"`) and clean CSS component separation:

- **JavaScript Feature Modules (`static/js/modules/`)**:
  - `utils.js`: Isolated feature initialization (`initFeature`) and toast notifications;
  - `theme.js`: Dark/light mode toggle with system preference watching, PWA install prompt, and Service Worker registration;
  - `portions.js`: Culinary quantity parsing (fractions, mixed numbers, decimals) and scaling algorithms;
  - `checklist.js`: Ingredients checklist with per-recipe and per-variant `localStorage` persistence;
  - `shopping.js`: Pantry evaluation modal, aisle categorization, staples management, and formatted Google Keep export;
  - `search.js`: Real-time normalized accent-insensitive search and multi-tag filtering;
  - `cook.js`: Step-by-step cooking wizard, interactive substeps, parallel operations, and keyboard navigation;
  - `timers.js`: Interactive cooking timers with Web Audio melodic 3-note chime synthesis;
  - `voice.js`: Natural text-to-speech reading (`SpeechSynthesis`), hands-free voice commands (`SpeechRecognition`), and screen Wake Lock;
  - `variants.js`: Seamless recipe variant switching and URL state synchronization.

- **Component-Level CSS (`static/css/`)**:
  - Cleanly separated into maintainable domain files (`variables.css`, `base.css`, `topbar.css`, `catalogue.css`, `recipe.css`, `ingredients.css`, `modal.css`, `cook.css`, `timers.css`, `thermomix.css`);
  - Automatically concatenated at build time into `output/assets/app.css` to avoid multiple HTTP requests in production.

- **Shared Jinja Macros (`templates/macros.html`)**:
  - Centralized badges for Thermomix models and appliance icons (`tmx_badge`, `appliance_tags`).


## Recipe image skill

The workspace skill at `.agents/skills/generate-recipe-image/` defines
CookiGram's approved visual identity: warm, semi-realistic manga culinary
illustrations in a responsive landscape format. It prevents unlicensed source
photographs from being used as generation references, distinguishes previews
from approved repository replacements, and records the provider, prompt and
human selection. Gemini CLI discovers `.agents/skills/` directly; run
`/skills reload` after adding or changing a skill.

## Appliance declarations and validation

Keep source compatibility separate from CookiGram's documented support:

```yaml
appliances:
  thermomix: [TM31, TM5, TM6, TM7]
source_appliances:
  thermomix: [TM5, TM6, TM7]
required_equipment:
  - Thermomix TM31, TM5, TM6 or TM7
  - Varoma with steaming tray
appliance_validation:
  TM31:
    status: human-tested
    portions: 6
    note: Six-serving version tested by the project owner on a TM31.
```

Only record `human-tested` after an explicit report, and include the yield that
was actually tested.

## Continuous Integration (CI) & GitHub Pages

Configure **Settings → Pages → Source** to use **GitHub Actions**. Every pull request and push to
`main` triggers the CI workflow (`ci.yml`) running tests and Playwright on Python 3.12 and Node.js 22. Pages deploys the exact tested commit only after all CI checks succeed.

The generated, versioned service worker pre-caches the catalogue,
`recipes.json`, every recipe and cook page, frontend assets, and recipe images.
After the first complete visit, all 23 recipes remain available in airplane
mode. HTML navigation is network-first with an offline cache fallback; static
assets are cache-first, and stale versioned caches are removed on activation.

## 🗺️ Product Roadmap & Maturity Milestones (Kitchen OS)

CookiGram aims to be the **Kitchen Operating System (Kitchen OS)**. Development is structured around major user experience milestones:

| Milestone | Name | Status | Cook Experience & Value |
| :--- | :--- | :---: | :--- |
| **v1** | **Recipe OS** | ✅ **Shipped** | **Deterministic foundation**: Canonical `.gram` recipes, exact mathematical portion scaling, traceable ANSES/CIQUAL nutrition, instant search, and 100% offline functionality. |
| **v2** | **Cooking Copilot** | 🔶 **Active Sprint** | **Countertop copilot**: Full-screen cook mode readable from 1 meter, persistent countdown timers with Web Audio alerts, hands-free voice commands, sensory flavor profiles, and utensil recognition. |
| **v3** | **Kitchen Scheduler** | ⏳ *Next Horizon* | **Multi-dish orchestration**: Constraint-based mathematical scheduler (Google OR-Tools CP-SAT solver). Automatically synchronizes oven, stovetop, and robot so all courses are ready together without stress ([Issue #51](https://github.com/PierreCsn/cookigram/issues/51)). |
| **v4** | **Smart Meal Planner** | ⏳ *Planned* | **Zero mental fatigue**: Weekly meal planning, ingredient consolidation, aisle-sorted shopping lists, and export to note apps. |
| **v5+** | **Kitchen Intelligence** | ⏳ *Exploration* | **Pragmatic pantry & Local-First**: Smart recipe suggestions based on fridge leftovers, local personalization, and privacy-first architecture. |

---

## License & Third-Party Media

This project is licensed under the [MIT License](LICENSE).  
Recipe photography and media in `static/images/` are licensed under their respective terms (such as Creative Commons CC BY-SA 4.0). Detailed photographer credits, source links, and modifications are declared in each recipe's `.gram` frontmatter.
