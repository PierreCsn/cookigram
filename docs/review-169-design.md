# Contre-review Design Expert — Meal Composition Layer (#169)

> **Mandat :** issue #169 — challenger #149 (CLOSED) et #151 (OPEN, décision PO pendante)
> du point de vue **expérience utilisateur et authoring**.
> **Scope strictement read-only :** aucun code produit modifié, aucun contrat
> versionné touché, aucune migration de recette.
> **Rôle :** Design Expert — la sémantique culinaire fine relève du Recipe Expert,
> l'exécution du Cooking Execution Expert, les surfaces agentiques de la review
> #166 (`docs/mcp-review-166-design.md`, `docs/mcp-review-166-recipe.md`).
> **Date :** 2026-09-05 — worktree `review/issue-169-design`.
> **Statut des sources :** #149 CLOSED (PDR-0011, taxonomie v1 validée) ·
> #151 OPEN (forme objet `required: true` recommandée, **non validée PO**) ·
> #150 EPIC · #152 / #154 / #160 / #156 / #163 OPEN.
> Corpus local : 162 recettes, **0 bloc `meal:`** à la date de rédaction.

**Position de lecture :** ne pas chercher à confirmer le modèle. Chercher ce qui
doit rester invisible pour l'utilisateur, ce qui est prématuré, et où le contrat
devient trop rigide pour être encore inversé à coût raisonnable.

---

## 1. Ce qui est confirmé (à ne pas rouvrir)

| # | Point | Pourquoi c'est bon pour l'UX / l'authoring |
|---|-------|---------------------------------------------|
| C1 | Tri-state `complete \| partial \| component` + `unknown` implicite (jamais `complete` par défaut) | L'absence d'information ne doit **jamais** se rendre comme une promesse positive. `unknown` = pas de badge, pas d'avertissement, planification libre (cf. §6). C'est le seul défaut sûr. |
| C2 | `role` dimension **séparée** de `completeness`, scalaire, facultative | Deux questions utilisateur distinctes : « est-ce un repas ? » vs « qu'est-ce que c'est ? ». Un seul axe obligerait à des états composites illisibles (`partial-main-needs-starch` comme « type »). |
| C3 | `complete` ≠ équilibré nutritionnellement | Évite un badge mensonger (« repas complet » lu comme « repas équilibré ») et un conflit frontal avec PDR-0010 (`vitality / pleasure / balanced`). Deux badges coexisteront peut-être un jour ; les confondre aujourd'hui serait une faute UX. |
| C4 | Données **éditoriales, déterministes**, aucun LLM à l'exécution | La suggestion d'accompagnement est une promesse de confiance. Une valeur inférée au runtime est instable, intestable, inexpliquable. L'assistance LLM reste cantonnée à la proposition côté auteur, validée avant publication. |
| C5 | **Aucune inférence depuis tags / ingrédients / titres / portions** | Le corpus prouve le danger : `curry-poulet-noix-coco.gram` porte le tag implicite « curry » et serait classé « sans féculent » par heuristique, alors que la recette **intègre 200 g de riz basmati + légumes Varoma** (cf. §4, CE-2). L'inférence produit des suggestions fausses avec aplomb. |
| C6 | Relations `needs` / `benefits_from` **réservées aux `partial`** | Un `complete` qui déclare des besoins se contredit à l'écran (« complet mais il manque quelque chose »). Un `component` qui prescrit son repas parent inverse la relation d'usage. La règle est un garde-fou d'affichage autant que de modélisation. |
| C7 | Exclusion de `starter` / `dessert` de la taxonomie v1 | Ce sont des **services** (ordre dans le repas), pas des rôles de composition (fonction structurelle). Les mélanger ferait poser à l'auteur une question qu'il ne se pose pas (« est-ce un starter ou un starch ? ») et polluerait le filtrage par besoin. |
| C8 | Migration **additive et progressive** (15–20 recettes, `unknown` par défaut) | Le seul rythme compatible avec la vérification recette par recette (corps réel, pas titre). Migrer tout le corpus d'un coup garantirait des erreurs type CE-2 à l'échelle. |
| C9 | Distinction `needs` (requis) vs `benefits_from` (conseillé) comme **deux listes** | Les deux correspondent à deux traitements UI réellement différents : **l'exigence** (état bloquant doux, « à prévoir ») vs **la recommandation** (nudge, « idéal avec »). Fusionner les deux ferait perdre cette nuance ; c'est la partie du schéma #151 qui mérite de survivre. |

