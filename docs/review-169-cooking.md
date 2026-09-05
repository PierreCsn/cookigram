# Revue Cooking Execution — Issue #169 : challenger #149 / #151 depuis l'exécution réelle

> **Rôle** : Cooking Execution Expert.
> **Scope** : repas composés, charge active, portions, maintien au chaud, équipement,
> composants, et frontière avec #154 / #51.
> **Contrainte de mission** : aucun scheduler codé, aucune recette modifiée.
> **Références** : #149 (complétude / rôle), #151 (`needs` / `benefits_from`),
> #150 (Epic Meal Composition), #152 (composants `.gram`), #154 (exécutabilité),
> #51 (Kitchen Scheduler), #91 (effort / élasticité), #93 (équipements / transitions),
> #98 (accords sensoriels — hors scope volontaire).

---

## 1. Thèse en une page

Le modèle `needs` / `benefits_from` proposé en #151 est **culinairement juste mais
exécution-naïf** : tel quel, il décrit *ce qui manque dans l'assiette* sans dire
*ce que l'ajout coûte en cuisine*. Appliqué naïvement, il produira des repas
gustativement cohérents mais **inexécutables par une personne seule** (deux minutes
simultanées, même bol robot sans lavage, four monopolisé à une autre température,
service qui s'effondre pendant qu'on dresse).

Ma recommandation :

1. **Garder `needs` / `benefits_from` purement structurels et culinaires**
   (QUOI manque), sous forme **liste simple**, sans y cacher de contraintes de
   planning, d'équipement ou de difficulté.
2. **Reporter toute la faisabilité d'exécution vers #154** (règles de garde-fou
   consommant #91 / #93), qui juge si une combinaison est raisonnable **avant**
   #51, lequel calcule QUAND/HOW.
3. **Rendre `needs` conditionnel au contexte** (portions, usage entrée vs plat,
   tradition culturelle étiquetée comme telle) au lieu d'un booléen statique
   `required: true` qui ment dans la moitié des cas réels.
