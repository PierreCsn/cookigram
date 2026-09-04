---
name: 🍲 Proposer ou importer une recette
about: Proposez une recette depuis un lien web ou un texte (un agent s'occupe de la conversion)
title: '[Recette] '
labels: ['recette', 'contenu']
assignees: ''
---

### 🔗 Source de la recette (Obligatoire)
<!-- Collez ici l'URL (Marmiton, Cookomix, blog, vidéo...) OU collez directement le texte brut de la recette -->


### ✍️ Remarques ou préférences (Facultatif)
<!-- Exemples :
- « Version traditionnelle sans Thermomix pour 4 personnes »
- « Remplacer les lardons par du tofu fumé »
- « Ajuster pour 6 personnes au lieu de 4 »
-->


<!-- ======================================================================= -->
<!-- DIRECTIVES POUR L'AGENT IA (CODING AGENT / WORKSPACE AGENT)             -->
<!-- ======================================================================= -->
<!--
AGENT_DIRECTIVE:
1. Objectif : Importer cette recette dans CookiGram au format canonique Gram (.gram).
2. Directives culinaires :
   - Consulter impérativement .agents/skills/import-recipe-gram/SKILL.md.
   - Créer recipes/<slug>.gram en respectant PDR-0005 (6 à 10 macro-étapes, sous-étapes interactives `- `).
   - Renseigner frontmatter complet (prep_time, total_time distincts, spiciness 0..5, scaling, flavors, source, author).
   - Vérifier et synchroniser .gram/ingredients.yaml et .gram/ingredient-provenance.yaml.
   - Déclarer l'image :
     - Si aucune image HD n'est générée immédiatement, utiliser `image: images/placeholder-recipe.jpg`
       avec image_credit (author: CookiGram, source: https://github.com/PierreCsn/cookigram, license: Illustration temporaire).
     - Rédiger le prompt de génération dans `image-prompts/<slug>.md`.
3. Validation automatique obligatoire avant PR :
   `python -m generator.recipe_check recipes/<slug>.gram`
4. Soumission :
   - Créer une branche isolée `recipe/<slug>`.
   - Produire un commit conventionnel propre `feat(recipes): ajouter <titre>`.
   - Ouvrir la Pull Request avec une fiche récapitulative claire pour le contributeur.
-->