---

## 2. Ce qui doit être simplifié

### S1. `required: true` dans `needs` — champ redondant à supprimer (recommandation centrale)

Question explicite de #169 : **« `required: true` apporte-t-il réellement une
information alors que l'objet est déjà dans `needs` ? » Réponse Design : non.**

```yaml
# Forme recommandée (listes simples — cf. contrat minimal §5)
needs: [starch]
benefits_from: [vegetable]

# Forme à rejeter en v1 (objet à champ tautologique)
needs:
  - role: starch
    required: true
```

Arguments :

1. **Zéro consommateur.** Aucune UI, aucun planner, aucun tool MCP, aucun
   validateur ne lit aujourd'hui autre chose que l'appartenance à la liste. Un
   champ sans lecteur est du poids mort de contrat.
2. **Validation tautologique.** La règle « `required` doit être présent et égal
   à `true` » ne détecte que des erreurs que la forme simple **rend impossibles**
   (on ne peut pas écrire `required: false` dans une liste de scalaires). On
   complexifie le schéma pour ensuite tester la complexité.
3. **Friction d'authoring.** L'auteur (humain ou skill d'import) doit produire un
   objet à deux champs au lieu d'un mot, avec un mode d'échec en plus
   (`required: false`, `required: "yes"`, champ oublié). Chaque friction
   d'authoring se paie en qualifications bâclées — exactement ce que CE-2 montre
   qu'on ne peut pas se permettre.
4. **Coût d'inversion asymétrique.** Ajouter un champ plus tard (si un vrai
   besoin naît : portion, variante, alternative) est une migration additive
   classique. Retirer un champ figé dans le **contrat public versionné
   (`cookigram-contract` v1.0.0 épinglé, `docs/PUBLIC-CONTRACT.md`)**, consommé
   par Core, le planner et le MCP, est une rupture. La stratégie « simple
   maintenant, étendre si besoin prouvé » est la seule prudente.
5. **L'argument « auto-documenté / extensible » ne tient pas.** `needs: [starch]`
   se lit aussi bien que l'objet, et l'extensibilité sans cas d'usage actuel est
   précisément l'extensibilité prématurée que #169 demande de traquer (cf. §7).

> Statut gouvernance : **recommandation expert** (Design), en désaccord assumé
> avec la recommandation Recipe/Cooking de #151 sur ce seul point. **Décision PO
> requise (D1).** Le fond sémantique de #151 (deux listes, rôles canoniques,
> règles v1) n'est pas contesté — seule la forme objet l'est.

### S2. Taxonomie `role` : confirmer les 7 valeurs comme **identité**, restreindre les **cibles de besoins**

