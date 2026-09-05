# PDR-0010 : Vision « Nutrition Plaisir & Nutrition Santé » intégrée au Meal Planning hebdomadaire

* **Date :** 5 septembre 2026  
* **Statut :** Validé par le Product Owner (@PierreCsn, utilisateur n°1)  
* **Décideurs :** Pierre (@PierreCsn, Product Owner), Product Lead  
* **Issue associée :** [PierreCsn/cookigram#136](https://github.com/PierreCsn/cookigram/issues/136)  

---

## 1. Contexte & Problème d'Usage

Jusqu'alors, la nutrition dans CookiGram était abordée sous un angle exclusivement comptable et analytique (calcul déterministe des calories et macronutriments via les tables ANSES CIQUAL).

Bien que rigoureuse et exempte d'hallucinations, cette approche souffrait de deux limites majeures constatées par l'utilisateur n°1 (Pierre) :
1. **La fausse dichotomie Plaisir vs Régime :** Les outils nutritionnels classiques (type MyFitnessPal) reposent sur un comptage de calories punitif, rigide et culpabilisant, menant inévitablement à l'abandon ou à une cuisine austère et insipide.
2. **L'isolement de la recette :** Évaluer l'équilibre plat par plat n'a aucun sens physiologique. La nutrition humaine se régule sur **le rythme de la semaine** : la cuisine efficace et légère du quotidien cohabite avec la cuisine réconfortante et festive du week-end.

---

## 2. Décision Produit Fondamentale

Le Product Owner et le Product Lead décident d'ancrer l'évolution nutritionnelle de CookiGram au cœur du **Module de Meal Planning hebdomadaire**, articulé autour de la règle d'or **« 80 % Vitalité Quotidienne / 20 % Plaisir Assumé »**.

CookiGram n'interdit aucun beurre ni aucun sucre : il orchestre l'équilibre hebdomadaire en permettant à l'utilisateur de placer ses « moments plaisirs » au sein d'une semaine physiologiquement régulatrice, protectrice du sommeil et stimulante pour l'énergie.

---

## 3. Piliers d'Architecture & Fonctionnalités

### Pilier 1 — Typologie des Recettes dans le format `.gram`
Ajout dans le schéma de métadonnées [`generator/schema.py`](https://github.com/PierreCsn/cookigram-core/blob/main/generator/schema.py) et dans les [`recipes/*.gram`](../recipes/) du champ optionnel :
```yaml
nutrition_profile: vitality | pleasure | balanced
```
* **`vitality` (Santé / Quotidien) :**  
  Plats digestes, riches en fibres ($\ge 6\text{ g}$), index glycémique modéré, pauvres en acides gras saturés. Idéal du lundi au jeudi soir (préparation $< 30\text{ min}$, favorise un sommeil profond sans lourdeur digestive).
* **`pleasure` (Gourmand / Bistrot / Fête) :**  
  Plats réconfortants, sauces émulsionnées, gratins, cuissons longues, douceurs sucrées (*Porc au caramel*, *Pommes Anna*, etc.). 100 % assumés pour le vendredi soir, le samedi ou les tablées conviviales.
* **`balanced` (Équilibré par nature) :**  
  Plats complets spontanément équilibrés combinant protéines maigres, légumes généreux et féculents complexes.

---

### Pilier 2 — Composition de Semaine « Kiffs d'Abord & Compensation »
1. **Choix des moments plaisirs :** L'utilisateur commence par sélectionner les 1 ou 2 plats gourmands qu'il a envie de savourer cette semaine.
2. **Génération compensatoire :** CookiGram tisse les repas restants de la semaine avec des recettes `vitality` complémentaires pour garantir l'équilibre global :
   - *Midi :* Énergie active durable, protéines rassasiantes, féculents complets (anti-coup de pompe de 14h).
   - *Soir :* Légèreté, légumes abondants, soupes ou poissons vapeur pour maximiser la récupération nocturne.

---

### Pilier 3 — Le Défi Positif « 30 Plantes par Semaine » (Microbiote)
Remplacement de l'obsession calorique par la métrique moderne du microbiote (consensus *American Gut Project*) :
* Calcul automatique du nombre de végétaux distincts consommés sur la semaine (légumes, fruits, céréales complètes, légumineuses, graines, herbes aromatiques, épices).
* Jauge hebdomadaire valorisante : *« 26 / 30 végétaux différents au menu cette semaine ! »*.

---

### Pilier 4 — Mutualisation des Ingrédients & Zéro Gaspillage (Lien `menu_basket`)
Le Meal Planning optimise la liste de courses en cascade :
* Les herbes fraîches, épices ou produits achetés pour le plat `pleasure` du week-end sont réutilisés dans les plats `vitality` de la semaine.
* Économie financière et zéro gaspillage alimentaire sur les produits frais.

---

## 4. Découpage & Trajectoire Opérationnelle

1. **Jalon 1 (Spécification & Schéma) :**  
   - Intégrer `nutrition_profile` dans le schéma de validation [`generator/schema.py`](https://github.com/PierreCsn/cookigram-core/blob/main/generator/schema.py).
   - Qualifier le catalogue existant des 88 recettes via l'agent `Recipe-Expert`.
2. **Jalon 2 (Algorithme d'Équilibrage Hebdomadaire) :**  
   - Étendre [`menu_basket.py`](https://github.com/PierreCsn/cookigram-core/blob/main/generator/menu_basket.py) pour agréger les métriques d'une semaine (ratio 80/20, diversité végétale).
3. **Jalon 3 (Interface UI Meal Planning) :**  
   - Écran de composition hebdomadaire avec vue calendrier, curseur Plaisir/Santé et export panier de courses.

---

## 5. Justification et Principes Appliqués

* **Principe 6 — Product Owner comme utilisateur n°1 :** Répond directement au besoin quotidien de Pierre de manger sainement sans frustration ni complexité.
* **Principe 1 — Cooking first & Pas de culpabilisation :** La cuisine reste un art du plaisir et du goût ; la santé découle de l'harmonie globale et non de la privation.
* **Règle PDR-0004 — Déterminisme :** Calcul des 30 plantes et des ratios d'ingrédients 100 % algorithmique et traçable dans CIQUAL.
