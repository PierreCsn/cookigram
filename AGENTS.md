# Directives du dépôt public de recettes CookiGram 🍳

> Dépôt officiel : https://github.com/PierreCsn/cookigram<br>
> Dépôt moteur privé : [`PierreCsn/cookigram-core`](https://github.com/PierreCsn/cookigram-core)

## Périmètre

Ce dépôt contient uniquement le corpus culinaire Gram, les données d’ingrédients et de provenance, les images, les prompts et la documentation. Le moteur de génération, le parseur et validateur complet, la PWA, le build et les tests applicatifs résident dans `cookigram-core`. Ne créez pas de code moteur ou applicatif ici et ne supposez pas que ce worktree peut construire le site seul.

La recette sourcée est la source de vérité : ne jamais inventer silencieusement une quantité, une durée, un réglage d’appareil, une compatibilité ou une donnée nutritionnelle.

## Standard des recettes `.gram`

- Une action `[Macro-action]` regroupe une phase logique ; les lignes `- ` sont les unités exécutables.
- Une puce décrit un geste ou un réglage machine. Séparez commande robot, geste manuel et cuisson.
- Regroupez au plus deux ou trois ingrédients par ajout cohérent et indiquez les découpes dans l’annotation de l’ingrédient.
- Ajoutez un état d’arrêt observable : coloration, texture, odeur ou température.
- Chaque `@ingrédient{quantité}` doit être résolu par [`.gram/ingredients.yaml`](.gram/ingredients.yaml). Toute nouvelle valeur nutritionnelle ou physique doit être sourcée dans [`.gram/ingredient-provenance.yaml`](.gram/ingredient-provenance.yaml).
- Une température `^{120 C}` exclut le TM31 ; dans ce cas, limitez `appliances.thermomix` à TM5, TM6 et TM7.

## Images

Une image finale va dans `static/images/<slug>.<ext>` et son prompt dans `image-prompts/<slug>.md`. Suivez [`generate-recipe-image`](.agents/skills/generate-recipe-image/SKILL.md) pour les métadonnées et la vérification des droits.

## Validation réellement disponible

Depuis la racine, les contrôles publics sont :

```bash
python -c "import yaml, glob; [yaml.safe_load(open(f, encoding='utf-8')) for f in glob.glob('.gram/*.yaml')]"
python scripts/audit-recipe-images.py --check
```

Le second contrôle détecte les images manquantes, les prompts manquants et les images restées sur le placeholder. La CI exécute ces contrôles pour les PR sans secret Core. Avec le secret, elle récupère le commit de `cookigram-core` indiqué par [`.core-version`](.core-version), lance `python -m generator.recipe_check --root .` et construit le site. Le workflow Pages utilise la même dépendance privée après une CI réussie.

Ne documentez pas `cookigram check`, `python -m generator...`, `npm`, `pytest` ou `ruff` comme outils disponibles localement dans ce dépôt de contenu.

## Travail d’agent

Pour un import Web, suivre [`import-recipe-gram`](.agents/skills/import-recipe-gram/SKILL.md), conserver l’URL et l’auteur de la source et signaler les incertitudes. Pour une simple correction locale, aucune recherche Web n’est requise.