4. **Ne figer ni la taxonomie des rôles ni le statut des composants (#152)**
   dans le contrat #151 : ce sont des décisions PO encore ouvertes.

Le découpage que je défends :

```text
#149/#151  → QUOI manque ? (structure culinaire, déclaratif, auteur)
#154       → EST-CE RAISONNABLE ? (garde-fous d'exécution, avant solveur)
#51        → QUAND / COMMENT ? (ordonnancement, solveur CP-SAT)
#98        → LEQUEL choisir parmi les candidats valides ? (classement sensoriel)
```

Si une information sert à répondre à « est-ce raisonnable ? » ou à « quand ? »,
**elle n'a pas sa place dans `needs`**.

---

## 2. Ce que je confirme (depuis le plan de travail)

- **La distinction `complete / partial / component` (#149) est utile en exécution.**
  Elle répond à une vraie question de cuisine : « est-ce que je peux lancer ça
  seul un soir de semaine ? ». Un one-pot (`one-pot-poulet-riz-legumes`) se lance
  seul ; un `porc-au-caramel` seul laisse quatre personnes sur leur faim sans riz.
  Cette dimension doit rester.
- **`needs` exprime un vrai manque structurel, pas un score de goût.**
  « Porc au caramel → féculent » n'est pas une préférence (#98), c'est de la
  structure de repas. Confirmer la séparation #151 vs #98.
- **La complétude n'est ni la nutrition ni l'accord sensoriel.**
  Confirmer le garde-fou de #149 : un ramen complet n'est pas « équilibré », il
  est seulement servable seul.
- **Les composants doivent être des objets exécutables (#152).**
  Confirmé depuis l'exécution : si le riz suggéré n'a ni durée, ni ressource, ni
  pas-à-pas, le scheduler #51 ne peut rien en faire et la liste de courses reste
  fausse. Mais c'est une décision #152, pas un prérequis pour figer #151.

---

## 3. Contre-exemples exécution (corpus réel, vérifié dans ce dépôt)

Chaque cas suit le même gabarit : *ce que dit le modèle naïf → ce qui casse en
vraie cuisine → ce que ça implique pour le contrat*.

### CE-1. Porc au caramel + riz : le « bon » exemple qui cache un conflit bol

- **Modèle naïf** : `porc-au-caramel` (`recipes/porc-au-caramel.gram`, TM6/TM7,
  bol monopolisé en 3 phases haute température) `needs: [starch]` → suggérer
  « riz Thermomix mode rice-cooker » (`recipes/riz-thermomix-mode-rice-cooker.gram`).
- **Réalité d'exécution** : les deux préparations veulent le **même bol unique**
  en séquence, avec transvasement + rinçage entre les deux (#93 : *cleaning delay*).
  Rien ne peut se paralléliser. Le repas reste faisable (les deux plats tiennent
  bien au chaud), mais il est **strictement séquentiel** : ~20 min de plus que ce
  que deux durées additionnées naïvement suggèrent.
- **Leçon** : `needs: [starch]` est correct culinairement, mais le **choix du
  candidat** (riz casserole / rice-cooker / four / Thermomix) change radicalement
  la charge et le planning. Cette information d'équipement appartient à #154/#51,
  **pas** à `needs`. `needs` ne doit pas encoder « riz Thermomix » ni « +25 min ».

### CE-2. Faux-filet sous-vide + béarnaise : `benefits_from` qui ressemble à un conseil, exécution = piège minute

- **Modèle naïf** : viande `benefits_from: [sauce]` → béarnaise
  (`recipes/sauce-bearnaise.gram`, émulsion beurre-jaunes à 80 °C).
- **Réalité d'exécution** : la béarnaise a une **élasticité thermique quasi nulle**
  (#91) : elle ne se maintient pas, ne se réchauffe pas, tranche si on la laisse.
  Elle concentre toute la **charge active au moment exact du service**, pendant
  que la viande repose et que l'accompagnement attend. C'est la combinaison la
  plus dangereuse pour un cuisinier seul, alors que le modèle la présente comme
  une simple « option ».
- **Leçon** : `benefits_from` ne doit **jamais** laisser croire qu'un ajout est
  gratuit. Mais la solution n'est pas d'ajouter `difficulté: haute` dans `needs`
  : c'est à **#154** de marquer « sauce minute = +1 tâche active à T-service,
  déconseillée si le plat principal exige déjà un dressage minute ». Le contrat
  #151 reste binaire et simple ; la pondération vit en #154.

### CE-3. Tantanmen ramen : `complete` qui interdit tout ajout… sauf que l'exécution est déjà saturée

- **Modèle naïf** : `tantanmen-ramen-epice.gram` (TM + Varoma + casserole en
  parallèle) = `complete`, `needs: []`. Composition terminée.
- **Réalité d'exécution** : la recette **sature déjà** l'attention (3 ressources
  simultanées) et le plan de travail. Un utilisateur qui ajoute quand même des
  gyozas « parce que l'UI le propose » fabrique un repas inexécutable.
- **Leçon** : pour les `complete` à forte charge interne, la composition doit
  **refuser ou freiner les ajouts** (« ce repas se suffit, ajouter un composant
  dégrade le service »). C'est une règle #154 / UX, pas un champ #151. Mais #151
  doit garantir que `needs: []` + `complete` signifie bien « ne rien suggérer par
  défaut » — sinon la cascade #152/#160 proposera du riz avec un ramen.

### CE-4. Gratin de chou-fleur : `component` ou `main` selon la portion, et four monopolisé

- **Modèle naïf** : `gratin-chou-fleur.gram` (6 portions, familial) = `component`,
  `role: vegetable`.
- **Réalité d'exécution** : servi en **plat unique du soir** pour 3 (double
  portion), il devient un `main` de fait — le statut **bascule avec la portion
  et le contexte**, comme #169 le soupçonne. Côté four : 30–40 min de cavité
  unique à ~180–200 °C. Toute autre suggestion « allant au four » à température
  incompatible (#93) rend le repas impossible sans second four.
- **Leçon x2** : (a) un `required: true` statique ne survit pas au changement de
  portion — `needs` doit être **qualifié par le contexte**, pas booléen absolu ;
  (b) la compatibilité four ne se déduit pas des rôles — elle appartient à
  #154/#51 via les ressources déclarées, pas à `needs`.

### CE-5. Salade César : `complete` le midi, `starter` le soir — le contexte décide, pas la recette

- **Modèle naïf** : `salade-cesar.gram` (poulet, œufs mollets 6 min, croûtons) =
  `complete`, `role: salad`.
- **Réalité d'exécution** : le midi pour 1→2, c'est un repas ; le soir en entrée
  pour 4 avant un plat, c'est un `starter`. Exécution triviale (pas de conflit
  thermique, poêle + casserole brièvement), mais **fraîcheur minute** : romaine +
  sauce ne tiennent pas dressées — contrainte inverse des plats mijotés.
- **Leçon** : `role: salad` ne dit pas si c'est une entrée ou un repas ; la
  **portion et le moment** décident. Le contrat doit autoriser l'ambiguïté
  explicite (voir §5, règle R3) plutôt que de forcer un rôle unique faux.

### CE-6. Curry : « avec ou sans riz intégré » — deux variantes, deux `needs`

- **Corpus** : `curry-poulet-express.gram`, `curry-poulet-fruits-riz.gram`
  (riz **intégré**), `curry-de-boeuf.gram`, `curry-poulet-tomates-amandes.gram`.
- **Piège** : la variante avec riz intégré est `complete` ; la même base sans riz
  est `partial needs: [starch]`. Le statut n'est **pas une propriété du « curry »
  en général**, il dépend de la variante rédigée.
- **Leçon** : `meal.*` est une métadonnée **par fichier `.gram`**, jamais par
  famille de plats. Et `needs` ne doit pas tenter de modéliser « riz intégré en
  option » : si deux variantes coexistent, ce sont deux recettes avec deux
  métadonnées. Pas de conditionnelle dans le contrat v1.

### CE-7. Veloutés / soupes : le cas qui tue `required: true`

- **Corpus** : `soupe-butternut-curry-amandes.gram`,
  `veloute-potiron-cannelle.gram`, `soupe-poireaux-pommes-de-terre-fenouil.gram`.
- **Réalité** : la même soupe est entrée (petite portion, `needs` du repas porté
  par la suite), plat léger (grande portion + pain), ou repas (avec œuf/lardons/
  tartine). Un `needs: [{role: bread, required: true}]` est faux deux fois sur
  trois. Pire : le pain ne se « cuisine » quasiment pas (charge ~0, pas de
  ressource) — en faire un `needs` bloquant, c'est confondre **structure
  culturelle** (« en France on sert du pain ») et **nécessité culinaire**.
- **Leçon** : c'est ici que `required: true` fait le plus de dégâts (voir §4).
  Le besoin pain est **culturel et optionnel**, jamais requis au sens exécution.

### CE-8. One-pot poulet-riz-légumes : `complete` par construction — tout ajout est une faute

- **Corpus** : `one-pot-poulet-riz-legumes.gram` (« poulet doré et riz moelleux
  cuits dans une seule poêle… pour un dîner familial complet »).
- **Réalité** : protéine + féculent + légumes déjà dans la poêle. Suggérer un
  féculent supplémentaire, c'est du **sur-service** : gaspillage, surcharge,
  confusion.
- **Leçon** : le contrat doit permettre d'exprimer « complet, ne rien ajouter »
  sans ambiguïté (`needs: []` explicite ou absent + `complete`). Les consommateurs
  (#160, MCP) doivent traiter `complete` comme **signal d'arrêt**, pas comme
  invitation à enrichir.

### CE-9. Pizza margherita : `complete` mais four minute — le composant « entrée au four » est un conflit garanti

- **Corpus** : 20+ pizzas (`pizza-margherita.gram`, …), cuisson vive, service
  immédiat, four à haute température monopolisé en continu pour une tablée.
- **Réalité** : la pizza est `complete`, mais son exécution **interdit** tout
  composant four simultané. Une entrée froide (salade) passe ; une entrée chaude
  au four casse le service.
- **Leçon** : « complete » ne veut pas dire « exécution légère ». La charge four
  n'apparaît nulle part dans `needs` — et c'est très bien : elle relève des
  ressources #93 exploitées par #154/#51.

### CE-10. Riz basmati : le composant idéal… à condition de choisir la bonne méthode

- **Corpus** : `riz-basmati-pilaf.gram`, `riz-basmati-au-four.gram`,
  `riz-blanc-long-casserole.gram`, `riz-creole-grande-eau.gram`,
  `riz-thermomix-mode-rice-cooker.gram`, `riz-rice-cooker.gram`, etc.
- **Réalité** : le riz est le **meilleur compagnon d'exécution** (tolère le
  maintien au chaud couvert 10–15 min, charge active faible après démarrage).
  Mais chaque méthode consomme une **ressource différente** (feu, four, bol
  robot, rice-cooker). Le « même » composant a donc 5 profils d'exécution.
- **Leçon** : #152 ne doit pas créer « la » recette riz canonique unique — ou
  alors avec variantes de méthode explicites. Et #151 ne doit pas désigner une
  méthode : `needs: [starch]` pointe un **rôle**, la sélection du candidat et de
  sa méthode relève de la composition + #154 (quelle ressource est libre ?).

---

## 4. Le problème central : `needs` / `benefits_from` cachent trois choses

### 4.1. Des contraintes de planning déguisées en besoins culinaires

Exemples de glissement observés dans les discussions #151/#154 :

| Formulation « besoin » | Contrainte d'exécution réellement cachée | Où elle doit vivre |
|---|---|---|
| `needs: [starch]` sur un plat déjà long et actif | « il faut un féculent **passif** car le cuisinier est saturé » | #154 (préférer candidat passif), pas #151 |
| `benefits_from: [sauce]` | « sauce minute = pic de charge à T-service » | #154 (règle sauces minute), pas #151 |
| `needs: [vegetable]` | « légume vapeur = Varoma occupé, conflit avec plat au Varoma » | #154/#51 (ressources), pas #151 |
| `needs: [bread]` | « pain = charge 0, toujours proposable » | #154 (candidat par défaut à coût nul), pas un `needs` bloquant |

**Règle** : si la satisfaction d'un besoin dépend de *qui cuisine, avec quel
équipement, dans quel ordre*, ce n'est plus un besoin structurel — c'est de la
faisabilité (#154) ou de l'ordonnancement (#51).

### 4.2. Des hypothèses culturelles présentées comme des nécessités

- **« Porc au caramel REQUIERT du riz »** : c'est la tradition de service
  française d'un plat asiatique + l'intention de l'auteur (« accompagné par
  exemple d'un bol de riz blanc » dans `porc-au-caramel.gram`). Au Vietnam, le
  même registre se sert parfois avec nouilles, pain bánh mì, ou en partage
  multi-plats sans féculent dédié. `required: true` **fige une norme culturelle
  en contrat machine**.
- **« Steak requiert une garniture »** : steak-frites (France), steak-seul en
  dégustation bouchère, steak + salade légère l'été. Le « requis » dépend du
  repas, pas du steak.
- **« Soupe requiert du pain »** (CE-7) : coutume française, pas nécessité.
- **« Curry requiert riz OU pain »** : la disjonction elle-même est culturelle
  (riz au Japon/Inde du Sud, pain en Inde du Nord) — un `needs` mono-rôle ment,
  un `needs` multi-rôles avec OU introduit de la logique propositionnelle dans
  un contrat v1. À reporter.

**Règle** : tout besoin d'origine traditionnelle doit être **étiqueté comme tel**
(note auteur) et classé en `benefits_from`, jamais en `needs` bloquant — sauf
déséquilibre structurel évident (viande seule pour 4 sans rien = `needs`
légitime, justifié par la satiété, pas par la tradition).

### 4.3. Une fausse précision : `required: true` dans `needs`

La question de #169 est directe, ma réponse l'est aussi :

```yaml
# Forme proposée en #151 — À REJETER en v1
needs:
  - role: starch
    required: true
```

`required: true` n'apporte **aucune information** : l'objet est déjà dans `needs`.
Pire, il suggère qu'un jour on écrira `required: false` dans `needs`, c'est-à-dire
exactement ce que `benefits_from` exprime déjà. C'est une complexité sans usage
actuel (YAGNI pur) qui ouvre la porte à trois états de vérité pour deux tiroirs.

```yaml
# Forme recommandée — v1
meal:
  completeness: partial
  role: main
  needs: [starch]
  benefits_from: [vegetable]
```

**Si un besoin futur exige une structure objet** (quantité, condition de portion,
alternative OU), on l'introduira **quand le cas réel arrivera**, pas avant.
Aujourd'hui, aucun usage actuel (composition simple, liste de courses, suggestions)
ne nécessite l'objet.

---

## 5. Règles minimales recommandées (contrat v1)

### R1. `needs` / `benefits_from` = listes simples de rôles, rien d'autre

```yaml
meal:
  completeness: partial | complete | component
  role: main | starch | vegetable | sauce
  needs: [starch]            # requis structurels — absence = repas bancal
  benefits_from: [vegetable] # apports conseillés — absence = repas valide mais perfectible
```

- Pas d'objet, pas de `required:`, pas de durée, pas d'équipement, pas de
  difficulté, pas de quantité.
- `needs` vide ou absent + `complete` = signal d'arrêt pour les consommateurs.

### R2. Taxonomie des rôles réduite à 4 en v1 : `main | starch | vegetable | sauce`

- **Garder** : les quatre rôles qui portent un `needs` réel et des exemples
  corpus massifs (riz/pâtes/semoule ; légumes vapeur/rôtis ; béarnaise/poivre/
  béchamel du gratin).
- **Reporter** : `salad` (fusionné dans `vegetable` en v1 — la César et la
  grecque sont des légumes composés ; la distinction entrée/repas vient du
  contexte, CE-5), `bread` (pas un rôle cuisiné : charge ~0, jamais un `needs`
  bloquant, mention en note libre), `condiment` (oignons caramélisés, pesto,
  vinaigrette : `sauce` ou note libre en v1), `starter`/`dessert` (ce sont des
  **positions dans le menu**, pas des rôles de composition — hors scope v1).
- Chaque valeur conservée doit avoir ≥3 exemples corpus réels (condition
  d'acceptation de la taxonomie).

### R3. `needs` est contextuel : portion + usage, pas booléen absolu

Tout `partial` dont le statut bascule avec la portion ou le moment (CE-4, CE-5,
CE-7) **doit** documenter la condition en note auteur structurée :

```yaml
meal:
  completeness: partial
  role: main
  needs: [starch]
  note: "En entrée (petites portions), servi seul. En plat (portion ×2), prévoir un féculent."
```

- v1 : champ `note` libre (chaîne). Pas de DSL de conditions (`if portions > …`,
  `unless starter`) — prématuré, aucun consommateur ne l'exploiterait.
- L'auteur déclare son **intention éditoriale** (« conçu pour… »), pas une
  propriété intrinsèque de la nourriture (#169 §1 : c'est bien l'intention qui
  est modélisée — l'assumer explicitement).

### R4. `meal.*` est par fichier `.gram`, jamais par famille de plats

Variantes avec/sans riz intégré (CE-6), gratin plat vs accompagnement (CE-4),
soupe entrée vs repas (CE-7) : chaque fichier porte sa propre métadonnée.
Interdiction de « deviner » le statut depuis le titre ou les tags.

### R5. Interdiction d'encoder l'exécution dans `needs`

Sont **refusés en validation** dans `meal.needs` / `meal.benefits_from` :
durées, équipements (`four`, `thermomix`, `Varoma`), températures, niveaux
(`actif`, `minute`, `facile`), effectifs, créneaux. Ces données vivent déjà
(frontmatter `appliances`, `required_equipment`, minuteurs `~{…}`, `^{…}`) ou
vivront en #91/#93/#154. Dupliquer, c'est diverger.

### R6. `benefits_from` n'est jamais une promesse d'exécution

Règle de lecture imposée aux consommateurs : un `benefits_from: [sauce]` peut
désigner une sauce minute inexécutable dans le contexte courant. Seule #154
tranche. L'UX ne doit jamais afficher « il vous manque X » comme une injonction
sans filtre faisabilité (voir §7).

---

## 6. Ce qui doit rester HORS contrat (v1) — volontairement

| Élément | Pourquoi pas maintenant | Où plus tard |
|---|---|---|
| Objet structuré `needs: [{role, required, …}]` | Aucun usage actuel ; YAGNI (§4.3) | Si un cas réel l'exige, avec preuve |
| Conditions machine (`si portions > N`, `OU` logique curry riz/pain) | Aucun consommateur ; logique propositionnelle prématurée | v2, après retour d'usage #160 |
| Score / catégorie « complexité ajoutée » du composant | C'est #154, pas #151 | #154 (proposition faisabilité) |
| `holding_tolerance`, `effort`, ressources par étape | C'est #91/#93, inféré ou déclaré à l'étape | #91/#93 → consommé par #154/#51 |
| Compatibilité fours / températures, *cleaning delay* | Logistique #93, calculée par le solveur | #154 (garde-fou) puis #51 |
| Équilibre nutritionnel, fibres, macros | Indépendant par décision #149 | Epic nutrition / Meal Planning |
| Score d'accord sensoriel #98 | Classement, pas structure | #98 en aval de la composition |
| Catalogue des composants canoniques, anti-duplication | C'est #152 | #152 |
| `salad / bread / condiment / starter / dessert` comme rôles v1 | Mélange fonction/type/position ; exemples insuffisants ou contextuels | Réintroduire sur preuve corpus |
| Suggestions automatiques d'accompagnements (moteur) | Discovery, pas de moteur en #151 | #160 / futur Shopping Planner |
| Multi-scheduler, profils cuisine multi-foyers | Aucun usage actuel | #51 v3 |

---

## 7. Frontière #154 / #51 : qui fait quoi (proposition exécution)

Pour éviter que #151 ne soit consommée directement par le solveur sans garde-fou :

```text
Recette (.gram + meal.*) ── #149/#151 ──► QUOI manque (rôles)
        │
        ▼
Règles de faisabilité ── #154 ──► EST-CE RAISONNABLE ?
  (charge active cumulée, nbre de « minute » simultanés,
   équipements exclusifs, maintien au chaud, repos, dressage)
        │  refuse / avertit / préfère le candidat passif
        ▼
Solveur ── #51 ──► QUAND / COMMENT (planning déterministe)
        │
        ▼
Explication / UX (timeline, minuteurs, « +10 min en parallèle »)
```

**Garde-fous #154 minimaux que mon analyse impose** (à spécifier dans #154, pas ici) :

1. **Pic de charge à T-service** : pas plus d'**une** tâche `active_human`
   minute simultanée pour un cuisinier seul (béarnaise + dressage + découpe =
   refus ou séquençage forcé).
2. **Équipements exclusifs** : tout composant exigeant une ressource déjà
   monopolisée (bol Thermomix du porc au caramel, four du gratin) déclenche
   séquençage + *cleaning delay* ou substitution de méthode (riz casserole
   plutôt que riz Thermomix).
3. **Maintien au chaud** : préférer par défaut les composants à forte élasticité
   (riz couvert, mijotés, gratins) quand plusieurs candidats sont culinairement
   équivalents ; signaler les composants à élasticité nulle (béarnaise, œufs
   mollets de la César dressée, pizza).
4. **Règle de substitution** : « à accord culinaire proche, choisir le candidat
   le moins chargé » (riz pilaf passif > poêlée minute quand le plat principal
   est déjà actif).
5. **`complete` saturé** (ramen, one-pot) : ne rien suggérer par défaut ;
   tout ajout exige validation explicite utilisateur.

**#51 ne consomme jamais `needs` brut** : il consomme un *repas composé validé*
(choix de composants + méthodes) passé au filtre #154.

---

## 8. Décisions explicitement demandées au PO (@PierreCsn)

| # | Décision | Recommandation expert | Impact si refusée |
|---|---|---|---|
| D1 | Adopter la **forme liste simple** (`needs: [starch]`) et rejeter `required: true` en v1 | Oui — §4.3 | Conserver l'objet = complexité sans usage, divergence future garantie |
| D2 | Réduire les rôles v1 à **`main \| starch \| vegetable \| sauce`**, reporter `salad/bread/condiment/starter/dessert` | Oui — §R2 | Taxonomie mixte fonction/type/position, incompréhensible en authoring et en UX |
| D3 | `needs` **consultatif, jamais bloquant** : l'utilisateur peut cuisiner un `partial` seul (repas assumé incomplet) | Oui — l'outil conseille, ne contraint pas | « Requis » bloquant = fausse autorité culturelle (§4.2), frictions UX |
| D4 | **Traditions culturelles étiquetées** : un besoin d'origine coutumière va en `benefits_from` + note, pas en `needs` | Oui — §4.2 | Figer des normes FR en contrat machine, inadapté aux usages asiatiques/italiens/etc. du corpus |
| D5 | `meal.*` **par fichier**, avec `note` libre de contexte (portion/usage) ; pas de DSL conditionnel en v1 | Oui — §R3/R4 | Sans note, les cas soupe/salade/gratin/curry mentiront une fois sur deux |
| D6 | **Frontière stricte** : #151 déclare QUOI, #154 juge RAISONNABLE, #51 calcule QUAND ; #51 ne lit jamais `needs` brut | Oui — §7 | Scheduler nourri de besoins bruts = plannings inexécutables, échec v3 |
| D7 | `complete` + `needs: []` = **signal d'arrêt** pour #160/MCP (ne rien suggérer par défaut, notamment ramen/one-pot/pizza) | Oui — CE-3/CE-8 | Sur-service systématique, perte de confiance |
| D8 | Reporter le **moteur de suggestion** et le **score de complexité** vers #154/#160, hors contrat #151 | Oui — §6 | Scope creep : figer en contrat ce qui doit rester heuristique d'exécution |

Sans validation PO sur D1–D6 au minimum, le contrat #151 ne doit pas être
considéré comme stable pour implémentation (gouvernance #169 : *décision
nécessitant validation PO*).

---

## 9. Vérifications effectuées (traçabilité)

- Corpus lu : `porc-au-caramel`, `tantanmen-ramen-epice`, `gratin-chou-fleur`,
  `salade-cesar`, `one-pot-poulet-riz-legumes`, `sauce-bearnaise` (frontmatter +
  ressources), inventaire des variantes riz/curry/soupe/pizza/gratin/salade.
- Issues relues : #149, #150, #151, #152, #154, #51, #91, #93 (rôles, garde-fous,
  séparation déterministe/LLM).
- **Aucun code modifié, aucune recette modifiée, aucun scheduler implémenté.**
  Livrable unique : ce document.
- Validations dépôt : `yaml` + audit images (voir rapport de PR).

---

## 10. Statut de ce document (gouvernance #169)

- **Hypothèse** : les 10 contre-exemples et les 3 glissements (§4) — contestables,
  à challenger par Recipe Expert / Design Expert.
- **Recommandation expert** : règles R1–R6, tableau hors-contrat, frontière §7.
- **Décision Lead** : à synthétiser par le Lead (pas de préemption ici).
- **Décisions PO** : D1–D8 ci-dessus, autorité finale @PierreCsn.
- **Contrat stable** : uniquement après validation PO — en attendant, ce document
  est une contre-review, pas une spécification.
