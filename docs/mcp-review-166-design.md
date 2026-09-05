# MCP Review — Design Expert (issue #166)

> **Scope :** review read-only de #156 (EPIC MCP) et #163 (séparation MCP Core / MCP CookiGram),
> au prisme de l'expérience CookiGram existante.
> **Aucun serveur MCP codé, aucune modification de `cookigram-core`.**
> **Rôle :** Design Expert — surface **MCP CookiGram utilisateur** (la sémantique culinaire fine
> relève de la review Recipe Expert en miroir).
> **Date :** 2026-09-05 — worktree `review/issue-166-design`.

## 1. Référentiels relus

- #156 : vision, axes 1–8 (tools candidats, resources, READ/ANALYZE/WRITE, authoring, Meal Composition, sécurité, transport, vocal).
- #163 : séparation Core (déterministe, réutilisable) / CookiGram (usages utilisateur), règles de non-duplication métier.
- #166 : mandat de review croisée, principe `.gram = vérité culinaire / Core = vérité déterministe / CookiGram = expérience produit / MCP = interface agentique / LLM = intention + dialogue + orchestration`.
- Expérience existante : fiche recette → portions → checklist → courses (`menu_basket` côté core) → Mode Cuisine pas-à-pas (`templates/cook.html`, modules `cook.js`/`timers.js`, persistance `localStorage` `cookigram:<recipe>:step-id`), PWA offline mobile-first, principes `PRODUCT_PRINCIPLES.md` (cooking-first, 44 px, lisibilité à 1 m, zéro friction), `docs/MEAL_PLANNING_NUTRITION.md` (80/20, 30 plantes, `menu_basket` hebdomadaire), parcours discovery #150→#154 (complétude, `needs`/`benefits_from`, composants `.gram`, exécutabilité), Meal Planner #160/#139, Kitchen Scheduler #51/#92, Nest Hub #87 + commentaire de cadrage #156 (smartphone/tablette = référence, vocal = valeur, Nest = opportuniste).

## 2. Intentions utilisateur réellement utiles (priorisées)

| # | Intention (formulation utilisateur) | Ancrage produit | Avis Design |
|---|--------------------------------------|-----------------|-------------|
| U1 | « Trouve-moi une recette de X » | Catalogue + recherche existante | **Core-useful, v1.** |
| U2 | « Montre-moi cette recette pour N personnes avec mon matériel » | Fiche + `scaling` + `appliances`/`required_equipment` | **Core-useful, v1** — inclure portions + équipement en contexte, pas en tool séparé. |
| U3 | « Qu'est-ce qui manque pour en faire un vrai repas ? » | #151 (`needs`/`benefits_from`), #153 | **Utile, v1 READ/ANALYZE**, à condition de retourner `unknown` quand le modèle n'est pas stabilisé. |
| U4 | « Complète avec un accompagnement simple » | #152 (composants `.gram`), #153 (parcours compléter → cuisiner) | **Utile, v1** sous forme d'**opération métier unique**, pas de pipeline de micro-tools. |
| U5 | « Ajoute ce repas à mercredi soir / montre ma semaine » | #160, #139 | **Utile, v1 READ + WRITE最小** — le WRITE planning est le premier WRITE légitime. |
| U6 | « Prépare mes courses » (repas ou semaine) | `menu_basket`, #160 § Shopping Planner | **Utile, v1 ANALYZE** (calcul, pas de persistance opaque). |
| U7 | « Qu'est-ce que je fais maintenant en cuisine ? » (dont mains libres / vocal niveau 1–2) | Mode Cuisine, #51/#92, #87 | **Utile mais v2** : exige un modèle de **session d'exécution partagée** qui n'existe pas (état aujourd'hui en `localStorage` + DOM timers). Exposer des tools de session avant ce modèle = couplage prématuré. |
| U8 | « Vérifie / corrige / importe cette recette » (authoring) | Axe 4 #156 | **Non-utilisateur.** Reporter vers surface authoring séparée, jamais dans le MCP utilisateur v1. |

