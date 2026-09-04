# Directives et règles du projet CookiGram 🍳

Ce document définit les règles impératives que tout agent d'assistance ou développeur doit respecter dans ce dépôt.

## Chargement persistant du profil d'agent & Registre vivant

Ce fichier est le point d'entrée commun du dépôt pour Codex, OpenCode et Gemini Code.
Pour une efficacité maximale et une économie drastique de temps et de tokens :

1. Consulter en priorité absolue [`.agents/STATUS.md`](.agents/STATUS.md) et [`.agents/claims.json`](.agents/claims.json) pour connaître l'état vivant du projet et les claims en cours.
2. Respecter scrupuleusement la règle de verrouillage anti-doublon [`.agents/rules/task-claiming.md`](.agents/rules/task-claiming.md) : **interdiction absolue de coder sans claim préalable ni validation officielle**.
3. Pour le profil complet du développeur : [`.agents/roles/senior-developer.md`](.agents/roles/senior-developer.md).
4. [`PRODUCT_PRINCIPLES.md`](PRODUCT_PRINCIPLES.md) et les règles spécialisées dans [`.agents/rules/`](.agents/rules/).
5. Règles d'orchestration tri-agents (AGY, OpenCode, Codex) et frugalité de quotas : [`.agents/rules/token-frugality.md`](.agents/rules/token-frugality.md) et [`.agents/rules/multi-agent-orchestration.md`](.agents/rules/multi-agent-orchestration.md).

---

## 🍲 Contribution Culinaire & Importation de Recettes (Agents & Tiers)

Si votre mission consiste à **ajouter, adapter, traduire ou vérifier une recette** :
1. **Pas de verrou dev requis** : Vous n'avez pas besoin de claim dans `claims.json` ni d'exécuter la suite Playwright/E2E.
2. **Guide impératif** : Consultez le skill culinaire universel [`.agents/skills/import-recipe-gram/SKILL.md`](.agents/skills/import-recipe-gram/SKILL.md).
3. **Validation atomique instantanée (< 2 s)** :
   ```bash
   python -m generator.recipe_check recipes/<slug>.gram
   ```
4. **Illustration d'attente autorisée** : Si aucune image photoréaliste n'est générée immédiatement, déclarez `image: images/placeholder-recipe.jpg` et consignez le prompt dans `image-prompts/<slug>.md`.
5. **Soumission** : Travaillez sur une branche isolée (`recipe/<slug>`) et ouvrez une Pull Request.

---

## 1. Règle impérative : Versionnement Git systématique (Commit & Push)

> **Règle d'or :** Tout travail achevé doit être systématiquement **gité, commité et poussé (`git push`)** avant de clore l'intervention. L'arbre de travail (`working tree`) doit être propre à la fin de chaque tâche.

### Procédure de clôture de tâche obligatoire :

> ⚡ **Économie de temps et de tokens :** Pendant la phase de développement itératif, n'exécutez que les tests ciblés du composant modifié (ex: `npm run test:unit` ou `pytest tests/test_cible.py`). La suite complète (`pytest` globale + `playwright e2e` qui dure 12-14 min) ne doit être lancée **qu'une seule fois**, lors de la validation finale avant commit/push.

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
* **Icônes d'ingrédients & Graphisme (Codex & Agents)** :
  * Respecter impérativement la spécification [`.agents/rules/ingredient-icons.md`](.agents/rules/ingredient-icons.md).
  * Style « spot illustration / sticker manga », optimisé pour l'affichage en 24×24 px et 32×32 px (silhouette identifiable, contours encrés nets, fond transparent).
  * Affichage autorisé : liste d'ingrédients, modale de courses, bloc étape en Mode Cuisine. Interdit dans le corps de texte des étapes.

---

## 3. Gouvernance produit et priorisation des tâches (Human-in-the-loop)

* **Le Product Owner (@PierreCsn) est l'utilisateur n°1** :
  * CookiGram est construit avant tout pour son expérience réelle en cuisine.
  * Ses retours qualitatifs prévalent sur les métriques théoriques ou les dogmes conventionnels.
* **Document de référence : [`PRODUCT_PRINCIPLES.md`](PRODUCT_PRINCIPLES.md)** :
  * **Principe 1 — Cooking first** : La lisibilité et l'ergonomie en cuisine (plan de travail, mains sales/mouillées, cibles 44 px min, minuteurs accessibles, zéro chevauchement de la barre de navigation `.cook-nav`) ont la priorité absolue.
  * **Principe 2 — Mobile & tablette first** : Le smartphone et la tablette tactile sont les scénarios d'usage primaires. Aucun débordement horizontal toléré (360 px, 390 px, 768 px).
  * **Principe 3 — Simplicité & frugalité** : Aucun framework lourd côté client, JavaScript ES natif, CSS compartimenté, rapidité d'exécution.
* **Ordre officiel de réalisation des tâches** :
  * L'ordre des travaux est impérativement fixé par l'issue épinglée **[#35](https://github.com/PierreCsn/cookigram/issues/35)** et les **Jalons GitHub (Milestones)**.
  * Tout développeur ou agent doit respecter strictement l'ordre des lots :
    1. **Lot 1 — UX Cuisine & Ergonomie Mobile (P0/P1)** : issues #28, #29, #27 (**URGENCE ABSOLUE**)
    2. **Lot 2 — SEO Critique & Indexation (P1)** : issues #15 (clos), #16 (clos), #20
    3. **Lot 3 — Ergonomie & Fiche Recette (P1)** : issues #26, #30, #32, #31
    4. **Lot 4 — SEO Avancé & Performance (P2)** : issues #33, #34, #17, #19, #18, #21, #22, #23, #24
    5. **Lot 5 — Dette Technique & Socle (P3/P4)** : issues #8, #1
  * **Interdiction de sauter un lot** pour travailler sur des améliorations secondaires tant que le lot en cours n'est pas soldé, testé et validé.

---

## 4. Rôles et profils d'agents spécialisés

Le projet CookiGram s'appuie sur une collaboration multi-agents. Les personas, directives opérationnelles et contraintes d'exécution propres à chaque rôle sont consignés dans le dossier [`.agents/roles/`](.agents/roles/) :

* **Recipe Expert Agent** : [`recipe-expert.md`](.agents/roles/recipe-expert.md)
  Directives pour l'autorité culinaire garantissant l'exactitude des recettes Gram, la taxonomie des ingrédients, la traçabilité nutritionnelle CIQUAL et la reproductibilité sur le plan de travail (cuisine robot et traditionnelle sans robot).

* **Cooking Execution Expert Agent** : [`cooking-execution-expert.md`](.agents/roles/cooking-execution-expert.md)
  Directives pour l'expert en assistance d'exécution culinaire garantissant la clarté et l'ergonomie du Mode Cuisine pas-à-pas sur le plan de travail, sans altération de la recette canonique (source de vérité).

* **Senior Development Agent** : [`senior-developer.md`](.agents/roles/senior-developer.md)
  Directives exhaustives pour l'ingénieur logiciel senior chargé d'implémenter les tâches approuvées, avec discipline Git/GitHub, validation mobile-first, respect absolu de la gouvernance et de la source de vérité Gram.
