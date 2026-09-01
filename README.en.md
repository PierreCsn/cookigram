# CookiGram 🍳

[![CI](https://github.com/PierreCsn/cookigram/actions/workflows/ci.yml/badge.svg)](https://github.com/PierreCsn/cookigram/actions/workflows/ci.yml)
[![Deploy GitHub Pages](https://github.com/PierreCsn/cookigram/actions/workflows/pages.yml/badge.svg)](https://pierrecsn.github.io/cookigram/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](pyproject.toml)
[![Gram Language](https://img.shields.io/badge/Gram-Gram%20Language-orange.svg)](https://gram-lang.org)

A modern, offline-first static recipe notebook and Progressive Web App (PWA) powered by [Gram language](https://gram-lang.org) files.

> 🌐 **Live Demo:** [https://pierrecsn.github.io/cookigram/](https://pierrecsn.github.io/cookigram/)  
> 🇫🇷 **Documentation en français :** [README.md](README.md) | 🤝 **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)

CookiGram is built on top of [Gram](https://gram-lang.org), an open-source culinary language engineered to make recipes structured, computable, and version-controllable with Git. Check out the [official Gram documentation](https://gram-lang.org/docs/) to explore the full syntax.

---

## Key Features

- 📱 **Offline-First PWA**: Installable on both mobile and desktop, works seamlessly without an active internet connection.
- 🍳 **Step-by-step Guided Cook Mode**: Distraction-free full-screen interface with checkable substeps.
- 🎙️ **Hands-free Voice Commands**: Navigate through instructions ("*next*", "*previous*", "*timer*") using the Web Speech Recognition API without touching your screen.
- 🗣️ **Text-to-Speech (TTS)**: Built-in step audio reading using native browser voice synthesis.
- ⏱️ **Multiple Timers**: Visual countdowns with Web Audio sound alerts and local state resumption.
- 🛒 **Smart Shopping List**: Isolates pantry staples, organizes items by supermarket aisles, and exports seamlessly to **Google Keep** checkboxes.
- 📊 **Nutritional Analysis**: Automatic CIQUAL-based calculation of calories and macronutrients (proteins, carbs, fats) per serving with ingredient breakdown.
- 🤖 **Culinary Robot Settings (Thermomix)**: Sleek parameter badges for time, temperature, reverse mode, and blade speeds.
- 🌙 **Adaptive Dark / Light Theme**: Respects system preferences or toggles instantly with one tap.
- 🔒 **Screen Wake Lock**: Prevents your device display from turning off while cooking.

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

# 3. Run test suite with coverage and code linter
pytest --cov=generator
ruff check generator tests

# 4. Build the static site
python -m generator.build

# 5. Preview locally
python -m http.server 8000 -d _site
```

Open [http://localhost:8000](http://localhost:8000) in your browser. Recipe files reside in the `recipes/` directory.

---

## License & Third-Party Media

This project is licensed under the [MIT License](LICENSE).  
Recipe photography and media in `static/images/` are licensed under their respective terms (such as Creative Commons CC BY-SA 4.0). Detailed photographer credits, source links, and modifications are declared in each recipe's `.gram` frontmatter.