Non-intentions (à ne pas exposer comme tools) : « valide la syntaxe `.gram` pour moi » (besoin dev, pas utilisateur), « classe ton corpus », « ranke mes accords sensoriels » (#98), « résous mon RCPSP » (#51).

## 3. Niveau d'abstraction : action utilisateur vs primitive technique

Principe appliqué : **un tool = une intention U1–U6 complète et explicable**, pas une étape interne du raisonnement Core.

- ✅ Bon niveau : `search_recipes`, `get_recipe`, `complete_meal`, `build_shopping_list`, `get_week_plan`/`add_meal_to_plan`, `get_cooking_plan` (sous réserve §5).
- ❌ Trop bas niveau pour MCP : `get_missing_roles`, `find_components(role)`, `rank_pairings`, `check_execution_feasibility`, `resolve_ingredients`, `get_step_ingredients`, `get_active_timers`, `repeat_instruction`. Ce sont des **fonctions internes Core / produit**, pas des intentions. Les exposer force l'agent généraliste à réassembler la règle métier — exactement ce que #163 interdit (« le LLM ne doit pas devenir le moteur déterministe caché »).
- ❌ Trop couplé UI/session : `get_current_step`, `get_next_action`, `complete_step`, `report_delay`, `reschedule_meal` *tant que* la session cuisine n'est pas modélisée côté Core/produit (aujourd'hui : pas de session partagée, timers liés au DOM, progression en `localStorage`). Le POC vocal doit d'abord cibler PWA push-to-talk (décision #156) et faire émerger le modèle de session ; les tools suivront.

