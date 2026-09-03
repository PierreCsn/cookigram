# CookiGram — État d'Exécution & Registre Vivant

> **Note aux agents :** Consultez ce fichier en priorité au démarrage. Il remplace la relecture de dizaines de fichiers de documentation et vous donne l'état exact du projet en moins de 500 tokens.

---

## 🚦 Tâches en cours (Claims actifs)

* **Aucun claim actif.** Le backlog est disponible pour un nouveau claim.

---

## 🎯 Prochaines Priorités Approuvées (Disponibles pour Claim)

1. **🔥 PRIORITÉ IMMÉDIATE (Jalon 2 — Sprint actif)** :
   * **Issue #80** : `feat(cooking): étape 0 « Mise en place du plan de travail » en Mode Cuisine` [P1 / Lot 1]
   * Statut : **Approuvé par le PO et spécifié par le Product Lead** (`potential-dev-work`).
   * *Prêt à être pris par un développeur (poser un claim dans `claims.json` avant de coder).*

2. **Horizon Jalon 3** :
   * **Epic #51** : `Kitchen Scheduler v3 (Solveur CP-SAT)`.

---

## ✅ Dernières Livraisons Clôturées

* **Issue #78 / PR #79** : Persistance de la progression en Mode Cuisine (minuteurs wall-clock, sticky bar contextuelle, cases à cocher ingrédients) — *Fusionné dans `main`*.
* **PR #76** : Import de 2 nouvelles recettes desserts (Cheesecake japonais & Flan aux œufs) — *Fusionné dans `main`*.
* **Issue #67 / PR #77** : Affichage du temps restant estimé dans le header du Mode Cuisine — *Fusionné dans `main`*.
* **Issue #68** : Explicitation pédagogique de l'évaporation sans projection au panier cuisson — *Fusionné dans `main`*.

---

## 🛑 Règles d'Or Développeurs

1. **Claim obligatoire** dans `.agents/claims.json` avant toute ligne de code.
2. **Interdiction d'inventer des fonctionnalités** sans issue portant le label `potential-dev-work`.
3. **Tests ciblés pendant le dev** (`node --test tests/frontend/<mon_test>.test.js` ou `pytest tests/<mon_test>.py`). Ne lancer la suite globale qu'avant le push final.
4. **Commit & push systématique** avec working tree 100% propre.
