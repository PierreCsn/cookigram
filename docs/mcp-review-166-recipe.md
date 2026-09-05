# Review Recipe Expert — Surfaces MCP Core / CookiGram (#166)

> **Scope strictement read-only.** Aucun serveur MCP codé, aucune modification de
> `cookigram-core` (propriétaire, épinglé par `.core-version`). Cette review
> s'appuie sur : décisions PO **PDR-0011** (#149, close), recommandation
> **#151** (`needs` / `benefits_from`, en discovery), **#156** (epic MCP),
> **#163** (séparation MCP Core / MCP CookiGram), et le corpus `.gram` local
> (162 recettes, **0 bloc `meal:`** à la date de rédaction).
>
> Statut des sources : #149 **CLOSED** (taxonomie v1 validée) · #151 **OPEN**
> (schéma objet recommandé, décision PO pendante) · #156 **OPEN** · #163 **OPEN** ·
> #166 **OPEN** (présente review).

---

## 1. Concepts : recette / repas / composant

### 1.1 Définitions exigées pour tout contrat MCP

| Concept | Nature | Source de vérité | Exemple |
| --- | --- | --- | --- |
| **Recette** | Préparation canonique, exécutable, versionnée | Fichier `.gram` (frontmatter + graphe d'étapes) | `porc-au-caramel.gram` |
| **Composant** | Recette dont l'**intention éditoriale** est de compléter un repas | `meal.completeness: component` + `role` | `riz-blanc-long-casserole.gram` → `component/starch` |
| **Repas** | Assemblage servi à un moment donné : 1 recette `complete`, ou 1 `partial` + compléments, dans un **contexte utilisateur** (convives, portions, contraintes) | Construit au runtime, validé par l'utilisateur | porc-au-caramel + riz jasmin + légumes, jeudi 20h, 5 pers. |

Le **repas n'est jamais une propriété d'une recette**. C'est la confusion la plus
dangereuse pour le MCP : exposer un tool `compose_meal` côté Core laisserait croire
que le repas se déduit de la recette. Or le repas exige un contexte utilisateur
(qui mange, combien, quand, avec quel équipement) que Core ne connaît pas.

### 1.2 Conséquence architecturale

- **Core** qualifie des **recettes** (lecture déterministe du bloc `meal`,
  validation du schéma, filtrage par rôle).
- **CookiGram** assemble des **repas** (choix utilisateur, ranking sensoriel #98,
  planning #160, faisabilité #154, ordonnancement #51).
- **MCP** expose les deux sans les mélanger : aucun tool ne doit prendre une
  recette en entrée et retourner un « repas » sans marquer explicitement la part
  de décision produit / utilisateur.

---

## 2. `completeness` / `role` / `needs` / `benefits_from` — état et ambiguïtés

### 2.1 Acquis #149 (décidé, à ne pas rouvrir)

- `completeness = complete | partial | component`, `meal` absent = **`unknown`**,
  jamais `complete` par défaut.
- `role` = dimension **indépendante**, scalaire, facultative ; taxonomie v1 :
  `main, starch, vegetable, sauce, salad, bread, condiment` (pas de `starter` /
  `dessert` en v1 — ce sont des services, pas des rôles de composition).
- `complete` ≠ équilibré nutritionnellement.
- **Interdiction d'inférer depuis les tags**, ingrédients, portions ou titres.

### 2.2 Point non figé : la forme de `needs` / `benefits_from` (#151 OPEN)

La correction PO du 2026-09-05 sur #149 est explicite : **la forme exacte de
`needs` / `benefits_from` n'est pas figée**. Deux variantes coexistent :

```yaml
# Variante A — listes simples (corps de #151, hypothèse de travail)
needs: [starch]
benefits_from: [vegetable]

# Variante B — listes d'objets (recommandation Recipe/Cooking Expert, #151)
needs: [{role: starch, required: true}]
benefits_from: [{role: vegetable}]
```

La recommandation #151 (variante B, avec `required: true` explicite dans `needs`,
unicité des paires, interdiction d'intersection `needs` ∩ `benefits_from`,
relations réservées aux `partial`) est culinairement saine et auto-documentée.
**Mais tant que le PO ne l'a pas validée, aucun contrat MCP ne doit figer l'une
ou l'autre.** Un tool MCP qui sérialiserait aujourd'hui `needs` créerait une
variante fantôme irréversible.

### 2.3 Règles v1 #151 à sanctuariser dans Core (pas dans le MCP)

1. Relations **réservées aux `partial`** : un `complete` ne déclare pas de
   `needs`, un `component` ne prescrit pas le repas parent.
2. Cibles = **rôles canoniques #149**, jamais un nom de recette ni un tag.
3. Pas de contraintes de durée / équipement / nutrition / sensoriel dans la
   relation (relève de #154 / #98 / #51).
4. Listes vides omises ; absence = « aucune relation déclarée », pas « aucun
   accord possible ».
5. Un composant satisfait **au plus une relation de rôle** en v1.

Si ces règles vivent dans l'adapter MCP au lieu de Core, chaque client
(Meal Planner, scheduler, agents) réimplémentera sa version → dérive garantie.

### 2.4 Fait corpus : 0 recette qualifiée, et une erreur de qualification déjà visible

`grep -rl "^meal:" recipes/` → **0 résultat**. Le MCP ne peut donc aujourd'hui
rien calculer sur la composition : tout tool `suggest_*` / `compose_*` branché
sur le corpus actuel ne peut retourner que `unknown` / `insufficient-data`.

Plus grave, la table d'échantillon de la recommandation #151 contient **une
erreur factuelle contre le corpus**, preuve du risque d'invention :

> #151 classe `curry-poulet-noix-coco` en `partial/main` avec `need starch`.

Or `recipes/curry-poulet-noix-coco.gram` **intègre 200 g de riz basmati**
(panier cuisson) **et** 260 g de légumes Varoma (poivron + courgette), servis
dans la même assiette (« Répartir le riz basmati et les légumes vapeur… Napper
de sauce curry »). Description : « Curry complet au Thermomix, avec riz basmati
et légumes cuits au Varoma ». C'est un **`complete/main`** par les critères #149
eux-mêmes (féculent + garniture intégrés), au même titre que
`curry-poulet-fruits-riz.gram`. Un MCP qui aurait servi la recommandation #151
telle quelle aurait **suggéré du riz avec un plat qui en contient déjà**.

Leçon : la qualification éditoriale doit être **vérifiée contre le corps de la
recette** (ingrédients réellement présents, dressage), jamais contre le titre,
les tags ou la mémoire d'un modèle. Ce cas devient le test T2 ci-dessous.

---

## 3. Frontière Core vs CookiGram (review de #156 Axe 1/5 et #163)

### 3.1 Principe de tri

| Déterministe, sans contexte utilisateur → **Core** | Décision / préférence / contexte → **CookiGram** |
| --- | --- |
| Valider le schéma `meal` ; lire `completness/role/needs` tels que déclarés | Ordonner des candidats (goût, saison, dispo, historique) |
| Lister les recettes d'un `role` donné (filtre exact) | Recommander « le meilleur » accompagnement |
| Mettre à l'échelle des quantités ; consolider une liste de courses (arithmétique) | Choisir les portions cibles, les régimes, les exclusions |
| Vérifier la cohérence (doublon, intersection, `needs` sur `complete`) | Composer, planifier, ordonnancer, confirmer avec l'utilisateur |

### 3.2 Verdict tool par tool

**À conserver côté Core (READ / ANALYZE, réutilisables hors MCP) :**

- `validate_recipe` — inclure à terme les règles `meal` §2.3.
- `get_recipe` (lecture canonique) — le MCP ne doit jamais résumer le `.gram`
  de mémoire ; il le lit.
- `scale_recipe`, `resolve_ingredients` — calculs déterministes.
- `get_meal_qualification` (nom imposé, voir §3.3) — lecture stricte du bloc
  `meal`, avec `unknown` explicite.

**À conserver côté CookiGram (READ produit, puis WRITE explicite) :**

- `search_recipes`, `get_recipe` (vue produit), `get_week_plan` (état utilisateur).

**À renommer / repenser (noms actuels trompeurs ou chevauchants) :**

| Nom #156 / #163 | Problème culinaire | Proposition |
| --- | --- | --- |
| `check_meal`, `check_meal_completeness`, `analyze_meal` | Trois noms pour une lecture ; « check » suggère un jugement | **`get_meal_qualification`** (Core, READ) : retourne le bloc déclaré + `unknown`, sans avis |
| `get_missing_roles` (#156 Axe 5) | Suggère un calcul ; or c'est une lecture éditoriale | **`get_declared_needs`** (Core, READ) : retourne `needs`/`benefits_from` déclarés ou `insufficient-data` |
| `suggest_components`, `suggest_meal_components` | Sonne comme une vérité (« il faut ») alors que c'est un ranking non contraignant | **`suggest_completions`** (CookiGram) : candidats filtrés par rôle puis classés (#98), marqués `suggestion` non contraignante |
| `find_components` | Filtre déterministe confondu avec suggestion | **`list_recipes_by_role`** (Core, READ) : filtre exact sur corpus qualifié |
| `rank_pairings` | Crée un besoin au lieu de classer des candidats | **`rank_candidates`** : n'intervient **qu'après** filtrage structurel ; ne crée jamais de besoin |
| `compose_meal` (listé « plus tard » côté Core en #163) | **Refus net côté Core** : composer = décider avec l'utilisateur | **`build_meal_proposal`** (CookiGram, WRITE/proposition) : assemblage soumis à confirmation, jamais une vérité |
| `check_execution_feasibility` | Mélange #154 (faisabilité) et #51 (ordonnancement) | Reporter ; à découper plus tard en `estimate_feasibility` (Core/ANALYZE) vs `schedule_meal` (produit) |

**À reporter (discovery amont non stabilisée) :**

- Tout **WRITE authoring** (`import_recipe`, `create/patch_recipe`, `classify`,
  `audit_corpus`) : #151/#152 non closes, 0 recette qualifiée, contrat public
  v1.0.0 ignorant `meal`. Autoriser l'écriture agentique maintenant, c'est
  laisser un LLM écrire la sémantique qu'il est censé consommer.
- Toute la **session cuisine vocale** (`get_current_step`, `complete_step`,
  `report_delay`, `reschedule_meal`, timers…) : aucun modèle de session (#51,
  #154) n'existe ; exposer ces tools figerait un état fantôme.
- `schedule_meal`, `get_cooking_plan` en MCP : dépendent de #51/#154.
- Resources `cookigram://meals/current`, `cookigram://equipment/my-kitchen` :
  état utilisateur non modélisé (cf. #160 Meal Planner, Shopping Planner).
- Transport distant / auth multi-utilisateur (#156 Axes 6-7) : prématuré avant
  le POC local en lecture seule.

### 3.3 Réponses aux questions de #166 (angle recette)

- *Surfaces #163 suffisamment distinctes ?* **Non en l'état** : `compose_meal`
  et `schedule_cooking` apparaissent côté Core « plus tard », et
  `check/suggest/compose` se chevauchent entre #156 Axe 1 et Axe 5. Appliquer le
  tableau §3.2.
- *Tools Core réutilisables hors MCP ?* Oui pour `validate/scale/resolve/list`
  **à condition** que la règle métier vive dans Core et que le MCP ne soit
  qu'un adapter fin (garde-fou #163 respecté, à faire respecter en revue de code).
- *Un agent généraliste peut-il utiliser CookiGram sans connaître `.gram` ?*
  Oui **si** les noms disent l'intention utilisateur (`suggest_completions`,
  `build_meal_proposal`) et **si** chaque réponse porte sa provenance
  (déclaré / calculé / suggéré / choix utilisateur) — sinon l'agent confondra
  suggestion et vérité.
- *Erreurs/absences représentables ?* **Pas encore spécifié** : exiger un
  contrat d'erreur commun (voir §4.2).
- *WRITE séparées ?* Principe « aucun WRITE par défaut » (#156 Axe 3) à garder ;
  marquer `build_meal_proposal` et tout planning comme WRITE dès le POC.

---

## 4. `unknown` / `insufficient-data` et déterminisme

### 4.1 Règle d'or

> **Tout tool de composition appliqué à une recette `unknown` (pas de bloc
> `meal`) ou à un schéma `needs` non encore figé (#151 OPEN) retourne
> `insufficient-data` avec motif explicite, jamais une suggestion devinée.**

Cas du corpus actuel : les 162 recettes étant non qualifiées, `suggest_*` et
`compose_*` doivent aujourd'hui répondre `insufficient-data: corpus not yet
qualified (see #149/#151)` — c'est le comportement **attendu**, pas un échec.

### 4.2 Contrat d'erreur minimal exigé (avant tout POC)

```yaml
status: ok | unknown | insufficient-data | invalid
provenance: declared | computed | suggestion | user-choice
reason: "meal block absent → completeness unknown (#149)"
missing: [meal.completeness, meal.needs]
```

- `unknown` = la recette n'a pas d'intention déclarée (soupe, salade-repas,
  shakshuka, gratins ambivalents en attente de qualification).
- `insufficient-data` = la question dépasse les données (ex. suggérer sans
  `needs` figés, composer sans portions ni date).
- `invalid` = recette rejetée par validation (ex. `needs` sur `complete`,
  rôle hors taxonomie, intersection needs/benefits_from).
- La **provenance** est obligatoire : un LLM qui cite une suggestion comme une
  règle (« CookiGram dit qu'il faut du riz ») doit être détectable.

### 4.3 Ce qui est déterministe vs ce qui ne l'est pas

- **Déterministe (Core, testable)** : validation du schéma, lecture du bloc,
  filtre par rôle, arithmétique d'échelle et de courses, détection
  doublon/intersection/interdiction.
- **Non déterministe (produit/LLM, à encadrer)** : classement des candidats,
  formulation conversationnelle, orchestration vocale. Le LLM **explique** un
  résultat Core, il ne le **calcule** jamais.

---

## 5. Risques de dérive sémantique culinaire

| # | Risque | Exemple concret | Garde-fou |
| --- | --- | --- | --- |
| R1 | Qualifier depuis le titre/tags/mémoire au lieu du corps | T2 : curry-noix-coco classé `partial` alors qu'il contient riz + légumes | Qualification relue contre ingrédients + dressage ; test T2 bloquant |
| R2 | Confondre tag et rôle | `curry-poulet-fruits-riz` tagué `riz` **et** contenant du riz vs curry sans riz ; tag `accompagnement` ≠ `component` | Règle #149 : `role` jamais déduit des tags ; le MCP n'expose aucun filtre par tag comme filtre par rôle |
| R3 | `needs` en texte libre (noms de recettes) | `needs: [riz-jasmin]` fige un produit au lieu d'une fonction | Enum de rôles uniquement ; validation rejette le reste |
| R4 | `complete` lu comme « équilibré » | Lasagnes `complete` mais non équilibrées | Champ nutritionnel séparé (#136, MEAL_PLANNING_NUTRITION.md) ; libellé `culinarily-complete`, jamais `balanced` |
| R5 | Rôle canonique vs usage contextuel | `gratin-chou-fleur` : `component/vegetable` par défaut, mais plat végétarien possible selon portion | Intention canonique déclarée ; contexte utilisateur ultérieur sans réécriture (recommandation #149 §2) |
| R6 | Frontières floues `sauce/condiment`, `salad` plat vs garniture, soupe entrée vs plat | `sauce-tahini`, `salade-cesar`, `soupe-poireaux-fenouil` | `unknown` assumé tant que l'auteur ne tranche pas ; `insufficient-data` côté MCP |
| R7 | `required: true` dérivant (`required: false` dans `needs`, champ fantaisie dans `benefits_from`) | Schéma objet non figé | Validation exacte des champs autorisés dès que #151 est décidée |
| R8 | Le sensoriel (#98) créant du besoin | « Le LLM trouve que ça va bien avec » → transformé en `needs` | Ordre imposé : filtre structurel (`needs`) **puis** classement (#98) ; `rank_candidates` ne remonte jamais vers `needs` |
| R9 | Le planning/scheduler redéfinissant la sémantique | #51/#160 décidant qu'un `component` « suffit » comme repas | #150 consomme `completeness/role/needs` sans les redéfinir (décision #149 §7) |

---

## 6. Cas de test concrets (à verser au POC et à la CI Core)

> Pré-requis : qualifier d'abord ces recettes avec leurs blocs `meal` (chantier
> #151, 15–20 recettes). Les résultats attendus ci-dessous découlent des
> décisions #149/#151 et du corps des `.gram`.

| ID | Entrée | Comportement attendu | Cible du test |
| --- | --- | --- | --- |
| T1 | `get_meal_qualification(porc-au-caramel)` | `partial/main`, `needs: [starch]`, `benefits_from: [vegetable]` (une fois qualifié) ; avant qualification : `unknown` + `insufficient-data` sur `get_declared_needs` | Lecture déclarative, pas d'inférence |
| T2 | `suggest_completions(curry-poulet-noix-coco)` | **Aucune suggestion de féculent** : `complete/main` (riz + légumes intégrés). Toute suggestion `starch` = ÉCHEC bloquant | Anti-invention (erreur #151 détectée par cette review) |
| T3 | `get_meal_qualification(curry-poulet-noix-coco)` vs `(curry-poulet-fruits-riz)` | Les deux `complete/main`, zéro `needs` — alors que l'un est tagué `riz` et l'autre non | Tags ≠ sémantique |
| T4 | `get_declared_needs(porc-au-caramel)` → `list_recipes_by_role(starch)` | Contient `riz-blanc-long-casserole`, `riz-basmati-pilaf` ; **ne contient pas** un curry `complete` ni une sauce | Filtre exact par rôle |
| T5 | `suggest_completions(soupe-poireaux-pommes-de-terre-fenouil)` | `insufficient-data` (entrée/plat/repas selon portion, intention non tranchée) ; jamais de `needs` inventé | `unknown` assumé |
| T6 | `suggest_completions(salade-cesar)` | `insufficient-data` (salade-repas plausible mais portion/intention à qualifier) | Idem |
| T7 | `get_declared_needs(gratin-chou-fleur)` | `invalid-operation` : un `component` ne déclare pas de besoins ; `list_recipes_by_role(vegetable)` le retourne comme **candidat**, pas comme demandeur | Asymétrie partial/component |
| T8 | `build_meal_proposal(faux-filet-boeuf-sous-vide)` sans portions ni date | `insufficient-data` listant `portions`, `target_time` manquants ; avec contexte : proposition `partial + starch + vegetable`, marquée `user-choice` à confirmer | Contexte obligatoire |
| T9 | Recette `complete` + `needs` (fixture invalide), rôle `dessert`, intersection needs/benefits | `invalid` avec motif (3 fixtures de validation) | Règles §2.3 |
| T10 | `rank_candidates(porc-au-caramel, role=starch)` | Ordre sensoriel (#98) **parmi** les `starch` uniquement ; le classement ne promeut jamais un non-`starch` | Ordre filtre-puis-classe |
| T11 | `build_meal_proposal(shakshuka-feta-oeufs)` | `complete/main`, aucune suggestion structurelle ; le pain reste une **préférence**, pas un `needs` | Requis vs conseillé |
| T12 | `get_recipe(porc-au-caramel)` via MCP | Contenu canonique (ou référence exacte), pas de reformulation des quantités/températures par le LLM | Anti-paraphrase des données |

---

## 7. Capacités Core manquantes (à remonter, pas à coder dans le MCP)

1. **Validation `meal`** : map, enum `completeness`, enum `role` v1, formes
   `needs`/`benefits_from` dès que #151 décidée, unicité, non-intersection,
   restriction aux `partial`, rejet des champs inconnus. (Contrat public
   `cookigram-contract v1.0.0` l'ignore ; corpus à 0 % qualifié.)
2. **Propagation `unknown`** : toute API Core de composition retourne le statut
   §4.2 au lieu d'une valeur par défaut.
3. **Requête par rôle** : `list_recipes_by_role` sur corpus qualifié (base du
   futur `find_components` déterministe).
4. **Lecture déclarative des besoins** : `get_declared_needs` = projection du
   bloc, zéro calcul, zéro LLM.
5. **Contrat d'erreur versionné** (`status/provenance/reason/missing`) publié
   dans le contrat public avant consommation MCP.
6. **Jeu de fixtures T1–T12** intégré aux tests Core (le T2 doit exister avant
   toute suggestion en production).

Tant que 1–5 manquent, le périmètre MCPMM admissible est : `search_recipes`,
`get_recipe`, `validate_recipe` (+ `get_meal_qualification` en lecture
`unknown`-aware). Tout le reste est discovery, pas implémentation.

---

## 8. Décisions PO / Lead nécessaires (arbitrages, pas d'exécution)

1. **Valider ou corriger la variante B de #151** (objets `{role, required}`) et
   **corriger l'échantillon** : `curry-poulet-noix-coco` = `complete/main`
   (riz + légumes intégrés), pas `partial`. Sans cette correction, la donnée de
   référence reste fausse.
2. **Confirmer l'ordre** : qualification éditoriale de 15–20 recettes (dont les
   12 du §6) **avant** tout tool `suggest_*` / `compose_*`, et validation Core
   du schéma `meal` **avant** tout adapter MCP (séquence #149 → #151 → #152 →
   #150 déjà validée en PDR-0011, à faire respecter pour #156/#163).
3. **Trancher le vocabulaire MCP** (§3.2) : `get_meal_qualification`,
   `get_declared_needs`, `list_recipes_by_role`, `suggest_completions`,
   `build_meal_proposal`, et l'interdiction du `compose_meal` côté Core.
4. **Imposer le contrat d'erreur** §4.2 (statuts + provenance obligatoire) sur
   les deux surfaces #163.
5. **Confirmer le POC minimal** : READ seul (`search/get/validate` +
   `get_meal_qualification`), local, sans WRITE, sans session vocale, avec
   `insufficient-data` comme réponse attendue sur corpus non qualifié.
6. **Statuer sur les cas `unknown` structurels** (soupe, salade-repas,
   shakshuka+pain, gratin plat vs accompagnement) : qui tranche éditorialement,
   et à quelle échéance — le MCP ne doit pas trancher à leur place.
7. **Rappeler l'interdiction d'inférence par tags** à tout futur code MCP
   (elle vaut aussi pour un ranker ou un orchestrateur LLM).

---

## 9. Synthèse livrable #166 (volet Recipe Expert)

1. **Tools à conserver** : `search_recipes`, `get_recipe`, `validate_recipe`,
   `scale_recipe`, `resolve_ingredients` + lecture déclarative (`get_meal_qualification`).
2. **Tools à renommer/repenser** : tableau §3.2 (`check_*` → `get_meal_qualification`,
   `get_missing_roles` → `get_declared_needs`, `suggest_*` → `suggest_completions`
   non contraignante, `compose_meal` → `build_meal_proposal` côté CookiGram uniquement).
3. **Tools à repousser** : WRITE authoring, session cuisine/vocale, scheduling,
   resources d'état, distant/auth.
4. **Capacités Core manquantes** : §7 (validation `meal`, `unknown`, requête par
   rôle, contrat d'erreur, fixtures T1–T12).
5. **Risques agentiques** : §4 (confusion suggestion/vérité sans provenance,
   `compose` sans contexte, paraphrase des quantités).
6. **Risques de dérive sémantique** : §5 R1–R9, dont l'erreur avérée T2.
7. **Arbitrages PO/Lead** : §8 (7 points).

*Prochaine étape recommandée (hors code) : décision PO sur #151 incluant la
correction T2, puis qualification des 15–20 recettes du §6, puis seulement
spécification du POC READ. Design Expert et synthèse croisée restent dus pour
clore #166.*