La taxonomie v1 (`main, starch, vegetable, sauce, salad, bread, condiment`) est
validée PO : **ne pas la rouvrir**. Mais #169 pose les bonnes questions
(`salad` vs `vegetable` ? `bread` vs `starch` ? fonction vs type d'aliment ?).
La sortie Design n'est pas de retailler la liste, c'est de distinguer **deux
usages aux exigences différentes** :

- **`role` = identité du composant** (« qu'est-ce que c'est ? ») : 7 valeurs OK.
  `bread` (focaccia, pain) et `salad` (salade froide) aident le parcours et le
  filtrage catalogue. `condiment` vs `sauce` (quantité/usage) aide l'auteur à
  qualifier vinaigrette et béarnaise sans les confondre.
- **`needs` / `benefits_from` = cibles de besoin** (« qu'est-ce qui manque ? ») :
  ici la granularité fine est un **risque de fragmentation du matching**. Un
  `needs: [bread]` ne matchera jamais un `component/starch` (riz), et un
  `needs: [salad]` jamais un `component/vegetable` — alors que culinairement le
  besoin est couvert. Résultat UX : « aucune suggestion » dans un corpus qui en
  regorge. Or fonctionnellement, `bread` **est** un `starch` et `salad` **est**
  (le plus souvent) un `vegetable` froid.

**Recommandation :** documenter que les cibles de besoins utilisent en priorité
`starch`, `vegetable`, `sauce` (qui couvrent ~95 % des besoins réels :
porc au caramel→riz, steak→garniture, curry→féculent), les autres rôles restant
possibles mais exceptionnels et justifiés. Cela ne change pas le schéma, ne
rouvre pas la décision PO #149, et protège la qualité des suggestions.

Cas limites traités par cette lecture :

- **Shakshuka + pain** : préférence, pas besoin → `benefits_from: [starch]`
  suffit, pas besoin d'un `needs: [bread]` qui naggerait l'utilisateur.
- **Gratin de chou-fleur** (`component/vegetable` par défaut éditorial) : un
  besoin `vegetable` le propose ; un besoin `salad` l'exclurait à tort.
- **Sauce / condiment comme besoin** : quasi jamais structurel ; si un auteur
  écrit `needs: [condiment]`, c'est un signal de sur-modélisation à relever en
  review, pas un cas à optimiser.

> Statut gouvernance : **recommandation expert**. **Décision PO/Lead requise
> (D2)** : subset préférentiel documenté vs taxonomie pleine ouverte comme
> cibles.

### S3. `benefits_from` : conserver en v1, mais sous surveillance d'usage

Le champ gagne sa place (C9 : nudge vs exigence), mais c'est le champ le plus
« mou » du contrat : frontière éditoriale floue (cf. steak : garniture « requise
ou très fortement attendue » ?), risque de remplissage systématique
(« benefit `vegetable` » partout = bruit). **Recommandation :** le conserver en
v1 **facultatif**, mesurer sur les 15–20 premières qualifications la part de
`benefits_from` qui produisent une suggestion réellement retenue, et trancher sa
pérennité à ce moment-là (D5). Ne pas en faire un champ attendu par les
consommateurs : le planner et le MCP doivent être utiles avec `needs` seul.

### S4. Rôle unique, pas de multi-rôles — confirmer le report

Le gratin « accompagnement ou plat » ne justifie pas un `role: [vegetable,
main]`. La règle « intention éditoriale par défaut, ou `unknown` » suffit, et
l'**override utilisateur dans le planner** (§6) est la soupape, pas un second
rôle. Tout multi-rôle en v1 doublerait la combinatoire de matching pour des cas
que le corpus ne démontre pas encore.

---

## 3. Ce qui doit rester invisible (vocabulaire interne ≠ langage utilisateur)

Aucun des termes du modèle ne doit apparaître tel quel dans l'UI, le planner ou
les réponses agentiques. Table de correspondance recommandée :

| Interne | Rendu utilisateur (FR) | Contexte |
|---|---|---|
| `partial` + `needs` | « **À prévoir :** riz » / « À compléter avec un féculent » | Fiche recette, planner |
| `partial` + `benefits_from` | « **Idéal avec :** des légumes » / « Ça marche aussi avec… » | Suggestion douce, jamais bloquante |
| `complete` | **Rien** (absence de friction = fonctionnalité) ou « Repas complet » discret | Ne jamais badger positivement par défaut ; la retenue est une qualité |
| `component` | « **Accompagnement** » (pas « composant ») | Contexte de complétion, filtre catalogue `dish / component` |
| `unknown` | **Rien du tout.** Ni badge, ni avertissement, ni « non classé » | Fiche et planner pleinement utilisables (exigence #160) |
| `needs` / `benefits_from` / `completeness` | **Jamais affichés** | Jargon de modélisation, pas de cuisine |
| `starch` / `vegetable`… | « féculent », « légumes », « sauce »… | Libellés FR métier dans l'UI ; l'anglais reste au contrat |

Principes :

1. **`unknown` est un droit, pas un manque.** 162 recettes sur 162 sont
   `unknown` aujourd'hui ; si l'UI stigmatise cet état, elle stigmatise tout le
   catalogue. Le planner #160 l'exige déjà dans ses critères d'acceptation.
2. **Le requis se dit fermement mais sans jargon, le conseillé se dit légèrement.**
   « À prévoir : riz » (exigence) vs « Idéal avec : une salade » (nudge).
   Inverser les tons (nagger sur une préférence, murmurer sur un vrai manque)
   est le premier risque UX du modèle — d'où l'importance de S2/S3.
3. **La forme objet `required: true`, si elle était retenue, fuirait vers
   l'authoring** (skill d'import, formulaires, docs auteur). La forme simple se
   traduit naturellement en UI d'authoring : deux listes à cocher (« À prévoir »
   / « Idéal avec »). C'est un argument d'authoring pour S1, pas seulement de
   schéma.

---

## 4. Contre-exemples UX (scénarios #169 passés au modèle)

| # | Scénario | Ce que le modèle dit | Leçon Design |
|---|---|---|---|
| CE-1 | Porc au caramel + riz + légume | `partial/main`, `needs: [starch]`, `benefits_from: [vegetable]` | **Cas nominal.** UI : « À prévoir : riz → Riz jasmin » + « Idéal avec : légumes ». Le parcours compléter→cuisiner (#153) vit ou meurt ici. |
| CE-2 | Curry coco **avec riz intégré** (`curry-poulet-noix-coco.gram` : 200 g riz basmati + légumes Varoma, « Curry complet… avec riz basmati et légumes ») | La table #151 le classe `partial` + `needs: [starch]` — **faux contre le corps de la recette** (déjà signalé côté Recipe). Par critères #149 : `complete/main`. | **L'UI ne sera jamais plus intelligente que la qualification.** Une fiche « À prévoir : riz » sur un plat qui en contient est une faute de confiance impardonnable. D'où : vérification auteur contre le corps (D7), jamais de rattrapage runtime, et `unknown` préféré à une qualification douteuse. |
| CE-3 | Steak + accompagnement | `partial/main`, besoin garniture « requis ou très attendu » | **Frontière requis/conseillé floue.** L'UI doit formuler mou même pour un besoin fort : « Classique avec : … » plutôt qu'injonction. Le modèle ne porte pas de degré — tant mieux, c'est à la présentation de doser. |
| CE-4 | Curry avec ou sans riz inclus | Deux recettes sœurs, deux statuts (`curry-poulet-fruits-riz` = `complete`, curry sans féculent = `partial`) | Le modèle tient **si** la qualification suit la recette et non le mot « curry ». Contre-exemple parfait de l'interdiction d'inférer (C5). |
| CE-5 | Soupe (entrée / plat léger / repas selon portion) | `unknown`, aucune relation | **Test d'acceptation `unknown`.** La soupe doit se planifier, s'afficher, se cuisiner sans aucun badge ni friction. Si un consommateur exige `meal`, c'est le consommateur qui a tort. |
| CE-6 | Salade César au poulet (accompagnement vs salade-repas) | `unknown` tant que l'intention éditoriale (portion) n'est pas tranchée | Ne pas créer un état « ça dépend ». L'auteur tranche ou s'abstient ; le planner (override) absorbe le reste. |
| CE-7 | Gratin de chou-fleur (accompagnement typique, plat végétarien possible) | `component/vegetable` par défaut éditorial | Si l'utilisateur le planifie en plat, **le planner ne doit pas le contredire** : l'override utilisateur prime toujours sur l'intention canonique. La rigidité acceptable du modèle a pour contrepartie la souplesse obligatoire du planner. |
| CE-8 | Pizza Margherita, ramen, one-pot, lasagnes, jambalaya | `complete/main`, aucune relation | **La retenue comme fonctionnalité.** Aucune suggestion, aucun badge : le modèle sait aussi se taire. Toute UI qui « propose quand même quelque chose » sur un `complete` trahit le contrat. |
| CE-9 | Shakshuka + pain éventuel | `complete/main`, pas de `needs` ; éventuellement `benefits_from` | Distinguer préférence et besoin structurel : modéliser le pain en `needs` produirait du nagging (« il vous manque du pain ») sur un repas autonome. |
| CE-10 | Repas de plusieurs petits composants (assiette composée) | Aucun état « assemblé » requis | **Argument YAGNI.** Le planner assemble librement ; aucun 4ᵉ état `assembled`/`platter` n'est nécessaire en v1. Le jour où un besoin métier le démontrera, on étendra — pas avant. |
| CE-11 | Auteur face au schéma (authoring) | `- starch` vs `- role: starch` + `required: true` | Le mode d'échec `required: false` n'existe pas en forme simple. **La forme la plus sûre est celle où l'erreur est inexprimable.** Argument décisif pour S1 côté authoring. |

---

## 5. Contrat minimal recommandé maintenant

```yaml
meal:                                   # bloc facultatif ; absent = unknown
  completeness: complete | partial | component   # obligatoire si meal présent
  role: main | starch | vegetable | sauce | salad | bread | condiment  # facultatif, scalaire
  needs: [starch]                       # facultatif, partial uniquement, liste de rôles (scalaires)
  benefits_from: [vegetable]            # facultatif, partial uniquement, liste de rôles (scalaires)
```

Règles déterministes (inchangées de #151 moins la forme objet) :

1. `meal` absent ou sans `completeness` → `unknown`, jamais `complete`.
2. `needs` / `benefits_from` autorisés **uniquement** sur `partial`.
3. Cibles = rôles canoniques #149 ; jamais un nom de recette ni un tag.
4. Pas d'intersection `needs` ∩ `benefits_from`, pas de doublon.
5. Listes vides omises ; absence = « aucune relation déclarée ».
6. Aucune déduction depuis tags, ingrédients, portions, titres.
7. Aucune contrainte de durée / équipement / nutrition / sensoriel dans la
   relation (relève de #154 / PDR-0010 / #98 / #51).
8. Cibles de besoins : `starch`, `vegetable`, `sauce` par défaut ; autres rôles
   exceptionnels et justifiés (cf. S2, sous réserve D2).

Validation : `meal` est une map ; `completeness` enum obligatoire ;
`role` scalaire enum ; `needs` / `benefits_from` listes de scalaires enum.
**Trois règles de validation disparaissent avec l'objet** (champ `required`
présent / booléen / égal à `true`) : c'est la mesure de la simplification.

---

## 6. Implications Meal Planner #160 (consommateur, pas co-définition)

1. **Tolérance `unknown` totale** (critère d'acceptation #160 déjà écrit) :
   semaine visualisable, ajout/déplacement/remplacement/suppression, portions —
   tout fonctionne sans `meal`. Le planner consomme le modèle quand il existe,
   ne l'exige jamais.
2. **L'override utilisateur est la soupape du modèle rigide** (CE-7) : toute
   suggestion « À prévoir » doit pouvoir être ignorée, remplacée, supprimée sans
   friction. C'est dans le planner — pas dans un 4ᵉ état — que vit la
   flexibilité.
3. **Pas de seconde sémantique locale** : interdiction de réinventer
   `completeness`/`needs` dans le front ; adapter isolé si le contrat bouge
   (forme simple vs objet). Si S1 est retenu, l'adapter reste trivial ; si
   l'objet est figé, l'adapter devra porter la tautologie — coût concret de la
   complexité.
4. **Présentation** : les suggestions de complétion utilisent le vocabulaire §3
   (« À prévoir », « Idéal avec »), jamais le brut. Un `complete` ne déclenche
   rien. Un `unknown` ne déclenche rien non plus.
5. **Shopping Planner futur** : la projection planning → recettes → portions →
   ingrédients est indépendante de `meal` ; la complétion enrichit le panier,
   elle ne le conditionne pas.

---

## 7. Implications MCP #156 / #163 (ne pas figer le modèle dans les surfaces)

En complément de la review #166 (plafond v1 : 6 tools d'intention,
`complete_meal` internalisant besoins/composants/faisabilité, contrat
d'ignorance explicite) :

1. **Aucune sérialisation du bloc `meal` brut** tant que #151 n'est pas tranchée
   PO. Exposer aujourd'hui `needs: [{role, required}]` créerait une variante
   fantôme irréversible (même alerte côté Recipe). Les tools d'intention
   (`describe_meal_needs`, `complete_meal`) portent le statut et une
   `explanation` en langage naturel ; la forme de stockage reste derrière
   l'adapter Core.
2. **La forme simple est aussi la forme MCP la plus sûre** : un payload
   `needs: ["starch"]` n'a pas de champ à mal interpréter côté agent
   généraliste (`required: false` inventé par un LLM n'est pas un scénario
   théorique). S1 protège donc aussi la couche agentique.
3. **`unknown` comme réponse légitime** : `describe_meal_needs` sur recette non
   qualifiée (100 % du corpus aujourd'hui) retourne `status: unknown` +
   explication, jamais une complétion devinée. Le garde-fou UX §3 vaut pour
   l'agent.
4. **Session cuisine / vocal / scheduler** : inchangé depuis #166 — reporté en
   v2 (pas de session partagée, timers liés au DOM, solveur non démarré).
   Aucune primitive de session ne doit naître du besoin de « faire joli » dans
   une démo MCP.
5. **Authoring séparé** : la qualification assistée (proposer `meal` à l'auteur,
   avec vérification corps-de-recette type CE-2) appartient à la surface
   authoring, jamais au MCP utilisateur.

---

## 8. Ce qui doit volontairement rester hors contrat (prématuré)

| Élément | Pourquoi pas maintenant |
|---|---|
| Champ `required` (ou tout champ d'objet dans `needs`/`benefits_from`) | Aucun consommateur ; voir S1 |
| Multi-rôles par recette | Aucun cas corpus démontré ; voir S4 |
| `starter` / `dessert` comme rôles | Services, pas fonctions de composition (C7) |
| 4ᵉ état (`assembled`, `platter`, « dépend du contexte ») | Le planner absorbe ces cas (CE-10, CE-6) |
| Contraintes durée / équipement / effort dans les relations | Relève de #154, après stabilisation |
| Score nutritionnel ou sensoriel dans `meal` | PDR-0010 et #98 sont des couches indépendantes |
| Cibles de besoins hors rôles (recette nommée, tag, ingrédient) | Casserait le matching et l'explicabilité |
| Migration de tout le corpus | 15–20 recettes vérifiées d'abord (C8), dont requalification de CE-2 |
| Sérialisation MCP du bloc brut | En attente D1/D6 |
| Solveur / ordonnancement / session vocale adossés à `needs` | #51, #154, axe vocal : consommateurs futurs, pas co-auteurs du contrat |

---

## 9. Incertitudes restantes (à instruire, pas à trancher à l'aveugle)

- **U1 — Frontière `salad` / `vegetable`.** Le Design tranche l'usage (S2), pas
  la botanique culinaire. Si le Recipe Expert démontre des besoins « salade »
  non couverts par « légume », rouvrir D2 avec exemples corpus.
- **U2 — Frontière requis / conseillé (steak, blanquette, traditions).**
  L'éditorial tranchera recette par recette ; l'UI amortit par la formulation
  (§3). Pas de 3ᵉ liste ni de degré : l'incertitude se gère en présentation,
  pas en schéma.
- **U3 — Rendement de `benefits_from`.** Mesurer sur les 15–20 premières
  qualifications (D5) avant d'en faire un pilier.
- **U4 — Coexistence des badges repas (`complet`) et nutrition (`vitality /
  pleasure / balanced`, PDR-0010).** Risque de double signal contradictoire
  (« repas complet mais plaisir »). À maquetter côté planner avant de figer un
  quelconque affichage conjoint.
- **U5 — Portions-dépendances (soupe, salade-repas).** La règle « intention par
  défaut ou `unknown` » tient si le planner offre l'override (CE-5/6/7).
  Vérifier sur prototype #160, pas sur papier.

---

## 10. Décisions PO / Lead demandées

| # | Question | Recommandation Design | Bloque |
|---|---|---|---|
| D1 | Listes simples vs objets `required: true` pour `needs`/`benefits_from` ? | **Listes simples** (§5). Seul point de désaccord avec la reco #151. | #151, contrat public, Core, MCP |
| D2 | Cibles de besoins restreintes (`starch/vegetable/sauce` par défaut) ou taxonomie pleine ouverte ? | **Subset préférentiel documenté**, autres rôles exceptionnels justifiés. | Qualité des suggestions, #152 |
| D3 | `unknown` = rendu nul + planification libre, y compris côté MCP (`status: unknown` explicite) ? | **Oui** — contrat d'ignorance partout. | #160, #156/#163 |
| D4 | Vocabulaire FR utilisateur (« À prévoir », « Idéal avec », « Accompagnement », silence sur `complete`/`unknown`) validé ou laissé à l'implémentation UX ? | Valider le principe (§3), laisser la formulation exacte à la maquette. | #153, #160 |
| D5 | `benefits_from` en v1 ou réévaluation après les 15–20 premières qualifications ? | **V1 facultatif + mesure d'usage**, pérennité tranchée ensuite. | #151 |
| D6 | Interdiction de sérialiser le bloc `meal` brut en MCP avant décision #151 ? | **Oui** — intention-level tools + `explanation` uniquement. | #156/#163 |
| D7 | Checklist auteur obligatoire : vérification contre le **corps** de la recette (féculent/garniture déjà présents ? dressage ?) avant toute qualification ? | **Oui** — process, coût faible, prévient les CE-2. | #151, #152, skill d'import |

> Gouvernance : ce document est une **recommandation expert** (Design). Il ne
> modifie ni PDR-0011 ni aucune décision PO. Les points D1–D7 nécessitent un
> arbitrage **Lead puis PO** avant de figer le contrat. Une fois tranchés :
> qualifier 15–20 recettes (dont correction CE-2), publier les valeurs dans le
> contrat versionné, puis seulement brancher planner et MCP dessus.

---

## 11. Alternatives rejetées et pourquoi (exigence #169)

1. **Objet `needs` avec `required: true`** — rejeté : champ sans lecteur,
   validation tautologique, friction d'authoring, coût d'inversion élevé (S1).
2. **Taxonomie réduite (fusion `salad`→`vegetable`, `bread`→`starch`)** —
   rejetée comme modification de `role` : la décision PO #149 est close et les
   valeurs aident l'identité/filtrage. La restriction porte sur les **cibles de
   besoins**, pas sur le vocabulaire (S2).
3. **4ᵉ état contextuel / assemblé** — rejeté : le contexte vit dans le planner
   (override) et le repas runtime, pas dans la recette canonique (CE-6/10).
4. **Inférence automatique depuis tags/ingrédients** — rejetée : CE-2/CE-4
   prouvent l'échec (C5).
5. **Suppression de `benefits_from`** — rejetée pour l'instant : la nuance
   exigence/nudge porte une vraie différence UI (C9), mais sous surveillance
   d'usage (S3/D5).
6. **Exposition MCP du modèle brut** — rejetée : figerait une discovery en cours
   dans une surface versionnée (D6, §7).

---

*Fin de la contre-review Design Expert — à confronter aux reviews Recipe et
Cooking Execution, puis synthèse Lead et arbitrage PO (D1–D7). Aucune
implémentation engagée.*
