# Guide de contribution à CookiGram 🍳

Merci de vous intéresser à CookiGram ! Ce projet vise à proposer un carnet de recettes moderne, résilient, offline-first et respectueux de la vie privée, propulsé par le langage culinaire [Gram](https://gram-lang.org).

---

## Architecture du projet

```
cookigram/
├── recipes/                  # Recettes au format .gram
├── generator/                # Générateur statique Python
│   ├── gram.py              # Parseur et modèle canonique
│   ├── build.py             # Script de génération du site
│   ├── nutrition.py         # Calculs caloriques & macronutriments
│   ├── shopping.py          # Évaluation intelligente de liste de courses
│   ├── plugins.py           # Chargeur d'extensions
│   └── models.py            # Dataclasses
├── templates/                # Templates HTML (Jinja2)
├── static/                   # Assets Web (CSS, JS, Service Worker, images)
│   ├── app.css              # Styles (Light / Dark, PWA, mobile-friendly)
│   ├── app.js               # Logique PWA, commande vocale, Keep, synthèse vocale
│   ├── sw.js                # Service Worker pour usage 100% hors-ligne
│   └── images/              # Photographies optimisées (< 200 Ko)
├── plugins/                  # Plugins de recettes (ex: thermomix_settings.py)
├── .gram/                    # Base de données nutritionnelle CIQUAL
│   ├── ingredients.yaml     # Valeurs nutritionnelles (100 g)
│   └── ingredient-provenance.yaml # Source et niveau de confiance
└── tests/                    # Tests unitaires et d'intégration (Pytest)
```

---

## Ajouter ou modifier une recette

### 1. Fichier `.gram`
Placez votre recette dans `recipes/<slug>.gram` avec un frontmatter YAML :

```yaml
---
title: Risotto crémeux aux champignons
portions: 4
prep_time: 15 min
total_time: 40 min
tags: [italien, réconfort, automne]
source: https://example.com/ma-recette
author: Nom de l'auteur
scaling:
  enabled: true
  min_portions: 2
  max_portions: 8
  step: 1
  note: Les temps de cuisson restent inchangés.
image: images/mon-risotto.jpg
image_credit:
  author: Photographe
  source: https://example.com/photo
  license: CC BY-SA 4.0
  license_url: https://creativecommons.org/licenses/by-sa/4.0/
  modifications: Recadrée et optimisée pour le web.
---
```

### 2. Instructions et sous-étapes
Chaque étape commence par un paragraphe décrivant l'action :
```
[Râper le parmesan]
- Mettre le @parmesan{60 g, coupé en morceaux} dans le #bol Thermomix{}.
- Pulvériser ~{10 s} à vitesse 10.
- Réserver dans un bol.
```

Balises supportées :
- `@nom de l'ingrédient{quantité, préparation}`
- `#équipement{}`
- `~{durée}` (ex: `~{15 min}`, `~{30 s}`)
- `^{température}` (ex: `^{180 C}`, `^{100 C}`)
- `- sous-étape` (crée une sous-étape cochable en mode pas-à-pas)

### 3. Référencement des ingrédients (Nutrition CIQUAL)
Chaque ingrédient déclaré avec `@nom` doit être documenté dans `.gram/ingredients.yaml` et `.gram/ingredient-provenance.yaml` pour alimenter le calcul nutritionnel et la liste de courses.

---

## Environnement de développement

### 1. Installation
```bash
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate sous Windows
pip install -e .[dev]
```

### 2. Lancer les tests et le linter
```bash
# Vérifier le code avec Ruff
ruff check generator tests
ruff format --check generator tests

# Exécuter les tests avec couverture
pytest --cov=generator

# Construire le site localement
python -m generator.build

# Prévisualiser dans votre navigateur
python -m http.server 8000 -d _site
```

---

## Règles pour les images et licences
- Ne soumettez jamais d'images sans mention d'auteur et licence explicite.
- Privilégiez les formats compressés JPEG ou WebP, dimensions recommandées ~1200x800px, poids inférieur à 200 Ko.
- Renseignez systématiquement le bloc `image_credit` dans le frontmatter.

---

## Règle de validation et de versionnement Git

Tout travail achevé doit être systématiquement validé, commité et poussé (`git push`) :
1. Valider le code et les tests (`pytest`, `npm test`, `ruff check generator tests`, `npm run lint`).
2. Vérifier que la génération du site fonctionne sans erreur : `python -m generator.build`.
3. Stager les modifications avec `git add`.
4. Créer un commit clair et précis avec `git commit -m "..."`.
5. Pousser sur la branche distante avec `git push`.
6. Vérifier que l'arbre de travail est propre (`nothing to commit, working tree clean`).