Règle proposée : **si un agent doit appeler plus de 3 tools pour répondre à une seule phrase utilisateur (ex. le pipeline `get_recipe → completeness → get_missing_roles → find_components → rank_pairings → check_feasibility` de l'axe 5 #156), l'abstraction est fausse.** Le pipeline appartient à Core/produit derrière un seul tool intentionnel (`complete_meal` / `analyze_meal`).

## 4. Nommage : lisibilité par un agent généraliste

| Nom actuel | Problème | Proposition |
|---|---|---|
| `check_meal` / `check_meal_completeness` | « check » ambigu (valide ? vérifie ? diagnostique ?) ; jargon `completeness` issu de #149, pas du langage utilisateur | `describe_meal_needs` (READ/ANALYZE, retourne `status: complete/partial/component/unknown` + `needs`/`benefits_from` + `explanation`) — le mot `completeness` reste dans le payload, pas dans le verbe |
| `suggest_components` vs `suggest_meal_components` vs `find_components` | Trois variantes pour la même idée ; `find` = recherche brute, `suggest` = recommandation | Un seul : `complete_meal` (action : rend un repas). La suggestion est un paramètre (`mode: suggest` vs `mode: apply`), pas un tool distinct |
| `compose_meal` vs `complete_meal` (#156 vs #163) | Doublon apparent | Ne garder qu'un verbe : `complete_meal` (compléter un plat partiel, cf. #153). `compose_meal` (assembler N plats ex nihilo) = **v2**, quand le modèle multi-recettes sera stabilisé |
| `generate_shopping_list` vs `build_shopping_list` | Doublon lexical | `build_shopping_list` (construit à partir d'un repas **ou** d'un plan — `source: meal | week_plan`), aligné sur `menu_basket`/`consolidate_*` existants |
| `schedule_meal` vs `schedule_cooking` vs `get_cooking_plan` | Confusion planning semaine / ordonnancement cuisine (#51) | `get_cooking_plan` = **lecture** du plan d'exécution (heure cible en entrée, timeline en sortie) ; aucun `schedule_*` mutant côté MCP v1. Le solveur OR-Tools reste interne Core |
| `validate_recipe` (surface utilisateur) | Besoin dev/authoring, pas utilisateur ; expose le jargon `.gram` | Retirer du MCP utilisateur v1 → réserver à MCP Core / authoring (`validate_recipe` y a sa place) |
| `get_recipe` | OK mais sous-spécifié | `get_recipe(slug, servings?, equipment?)` — le scaling et le filtrage matériel sont des **paramètres de contexte**, pas des tools (`scale_recipe` reste Core interne, appelé par le produit/MCP, jamais par le LLM directement) |
| `get_week_plan` / `add_meal_to_plan` | OK, ce sont les seuls noms déjà orientés intention | Conserver ; ajouter `remove_meal_from_plan`/`replace_meal_in_plan` ou un seul `update_week_plan(op: add|remove|replace|move)` — à trancher côté Core, pas 4 tools séparés |
| Tools vocaux (`complete_step`, `repeat_instruction`…) | Verbes d'UI, pas d'intention culinaire ; `repeat` = présentation, pas métier | Reporter (§7) ; le seul besoin vocal v1 = `get_cooking_plan` + lecture PWA existante |

Convention : verbes d'intention (`search/get/describe/complete/build/update`), anglais (cohérent avec le codebase et MCP), payload qui porte le vocabulaire métier (`role`, `needs`, `nutrition_profile`), jamais l'inverse.

## 5. READ / ANALYZE / WRITE — classification proposée (surface utilisateur v1)

**READ (sans effet de bord, idempotents) :** `search_recipes`, `get_recipe`, `get_week_plan`, `get_cooking_plan` (lecture d'un plan calculé à la demande, paramètres `target_time`, `servings`, `equipment` explicites).

**ANALYZE (calcul déterministe, sans effet de bord, à déléguer à Core) :** `describe_meal_needs` (= `check_meal` renommé), `complete_meal(mode: suggest)`, `build_shopping_list`. Idempotents, versionnés, avec forme d'erreur `unknown / insufficient_data` (§8).

**WRITE (effet persistant, périmètre minimal, auth explicite) :** `update_week_plan` (add/remove/replace/move), et uniquement lui en v1. Hypothèse #156 « aucun WRITE par défaut » conservée : WRITE = capability séparée/opt-in, journalisée, avec confirmation utilisateur pour `replace/remove`. Tout le reste (création/modif de recette, import, patch corpus, préférences persistantes, état de session cuisine) = **hors v1**, surface authoring ou future feature.

`validate_recipe`, `analyze_meal`, `scale_recipe`, `resolve_ingredients` : **pas des tools MCP CookiGram** — ce sont des capacités **Core** consommées en interne par les tools ci-dessus (cf. #163 : « CookiGram doit consommer Core plutôt que réimplémenter »).

## 6. Continuité recette → repas → planning → courses → cuisine

Chaîne cible (rappel #160) : `Recettes → Composition → Planning → Shopping → Courses → Cuisine (→ Scheduler)`.

| Transition | État actuel | Exigence MCP |
|---|---|---|
| Recette → repas | Discovery en cours (#151 vocabulaire instable, #152 pas de composants canoniques, #153 pas de parcours figé) | `describe_meal_needs`/`complete_meal` doivent accepter `unknown` et une explication, jamais inventer un `needs` ; **ne pas figer le modèle dans le contrat MCP** — adapter fin derrière le tool |
| Repas → planning | Prototype #160 à inspecter/améliorer, pas de contrat stable | `update_week_plan` minimal (créneau jour/moment + `recipe_slug` + `servings` + `meal_id` optionnel) ; ne pas exposer la cuisine interne du prototype |
| Planning → courses | `menu_basket`/`consolidate_*` existent côté core, extension hebdo + 30 plantes + 80/20 décrites dans `docs/MEAL_PLANNING_NUTRITION.md` | `build_shopping_list(source: week_plan)` = projection hebdo du existant, avec traçabilité recette→quantité et unités incompatibles conservées séparées ; ratio et plantes en **métadonnées explicatives**, jamais en score punitif |
| Repas/plan → cuisine | Mode Cuisine mono-recette solide (pas-à-pas, timers, voix locale, offline) ; multi-recettes = epic #51 non démarré | `get_cooking_plan` v1 = **mono-repas, lecture seule** (étapes ordonnées + timers + matériel) ; multi-recettes synchronisé = v2 derrière le solveur, pas un assemblage LLM de timelines |
| Cuisine live | Pas de session partagée (cf. §3), timers DOM-attachés | Bloquant pour tout tool mutant de session — voir §7 |

## 7. Risques de couplage UI (points durs)

1. **Resources `cookigram://meals/current` et `cookigram://equipment/my-kitchen`** : `current` suppose une session qui n'existe pas ; `my-kitchen` suppose un profil matériel/serveur de préférences qui n'existe pas. Exposer ces URI fige une architecture de state encore en discovery. **Recommandation :** v1 = paramètres explicites par appel (`equipment: [...]`, `servings`, `target_time`), resources limitées à `recipes/{slug}` (canonique `.gram` + vue simplifiée) et `ingredients/{id}` ; `meals/current`, `equipment/my-kitchen`, `corpus` brut = reportés.
2. **Pollution catalogue par les composants #152** : si chaque `riz blanc` devient une recette `.gram` ordinaire, `search_recipes` la remonte comme un plat. **Recommandation :** champ `role/component` filtrable (`kind: dish | component | all`, défaut `dish`), présentation produit différenciée — le MCP ne doit pas réinventer ce filtre, il le consomme.
3. **Meal Planner #160 comme contrat implicite** : le prototype ne doit pas devenir le schéma MCP par accident. **Recommandation :** isoler l'adapter (cf. #160 « isoler les adapters ») et faire du contrat MCP v1 un sous-ensemble volontaire, pas une sérialisation du state du prototype.
4. **Vocabulaire nutritionnel** : `nutrition_profile` (`vitality/pleasure/balanced`) non encore validé côté core, ne pas l'ajouter aux recettes prod avant le schéma (`docs/MEAL_PLANNING_NUTRITION.md` §3). **Recommandation :** MCP v1 n'expose ce champ qu'en lecture optionnelle + `unknown` toléré ; aucun tool ne **décide** d'un profil (calcul déterministe core ou `unknown`, jamais LLM).

## 8. Risques UX / agentiques

- **Explosion combinatoire** : 9 tools axe 1 + 5 axe 5 + 8 axe 8 + 7 #163 ≈ 20+ tools pour ~6 intentions → l'agent choisit mal, enchaîne, hallucine entre deux appels. **Mitigation :** v1 = **6 tools utilisateur** (§9), le reste internalisé Core.
- **LLM moteur caché** : assembler `find → rank → feasibility` côté agent = règle métier reconstruite dans le prompt, non testée, non versionnée. **Mitigation :** tests Core sur `complete_meal` (cas porc au caramel/riz jasmin, steak, curry, ramen, soupe, gratin — jeux #151), le MCP ne fait que transporter le résultat + `explanation`.
- **Devinette culinaire** : `needs`/`role` encore en discovery (#151 : requis vs conseillé, plats culturels, polyvalence selon portions). **Mitigation :** contrat d'ignorance explicite — `status: unknown`, `confidence`, `missing_data: [...]`, interdiction de compléter silencieusement ; la review Recipe Expert doit lister les cas `unknown` obligatoires.
- **WRITE silencieux** : `compose` qui écrit dans le plan, `schedule` qui réserve, `build_shopping` qui écrase un panier. **Mitigation :** seuls les WRITE nommés `update_*` mutent ; `complete/build/describe` = lecture ; toute mutation = `dry_run` par défaut envisageable + confirmation produit.
- **Confidentialité** : plan semaine, équipement, préférences = données utilisateur. **Mitigation :** séparation données publiques/corpus vs utilisateur (§ Axe 6 #156), auth si distant, logs des mutations, rate-limits anti-boucle d'agent.
- **Sécurité alimentaire / quantités** : scaling (`TODO` : `scaling.enabled:false` ex. blanquette), conversions US/impériales (#103), températures `^{120 C}` excluant TM31. **Mitigation :** `servings` validé contre `scaling.min/max`, refus explicite hors borne ; conversions uniquement via tables core sourcées, jamais estimées par le LLM.

## 9. Verdict tools : conserver / renommer / reporter

### 9.1 Conserver en v1 (surface utilisateur, 6 tools)

- `search_recipes(query, filters?, page?)` — READ. Filtres : `kind`, `tags`, `max_total_time`, `appliances`, `nutrition_profile?`. Pagination obligatoire.
- `get_recipe(slug, servings?, equipment?)` — READ. Retourne vue complète + quantités scalées **si** `scaling` le permet, sinon portion canonique + `scaling_note`.
- `get_week_plan(week?)` — READ.
- `update_week_plan(op, slot, meal)` — **seul WRITE v1**, capability séparée.
- `complete_meal(recipe_slug, servings?, equipment?, mode: suggest|apply)` — ANALYZE (suggest) ; `apply` ne persiste que via `update_week_plan`, jamais seul.
- `build_shopping_list(source)` — ANALYZE. `source: {meal…} | {week_plan…}`, traçabilité + unités séparées + métadonnées 80/20 / 30 plantes.

### 9.2 Renommer / repenser (pas de suppression métier, changement de forme)

- `check_meal*` → `describe_meal_needs` (voir §4).
- `compose_meal` + `suggest_components` + `find_components` + `rank_pairings` + `get_missing_roles` → fusionnés dans `complete_meal` (détail interne Core : `analyze_meal` + besoins #151 + composants #152 + faisabilité #154).
- `generate_shopping_list` → `build_shopping_list`.
- `schedule_meal` / `schedule_cooking` → `get_cooking_plan(target_time, servings, equipment)` **lecture seule** v1, mono-repas.
- `scale_recipe`, `resolve_ingredients`, `validate_recipe`, `analyze_meal`, `check_execution_feasibility` → **Core internes**, non exposés au MCP utilisateur (exposables au MCP Core/authoring).
- `get_recipe` enrichi des paramètres `servings`/`equipment` au lieu d'un tool de scaling séparé.

### 9.3 Reporter (explicitement hors v1)

- **Session cuisine mutante + vocal niveau 1–2** : `get_current_step`, `get_step_ingredients`, `get_active_timers`, `get_next_action`, `complete_step`, `repeat_instruction`, `report_delay`, `reschedule_meal`. Prérequis : modèle de session partagée device-agnostic (cf. décision de cadrage #156 : même état pour PWA smartphone/tablette/écran dédié, vocal par-dessus). POC = push-to-talk PWA d'abord.
- **Authoring** : `validate_recipe` (utilisateur), import, patch corpus, classification, audit — surface `cookigram-authoring-mcp` séparée ou profils de capabilities, jamais mélangée au MCP utilisateur.
- **Resources fragiles** : `cookigram://meals/current`, `cookigram://equipment/my-kitchen`, `cookigram://corpus` brut. V1 : `recipes/{slug}`, `ingredients/{id}` (+ `week_plan` si besoin, lecture).
- **Multi-recettes synchronisé / solveur** : `compose_meal` ex nihilo, `schedule_cooking` mutant, timeline multi-recettes — v2 après #154 (faisabilité) + #51 (solveur) + composants canoniques #152.
- **Transport distant/auth** (axe 7) : décision différée à juste titre ; v1 = stdio local adossé aux API Core stables, aucune logique métier dans l'adapter.

## 10. Capacités manquantes (à créer dans Core/produit, pas dans le MCP)

1. **Contexte d'appel standard** : `servings`, `equipment[]`, `target_time`, `dietary_exclusions[]`, `locale` — passé en paramètres, pas en state serveur implicite.
2. **Contrat d'ignorance** : enveloppe commune `{status, confidence, missing_data[], explanation}` pour `describe/complete/build/cooking_plan` quand #151/#152/#154 n'ont pas tranché.
3. **Explicabilité du `complete`** : `why: [...]` (rôle couvert, charge active ajoutée cf. #154, matériel partagé, maintien au chaud) — libellés utilisateur non-jargon (#153 : « requis / recommandé / alternative », jamais `needs` brut).
4. **Indicateur de complexité ajoutée** (#154) : `added_effort: trivial|moderate|demanding` + `+X min actives, parallélisables` — indispensable avant de proposer un 3e composant.
5. **Session d'exécution** (produit + Core) : état partagé `{meal_id, steps[], current_step, timers[], equipment_locks[]}` consommable par PWA, vocal et (plus tard) Cast — sans elle, aucun tool vocal.
6. **Filtre `kind: dish|component`** et composants canoniques #152 (riz jasmin/blanc, semoule, légumes vapeur/rôtis, salade, sauces élémentaires) avec variantes méthode (casserole/rice cooker/Thermomix/vapeur) sans explosion du catalogue.
7. **Versionnement + pagination + idempotence** : `contract_version` dans chaque réponse, `idempotency_key` sur `update_week_plan`, pagination `search_recipes`.
8. **Profils nutritionnels calculés, pas devinés** : `nutrition_profile`, ratio 80/20, 30 plantes = sorties déterministes core versionnées (`docs/MEAL_PLANNING_NUTRITION.md` jalons 1–3) ou absentes, jamais inférées par l'agent.

## 11. Implications assistant vocal (détaillées)

La cible #156-axe 8 (`micro → STT → LLM → MCP → Core → TTS`) est saine **si** le LLM reste dialogue et Core vérité d'exécution. En l'état :

- **Faisable sans MCP session** : niveau 1 « Suivant / Répète / Combien de temps ? » via la PWA existante (commandes vocales locales déjà dans `cook.js`) + `get_recipe`/`get_cooking_plan` en lecture.
- **Infaisable proprement** : niveau 2 contextuel (« quelle quantité de crème ? », « et après ? », « je peux remplacer ? », « j'ai 5 min de retard ») sans session partagée + timers serveur + recalcul solveur < 100 ms (§ #92). Un tool `report_delay` sans moteur derrière = promesse mensongère.
- **Risques spécifiques voix** : latence STT+LLM+TTS vs geste cuisine, homophones d'ingrédients/quantités (sécurité : « 100 g » vs « 100 ml », sel vs sucre), confirmations mains libres ambiguës pour les WRITE, bruit de cuisine/hotte, confidentialité micro. **Mitigation :** grammaire fermée niveau 1 en local d'abord ; niveau 2 = réponses courtes groundées sur l'étape courante (`step_id` cité dans chaque réponse) + reformulation chiffrée systématique (« 100 grammes de vin blanc, c'est bien ça ? ») ; aucun WRITE vocal en v1 sauf `update_week_plan` avec confirmation explicite.
- **Nest Hub** : suivre la décision de cadrage #156 — device-agnostic, POC smartphone/tablette, Cast/Nest opportuniste plus tard. Le MCP ne doit contenir **aucune** primitive Cast.

## 12. Décisions PO / Lead nécessaires (à trancher avant tout code MCP)

1. **Périmètre v1** : valider les 6 tools §9.1 + 1 WRITE (`update_week_plan`) comme plafond. Tout le reste = §9.2/9.3.
2. **Un vs deux serveurs** : trancher `cookigram-mcp` (utilisateur) vs `cookigram-authoring-mcp` — recommandation Design : **deux surfaces, un socle Core commun** (option « API commune + deux façades » de #156-axe 4), pour ne jamais exposer le WRITE corpus aux assistants utilisateur.
3. **Politique WRITE** : opt-in explicite, journalisation, confirmation pour `replace/remove`, `dry_run` par défaut ? Valider avant de spécifier `update_week_plan`.
4. **Modèle de session cuisine** : inscrire au backlog produit (prérequis vocal + multi-device) ou assumer durablement le mono-appareil `localStorage` — dans le second cas, retirer tout tool de session du discours MCP.
5. **Nest Hub** : confirmer le déclassement en opportuniste (cf. #156) pour clore #87 en attente du POC PWA.
6. **Nommage FR vs EN** : confirmer l'anglais technique (`describe_meal_needs`, `build_shopping_list`) avec libellés FR en payload/UX — cohérent avec `.gram`/codebase.
7. **Garde-fou `unknown`** : valider que le MCP a le droit — et le devoir — de répondre « je ne sais pas » (cf. review Recipe Expert pour les cas obligatoires : #151 portions-dépendantes, #152 composants manquants, #154 surcharge).
8. **Articulation avec #160** : le prototype Meal Planner peut-il diverger temporairement du contrat MCP v1 via adapter, sans le figer ? (Oui recommandé.)

## 13. Recommandations concrètes (ordonnées)

1. **Figer le plafond v1 à 6 tools** (§9.1) et interdire tout nouveau tool utilisateur sans arbitrage Lead/PO.
2. **Spécifier d'abord les contrats** (schémas I/O, erreurs `unknown/insufficient_data/incompatible_equipment/out_of_scaling_bounds`, pagination, `contract_version`) avant tout prototype de serveur — le serveur reste « fine couche d'adaptation » (#156).
3. **Internaliser les micro-tools** : `get_missing_roles/find/rank/feasibility` deviennent des étapes Core testées derrière `complete_meal`, avec jeux d'essai #151 (porc au caramel, steak, curry, ramen, soupe, gratin).
4. **Livrer `kind: dish|component`** + 8–12 composants canoniques #152 comme prérequis de `complete_meal` utile.
5. **Exposer `added_effort` + `why`** dans `complete_meal` (règle #154 : préférer le légèrement moins parfait mais trivialement parallélisable).
6. **Limiter les resources v1** à `recipes/{slug}` + `ingredients/{id}` ; bannir `meals/current` et `my-kitchen` tant que session/préférences non modélisées.
7. **POC vocal = PWA push-to-talk** sur smartphone/tablette, niveau 1 local + lecture `get_cooking_plan` ; niveau 2 et session partagée = chantier produit dédié avec Cooking Execution Expert.
8. **Séparer l'authoring** physiquement (serveur ou façade distincte, pas de WRITE corpus dans le MCP utilisateur).
9. **Journaliser et limiter** : auth/opt-in WRITE, idempotence, rate-limits, aucune donnée privée dans les resources, logs des mutations.
10. **Synthèse avec la review Recipe Expert** : produire le tableau commun §7 de #166 (conserver/renommer/reporter, capacités Core manquantes, dérives sémantiques, arbitrages) avant de lancer toute implémentation #156/#163.

## 14. Réponses aux questions de review #166 (Design)

- *Surfaces #163 assez distinctes ?* Oui en intention, à durcir : Core = verbes déterministes (`validate/analyze/scale/resolve`), CookiGram = verbes d'intention (§4). Tout tool CookiGram qui ne se formule pas en phrase utilisateur (« complète », « prépare mes courses ») appartient à Core ou n'existe pas encore.
- *Tools Core réutilisables hors MCP ?* Seulement si le MCP n'en duplique aucun — d'où §5 : le MCP utilisateur **appelle** Core, ne le réexpose pas.
- *Tools CookiGram = intentions ?* 6/20 aujourd'hui. Les autres sont des détails d'implémentation ou du futur (session, solveur).
- *Agent généraliste sans connaître `.gram` ?* Possible **si** renommage §4 + enveloppe `unknown` + `explanation` en langage naturel. Impossible avec `needs`/`benefits_from`/`completeness` bruts.
- *Erreurs/absences représentables ?* Pas encore — contrat §10.2 à créer.
- *WRITE séparés ?* Partiellement — `update_week_plan` isolé + authoring séparé (décision D2/D3) achèvent la séparation.
- *Capacités appartenant ailleurs ?* Oui : scaling/conversions/solveur/profils nutritionnels = Core ; parcours compléter→cuisiner, présentation composants, session = produit ; micro-rankings = internes.

---

*Fin du rapport Design Expert — à confronter à la review Recipe Expert puis synthèse commune (§7 de #166). Aucune implémentation MCP engagée.*
