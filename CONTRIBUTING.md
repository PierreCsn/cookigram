# Guide de Contribution à CookiGram 🍳

Merci de vous intéresser à CookiGram ! Ce projet vise à proposer un carnet de recettes moderne, résilient, offline-first et respectueux de la vie privée, propulsé par le langage culinaire [Gram](https://gram-lang.org).

---

## 1. Deux Dépôts Découplés (PDR-0008)

L'écosystème CookiGram s'articule en deux dépôts :
* **`PierreCsn/cookigram` (Ce dépôt — Public) :** Le carnet de recettes vivant, les photographies culinaires et la base de données nutritionnelle CIQUAL. C'est ici que sont accueillies toutes les contributions de recettes (par des humains ou des agents d'IA).
* **`PierreCsn/cookigram-core` (Privé) :** Le moteur logiciel Kitchen OS, l'application frontend PWA, les solveurs d'ordonnancement (CP-SAT) et la suite de tests E2E.

---

## 2. Contribuer une Recette (Workflow en 3 étapes)

La contribution d'une recette est rapide, déterministe et validée en moins de 2 secondes.

### Étape 1 : Créer le fichier `.gram` dans `recipes/`
Placez votre recette dans `recipes/<slug>.gram` avec son frontmatter YAML obligatoire :

```yaml
---
title: Risotto crémeux aux champignons
portions: 4
prep_time: 15 min
total_time: 40 min
spiciness: 0
scaling:
  default_portions: 4
  min_portions: 1
  max_portions: 12
tags: [italien, réconfort, automne]
source: https://example.com/recette
author: Chef Pierre
description: Un risotto fondant parfumé aux champignons de Paris et parmesan.
---

[Préparer les ingrédients]
- Émincer @oignon{1} et @gousses d'ail{2}.
- Nettoyer et couper @champignons de Paris{300 g} en lamelles.

[Cuisson du risotto]
- Faire suer l'oignon dans #casserole{} avec @huile d'olive{2 c. à soupe} pendant ~{5 min}.
- Ajouter le @riz arborio{320 g} et nacrer ~{2 min}.
- Mouiller progressivement avec @bouillon de légumes{1 l} chaud en remuant ~{18 min}.
- Hors du feu, incorporer @parmesan râpé{60 g} et @beurre{30 g}.
```

### Étape 2 : Vérifier les ingrédients
Si votre recette introduit de nouveaux ingrédients :
1. Déclarez leurs valeurs nutritionnelles dans [`.gram/ingredients.yaml`](.gram/ingredients.yaml).
2. Déclarez leur source et niveau de confiance dans [`.gram/ingredient-provenance.yaml`](.gram/ingredient-provenance.yaml).

### Étape 3 : Contrôler la conformité en local (< 2 s)
Exécutez le validateur atomique :

```bash
python -m generator.recipe_check recipes/<slug>.gram
```

Si le terminal affiche `✅ CONFORME`, votre recette respecte 100 % du contrat de données CookiGram.

### Image de la recette
* Si vous disposez d'une photographie (format 16:9, ratio recommandé 1280x720, < 200 Ko), déposez-la dans `static/images/<slug>.jpg`.
* Si vous n'avez pas encore d'image, le validateur accepte le visuel par défaut système (`static/images/placeholder-recipe.jpg`).

---

## 3. Contribution par un Agent d'IA (Agent-Native)

CookiGram est conçu pour accueillir les contributions automatisées via Coding Agents (GitHub Copilot Workspace, Claude Code, Cursor, Devin...) :
1. Créez une issue via le formulaire dédié : **[Demande d'importation de recette](.github/ISSUE_TEMPLATE/recipe_request.md)**.
2. L'agent génère le fichier `.gram` en s'appuyant sur la compétence culinaire [`import-recipe-gram`](.agents/skills/import-recipe-gram/SKILL.md).
3. L'agent exécute `python -m generator.recipe_check recipes/<slug>.gram` avant de soumettre la Pull Request.
4. La CI GitHub Actions valide la conformité en moins de 15 secondes.
