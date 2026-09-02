# Directives et règles du projet CookiGram 🍳

Ce document définit les règles impératives que tout agent d'assistance ou développeur doit respecter dans ce dépôt.

---

## 1. Règle impérative : Versionnement Git systématique (Commit & Push)

> **Règle d'or :** Tout travail achevé doit être systématiquement **gité, commité et poussé (`git push`)** avant de clore l'intervention. L'arbre de travail (`working tree`) doit être propre à la fin de chaque tâche.

### Procédure de clôture de tâche obligatoire :
1. **Validation qualité préalable** :
   * S'assurer que le linter Python et le formateur sont satisfaits : `ruff check generator tests` et `ruff format --check generator tests`.
   * S'assurer que le type checking Python est satisfait : `mypy generator/`.
   * S'assurer que le linter JavaScript est satisfait : `npm run lint`.
   * S'assurer que la syntaxe JavaScript est valide : `node --check static/app.js`, `node --check static/sw.js` et `for f in static/js/modules/*.js; do node --check "$f"; done`.
   * Exécuter la suite complète de tests Python : `pytest`.
   * Exécuter la suite de tests unitaires et E2E JavaScript : `npm test` (`npm run test:unit && npm run test:e2e`).
   * Vérifier que la génération du site statique s'exécute sans erreur : `python -m generator.build`.
2. **Staging des modifications** :
   * Vérifier les fichiers modifiés et non suivis avec `git status`.
   * Ajouter tous les fichiers pertinents avec `git add <fichiers>`.
   * Ne jamais commiter de fichiers temporaires, de caches ou de captures de test (respecter le `.gitignore`).
3. **Commit explicite et descriptif** :
   * Créer un commit avec un message structuré résumant clairement les fonctionnalités ajoutées ou les corrections apportées :
     ```bash
     git commit -m "Description claire et concise des modifications"
     ```
4. **Push immédiat** :
   * Pousser systématiquement les commits sur la branche distante active :
     ```bash
     git push
     ```
5. **Vérification finale** :
   * Exécuter `git status` pour confirmer que l'arbre de travail est propre (`nothing to commit, working tree clean`).

---

## 2. Architecture et principes techniques

* **Recettes `.gram`** :
  * Syntaxe canonique conforme au langage Gram.
  * Chaque ingrédient `@nom{quantité}` doit être référencé dans `.gram/ingredients.yaml` et documenté dans `.gram/ingredient-provenance.yaml`.
  * Tolérance zéro sur les conversions nutritionnelles silencieuses ou imprécises.
* **Frontend modulaire sans framework** :
  * Modules JavaScript ES natifs dans `static/js/modules/` (chargés via `<script type="module">`).
  * Chaque module doit exposer une fonction d'initialisation indépendante et tolérante à l'absence de son DOM.
  * Styles CSS découpés par domaine dans `static/css/`, automatiquement concaténés lors du build via `generator/build.py` dans `output/assets/app.css`.
  * Tests unitaires JavaScript dans `tests/frontend/*.test.js` utilisant le runner natif Node (`node --test`).
* **PWA & Offline-First** :
  * Le Service Worker précharge l'ensemble des recettes, images et assets.
  * Toute modification d'asset ou d'image doit mettre à jour le hash de version du cache.
