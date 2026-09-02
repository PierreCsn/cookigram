# Règle Produit : Gouvernance et Ordre de Priorité

> **Règle fondamentale :** Le Product Owner (@PierreCsn) est l'utilisateur n°1 de CookiGram. Le produit est conçu d'abord et avant tout pour son expérience réelle en cuisine.

---

## 1. Principes non négociables (voir `PRODUCT_PRINCIPLES.md`)
1. **Cooking first** : L'expérience vécue en cuisinant (lisibilité à 1 mètre, cibles tactiles 44px pour mains mouillées/sales, visibilité permanente des minuteurs, absence de recouvrement par `.cook-nav`) a la priorité absolue sur toute métrique théorique.
2. **Mobile & tablette first** : Pas de défilement horizontal parasite (360px, 390px, 768px). Respect des `safe-area-inset`.
3. **Simplicité & frugalité** : Zéro framework lourd, JavaScript ES modulaire natif, CSS compartimenté, rapidité d'exécution.

---

## 2. Ordre de traitement impératif des tâches
L'ordre d'implémentation est fixé par l'issue épinglée **#35** et les **Jalons GitHub (Milestones)**.

### Règle d'ordonnancement :
* **Ne jamais sauter de lot** : Aucun agent ne doit entamer des tâches d'un lot ultérieur tant que le lot en cours n'est pas soldé, testé et validé.
* **Ordre officiel** :
  1. `Lot 1 — UX Cuisine & Ergonomie Mobile (P0/P1)` : issues #28, #29, #27. **URGENCE ABSOLUE**.
  2. `Lot 2 — SEO Critique & Indexation (P1)` : issues #15 (clos), #16 (clos), #20.
  3. `Lot 3 — Ergonomie & Fiche Recette (P1)` : issues #26, #30, #32, #31.
  4. `Lot 4 — SEO Avancé & Performance (P2)` : issues #33, #34, #17, #19, #18, #21, #22, #23, #24.
  5. `Lot 5 — Dette Technique & Socle (P3/P4)` : issues #8, #1.

---

## 3. Garde-fous pour les développeurs et experts
* Ne jamais masquer d'illustration ou d'information essentielle sur mobile sans accord explicite du Product Owner.
* Ne jamais dégrader l'ergonomie en cuisine pour satisfaire un critère SEO ou esthétique secondaire.
* En cas de doute sur un comportement ou arbitrage produit, se référer aux principes dans `PRODUCT_PRINCIPLES.md`.
