# Meal Planning — Nutrition « Plaisir & Santé »

> Document d’architecture et de vision pour [PDR-0010](../decisions/PDR-0010-nutrition-plaisir-sante-meal-planning.md), associé à [l’Issue #136](https://github.com/PierreCsn/cookigram/issues/136).

## 1. Intention produit

Le Meal Planning hebdomadaire doit aider à manger avec plus de vitalité sans transformer la cuisine en régime punitif. Le plaisir est une composante légitime du menu : CookiGram organise la semaine autour des envies de l’utilisateur, puis construit les repas du quotidien qui les rendent compatibles avec une alimentation variée et une bonne énergie.

Le principe est une boussole d’organisation, pas une prescription médicale : il n’impose ni calories, ni aliments interdits, ni culpabilité lorsqu’une semaine ne suit pas exactement la cible.

## 2. Règle 80/20 : une semaine, pas un plat isolé

La règle s’applique aux repas principaux planifiés sur une semaine :

```text
80 %  Vitalité  → repas courants, variés, digestes et nourrissants
20 %  Plaisir   → repas choisis pour leur gourmandise, sans justification
```

Le ratio est calculé sur le nombre de créneaux classés, jamais sur les calories ou une prétendue « compensation » énergétique. L’arrondi est explicite et tolérant : pour une semaine courte ou un petit nombre de créneaux, l’algorithme privilégie les envies déclarées et signale seulement l’écart à la cible. Un repas `balanced` contribue à la stabilité de la semaine sans être forcé artificiellement dans une catégorie.

### Composition « kiffs d’abord »

1. L’utilisateur choisit d’abord un ou deux repas `pleasure` (par exemple un plat de bistrot ou une douceur de week-end).
2. Le planneur réserve ces créneaux et complète les autres avec des repas `vitality` et `balanced`.
3. Il vérifie le ratio, la diversité végétale et la faisabilité de la liste de courses.
4. Il propose des alternatives lorsqu’une contrainte est impossible, sans retirer silencieusement un plaisir choisi.

## 3. Dualité Vitalité / Plaisir

Le champ optionnel proposé dans les métadonnées `.gram` est :

```yaml
nutrition_profile: vitality | pleasure | balanced
```

| Profil | Rôle dans la semaine | Critères d’orientation |
| --- | --- | --- |
| `vitality` | Quotidien, notamment les repas où l’on recherche de la légèreté | Légumes et fibres présents, source de protéines rassasiante, préparation compatible avec l’énergie et le temps disponibles |
| `pleasure` | Moment gourmand, festif ou réconfortant | Sauce généreuse, gratin, dessert ou cuisson longue assumés ; aucune pénalisation dans l’interface |
| `balanced` | Socle polyvalent | Plat complet combinant naturellement plusieurs familles d’aliments |

Ces profils sont des repères éditoriaux et d’ordonnancement. Ils ne remplacent pas les valeurs CIQUAL affichées par le moteur nutritionnel et ne déduisent pas l’état de santé d’une personne.

### État d’implémentation

Le dépôt public contient les recettes et leurs métadonnées dans [`recipes/`](../recipes/). La validation du champ `nutrition_profile`, sa qualification sur le catalogue et l’interface de sélection restent à implémenter dans [`cookigram-core`](https://github.com/PierreCsn/cookigram-core). Le champ ne doit donc pas être ajouté aux recettes de production avant la livraison du schéma correspondant dans [`generator/schema.py`](https://github.com/PierreCsn/cookigram-core/blob/main/generator/schema.py).

## 4. Défi positif : 30 plantes par semaine

La métrique hebdomadaire compte les végétaux distincts consommés, et non leurs grammes ou leurs calories. Sont éligibles :

* légumes et fruits ;
* légumineuses ;
* céréales et pseudo-céréales, de préférence complètes ;
* graines et fruits à coque ;
* herbes aromatiques et épices.

Le calcul déduplique les ingrédients par identifiant canonique du référentiel du core, après résolution des alias (`tomate` et `tomates`, par exemple). Une plante utilisée dans trois recettes compte une seule fois ; trois formes ou quantités ne créent pas trois plantes. Les ingrédients non identifiables sont exclus du compteur et signalés pour éviter une précision inventée.

```text
plant_count = cardinalité(identifiants_végétaux_distincts des repas planifiés)
progression  = min(plant_count, 30) / 30
```

L’interface affiche une progression positive, par exemple « 26 / 30 végétaux différents », sans transformer 30 en seuil de réussite ou en conseil médical. Le référentiel et les règles de canonisation devront être versionnés et testés dans [`generator/nutrition/`](https://github.com/PierreCsn/cookigram-core/tree/main/generator/nutrition).

## 5. Compensation intelligente

« Compensation » signifie rééquilibrage de la composition de la semaine, jamais punition du repas plaisir. Après un choix `pleasure`, le planneur recherche des créneaux `vitality` ou `balanced` qui améliorent les dimensions suivantes :

* diversité végétale restante pour approcher 30 plantes ;
* alternance des sources de protéines et des familles d’ingrédients ;
* repas du soir simples et digestes lorsque l’utilisateur le souhaite ;
* charge de préparation compatible avec le temps et l’équipement déclarés.

Le moteur doit expliquer chaque proposition (profil, plantes ajoutées, ingrédients réutilisés, temps gagné). En cas de conflit, les préférences explicites, allergies et exclusions de l’utilisateur sont prioritaires ; le système demande une alternative plutôt que de fabriquer une donnée nutritionnelle.

## 6. Mutualisation anti-gaspi dans `menu_basket`

Le plan hebdomadaire alimente le panier consolidé. Le socle existant [`consolidate_menu`](https://github.com/PierreCsn/cookigram-core/blob/main/generator/menu_basket.py#L560-L585) et [`consolidate_ingredients`](https://github.com/PierreCsn/cookigram-core/blob/main/generator/menu_basket.py#L270-L360) savent déjà regrouper les ingrédients par nom canonique et unité compatible, tout en conservant séparées les unités hétérogènes pour éviter les conversions dangereuses.

L’extension hebdomadaire devra :

1. agréger les recettes de tous les créneaux retenus, et pas seulement une session de 2 à 4 recettes ;
2. réutiliser les herbes, épices, condiments et produits frais communs au plat `pleasure` et aux repas `vitality` ;
3. conserver la traçabilité de chaque quantité vers les recettes qui l’utilisent ;
4. distinguer quantité consolidée, achat minimal réaliste et reste prévisible ;
5. exposer simultanément le panier, le ratio 80/20 et la liste des plantes distinctes.

La mutualisation ne doit jamais changer silencieusement une recette : elle propose un usage voisin ou un ordre de consommation, tandis que la recette `.gram` reste la source de vérité.

## 7. Contrats déterministes et trajectoire

```text
recipes/*.gram
      │ profils + ingrédients canoniques
      ▼
plan hebdomadaire ──► ratio 80/20 ──► compensation explicable
      │
      ├──────────────► plantes distinctes ──► progression / 30
      └──────────────► menu_basket ──► panier mutualisé anti-gaspi
```

| Jalon | Contrat attendu | Dépôt cible |
| --- | --- | --- |
| 1 | Ajouter et valider `nutrition_profile`, puis qualifier le catalogue | [`cookigram-core`](https://github.com/PierreCsn/cookigram-core) et [`recipes/`](../recipes/) |
| 2 | Étendre [`menu_basket.py`](https://github.com/PierreCsn/cookigram-core/blob/main/generator/menu_basket.py) aux agrégats hebdomadaires, au ratio et aux 30 plantes | [`cookigram-core`](https://github.com/PierreCsn/cookigram-core) |
| 3 | Ajouter calendrier, préférences, feedback explicable et export du panier | [`cookigram-core`](https://github.com/PierreCsn/cookigram-core) |

Les tests devront couvrir les arrondis du ratio, la déduplication des alias, les ingrédients inconnus, les contraintes utilisateur, la mutualisation d’unités compatibles et la conservation des unités incompatibles. Les calculs nutritionnels existants restent ceux du moteur déterministe [`calculate_recipe_nutrition`](https://github.com/PierreCsn/cookigram-core/blob/main/generator/nutrition/calculator.py#L17-L130) ; aucun LLM ne décide d’un profil ou d’un résultat chiffré.
