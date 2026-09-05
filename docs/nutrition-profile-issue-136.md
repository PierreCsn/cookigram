# Nutrition profiles — Issue #136 / PDR-0010

## Objet

Première qualification éditoriale du catalogue pour le futur Meal Planning « Plaisir & Santé ». Le champ optionnel ajouté au frontmatter `.gram` est :

```yaml
nutrition_profile: vitality | pleasure | balanced
```

Il décrit la place naturelle d’une recette dans une semaine, et non une note médicale ni un objectif calorique.

- `vitality` : plat du quotidien, généralement riche en végétaux et/ou légumineuses, digeste et compatible avec un soir de semaine. Le seuil de fibres ≥ 6 g et le temps `<30 min` restent des critères à vérifier quand les données CIQUAL et le temps réel sont disponibles ; ils ne sont pas déduits artificiellement ici.
- `balanced` : composition déjà complète (protéine, végétaux, féculent ou matière grasse de qualité) sans nécessiter de twist particulier.
- `pleasure` : recette festive, généreuse, sucrée, très riche ou centrée sur une sauce/charcuterie ; elle est pleinement assumée dans les 20 % plaisir.

La classification est une première proposition humaine basée sur le titre, les ingrédients, les tags et la structure de chaque fiche. Elle ne modifie aucune proportion et devra être réévaluée après le moteur de menu et les données nutritionnelles fiables.

## Audit du corpus

Le ticket mentionne 88 recettes ; l’audit du checkout contient 89 fichiers `.gram`. Les 89 sont listés ci-dessous, exactement une fois.

### `vitality` — 30

`bolognaise-lentilles-vertes`, `curry-poulet-express`, `curry-poulet-noix-coco`, `dhal-lentilles-corail-coco`, `gratin-chou-fleur`, `poisson-a-la-veracruz`, `poulet-basquaise`, `ragout-porc-legumes`, `salade-cesar`, `salade-de-lentilles`, `salade-de-pois-chiches`, `salade-grecque`, `saumon-a-la-toscane`, `saumon-confit-sous-vide`, `saumon-laque-saveurs-asiatiques`, `sauce-cacahuete-citron-vert`, `sauce-green-goddess`, `sauce-miso-gingembre`, `sauce-tahini-yaourt-citron`, `shakshuka-feta-oeufs`, `soupe-butternut-curry-amandes`, `soupe-poireaux-pommes-de-terre-fenouil`, `veloute-asperge-cerfeuil`, `veloute-automne-gambas`, `veloute-butternut-lentilles-corail-curry`, `veloute-de-carottes-curry`, `veloute-glace-petits-pois`, `veloute-langoustines-coriandre`, `veloute-potiron-cannelle`, `vinaigrette-moutarde-dijon`

### `balanced` — 30

`ballotines-poulet-legumes-riesling`, `blanquette-de-poulet`, `bo-kho-boeuf-vietnamien`, `chili-con-carne`, `curry-de-boeuf`, `curry-poulet-fruits-riz`, `curry-poulet-tomates-amandes`, `filet-mignon-blanquette`, `gratin-poulet-brocolis`, `gratin-pommes-de-terre-saumon-epinards`, `jambalaya-poulet`, `lasagnes-bolognaise`, `lasagnes-moussaka`, `oeuf-parfait-64c-creme-champignons`, `one-pot-pasta-epinards-saumon`, `osso-buco-milanaise`, `pollo-al-ajillo`, `porc-aigre-doux-puree`, `poulet-gaston-gerard`, `risotto-petits-pois-jambon`, `risotto-poulet-champignons`, `roti-de-porc-sauce-echalote`, `salade-de-penne-italienne`, `seafood-boil-louisiane`, `saute-de-porc-au-curry`, `supreme-poulet-estragon-sous-vide`, `tourte-legumes-boeuf`, `focaccia-thermomix`, `pains-pita-maison`, `pommes-anna`

### `pleasure` — 29

`barbacoa-boeuf-effiloche`, `brioche-butchy`, `briochettes-perdues-erable`, `butter-chicken`, `carbonnade-flamande`, `carrot-cake`, `cheesecake-japonais-extra-leger`, `croquettes-de-poissons`, `faux-filet-boeuf-sous-vide`, `flan-aux-oeufs-caramel`, `foret-noire-cyril-lignac`, `ile-flottante-creme-anglaise`, `lu-rou-fan-porc-taiwanais`, `magret-canard-sous-vide`, `oignons-caramelises-balsamique`, `one-pot-pasta-aubergines-lardons-champignons`, `one-pot-pasta-soupe-oignon`, `pates-petits-pois-lardons`, `pesto-ail-des-ours`, `plat-de-cote-boeuf-instant-pot`, `porc-au-caramel`, `poulet-tikka-masala`, `riz-cajun-saucisse-fumee`, `sauce-au-poivre-vert`, `sauce-bearnaise`, `sauce-roquefort`, `souris-agneau-confite-sous-vide`, `tantanmen-ramen-epice`, `tarte-poireau-lardons`

Le décompte est donc **30 vitality / 30 balanced / 29 pleasure = 89**. Il devra être recalculé automatiquement lorsque le champ sera intégré au schéma partagé.

## Cinq recettes témoins

| Recette | Profil | Pourquoi ce choix | Twist de vitalité proposé |
| --- | --- | --- | --- |
| `dhal-lentilles-corail-coco` | `vitality` | Légumineuse, épinards, plat végétarien en une casserole | Garder la base ; servir avec davantage d’épinards ou une crudité citronnée, sans réduire le dhal ni remplacer silencieusement le lait de coco. |
| `salade-de-pois-chiches` | `vitality` | Légumineuse, légumes crus, herbes et citron | Ajouter une herbe fraîche ou un légume croquant déjà compatible avec la recette ; conserver la vinaigrette et son identité méditerranéenne. |
| `saumon-confit-sous-vide` | `balanced` | Protéine de qualité et cuisson douce, base facile à compléter | Associer à un légume de saison et à une céréale complète au moment du menu ; ne pas altérer la cuisson sous vide. |
| `blanquette-de-poulet` | `balanced` | Plat complet familial avec volaille, carottes et champignons | Ajouter une salade verte ou des légumes rôtis en accompagnement et réserver la sauce à la portion prévue. |
| `foret-noire-cyril-lignac` | `pleasure` | Dessert de fête, généreux et explicitement assumé | Aucun allègement obligatoire : placer ce kiff d’abord, puis mutualiser cerises, herbes ou légumes frais dans les repas vitality de la semaine. |

## Règles pour les futurs twists

1. Un twist enrichit l’accompagnement, les végétaux, les herbes ou l’organisation du menu ; il ne change pas silencieusement la recette source.
2. Le profil `pleasure` n’est pas une sanction : il sert à réserver une place visible aux envies gourmandes avant de composer le reste de la semaine.
3. La cible « 30 plantes par semaine » compte les végétaux distincts (fruits, légumes, légumineuses, céréales, herbes et épices), pas les calories.
4. Une future automatisation pourra proposer des twists selon les ingrédients déjà achetés et leur fraîcheur ; elle devra préserver les quantités et variantes d’appareils de la fiche.

## Décision d’implémentation

Le parseur actuel conserve déjà les clés YAML optionnelles dans `Recipe.metadata`. Cette livraison prototype le champ sur cinq fiches et documente la taxonomie ; l’extension du schéma partagé pour valider strictement l’énumération, puis son exploitation dans `menu_basket`, restent des étapes dédiées du Jalon 2.
