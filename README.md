# CookGram

Carnet de recettes statique et installable, généré depuis des fichiers `.gram`.

**Site : [pierrecsn.github.io/cookigram](https://pierrecsn.github.io/cookigram/)**

## Fonctionnalités du MVP

- catalogue responsive ;
- fiche recette et mode cuisson étape par étape ;
- minuteurs, reprise locale et maintien de l'écran allumé ;
- PWA avec cache hors ligne ;
- enrichissement build-time par plugins ;
- déploiement automatique sur GitHub Pages.

## Développement

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
python -m generator.build
python -m http.server 8000 -d _site
```

Ouvrir `http://localhost:8000`. Les recettes sont dans `recipes/`.

## Ajouter une recette

Créer un fichier `.gram` avec un frontmatter et une instruction par paragraphe :

```gram
---
title: Ma recette
portions: 4
tags: [rapide]
---

[Cuire] Cuire les @pommes de terre{800 g} au #four{} pendant ~{35 min} à ^{190 C}.
```

Le générateur utilise un modèle canonique interne. L'adaptateur Gram du MVP
prend en charge actions, ingrédients, matériel, minuteurs et températures. Son
remplacement futur par le compilateur officiel ne modifiera ni les templates ni
les plugins.

## GitHub Pages

Dans le dépôt GitHub, ouvrir **Settings → Pages → Source** et sélectionner
**GitHub Actions**. Chaque push sur `main` reconstruit et publie le site.
