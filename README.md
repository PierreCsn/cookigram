# CookGram

Carnet de recettes statique et installable, généré depuis des fichiers `.gram`.

Le projet utilise [Gram](https://gram-lang.org/fr/), un langage open source
conçu pour écrire des recettes structurées, calculables et versionnables avec
Git. Consultez la [documentation officielle de Gram](https://gram-lang.org/fr/docs/)
pour découvrir la syntaxe complète et son CLI.

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

## Base d'ingrédients Gram

La base locale se trouve dans `.gram/ingredients.yaml`. Après l'ajout d'une
recette, la maintenir avec le CLI officiel :

```bash
gram db sync
gram db lint
gram db enrich
gram db validate --strict
```

Les densités et données nutritionnelles proposées par `gram db enrich` doivent
être relues avant d'être conservées.

La provenance et le niveau de confiance sont suivis dans
`.gram/ingredient-provenance.yaml`. CIQUAL/ANSES est privilégié pour les
aliments génériques français ; Open Food Facts sert aux produits de marque.
Une valeur choisie par un humain peut être marquée `manual` et `locked: true`
afin qu'aucun agent ne la remplace automatiquement.

## Ajuster le nombre de portions

Chaque recette déclare ses règles dans son frontmatter :

```yaml
portions: 4
scaling:
  enabled: true
  min_portions: 2
  max_portions: 8
  step: 1
  note: Les temps de cuisson ne sont pas recalculés.
```

Pour une recette précise qui ne peut pas être redimensionnée :

```yaml
scaling:
  enabled: false
  reason: Quantités calibrées pour le bol et le programme du Thermomix TM31.
```

La PWA recalcule les quantités numériques et mémorise le choix sur l'appareil.
Les temps et températures ne sont jamais ajustés silencieusement.

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
