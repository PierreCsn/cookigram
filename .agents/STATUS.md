# CookiGram — État d'Exécution & Registre Vivant

> **Note aux agents :** Consultez ce fichier en priorité au démarrage. Il remplace la relecture de dizaines de fichiers de documentation et vous donne l'état exact du projet en moins de 500 tokens.

---

## 🚦 Tâches en cours (Claims actifs)

* **Aucun claim actif en cours.** Le backlog de dev est prêt pour de nouveaux claims approuvés.

---

## ✅ Dernières Livraisons Clôturées

* **Issue #78 / PR #79** : Persistance de la progression en Mode Cuisine (minuteurs wall-clock, sticky bar contextuelle, cases à cocher ingrédients) — *Fusionné dans `main`*.
* **PR #76** : Import de 2 nouvelles recettes desserts (Cheesecake japonais & Flan aux œufs) — *Fusionné dans `main`*.
* **Issue #67 / PR #77** : Affichage du temps restant estimé dans le header du Mode Cuisine — *Fusionné dans `main`*.
* **Issue #68** : Explicitation pédagogique de l'évaporation sans projection au panier cuisson — *Fusionné dans `main`*.

---

## 🎯 Prochaines Priorités Approuvées (Disponibles pour Claim)

1. **Lot 1 & Lot 3 : Clôturés à 100%** (Mode Cuisine mobile, ergonomie, contraste, saveurs, ustensiles, 120+ icônes d'ingrédients).
2. **Lot 4 : SEO Avancé & Performance (95% terminé)**.
3. **Lot 5 : Dette technique** (Compilateur officiel Gram #1).
4. **Horizon v3 : Epic #51 (Kitchen Scheduler - solveur CP-SAT)**.

---

## 🛑 Règles d'Or Développeurs

1. **Claim obligatoire** dans `.agents/claims.json` avant toute ligne de code.
2. **Interdiction d'inventer des fonctionnalités** sans issue portant le label `potential-dev-work`.
3. **Tests ciblés pendant le dev** (`node --test tests/frontend/<mon_test>.test.js` ou `pytest tests/<mon_test>.py`). Ne lancer la suite globale qu'avant le push final.
4. **Commit & push systématique** avec working tree 100% propre.
