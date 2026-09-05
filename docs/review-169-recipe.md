# Contre-review Recipe Expert — Meal Composition Layer (#169)

> Statut de ce document : **recommandation expert** (ni décision Lead, ni arbitrage PO, ni contrat implémentable).
> Références challengées : #149 (complétude + rôle), #151 (`needs` / `benefits_from`).
> Corpus audité : 162 recettes `.gram` réelles (aucune ne porte encore de clé `meal:` — vérifié).
> Principe : aucune recette modifiée, aucun code produit par cette review.

## 1. Gouvernance : qui décide quoi

| Niveau | Contenu dans ce document | Autorité |
|---|---|---|
| Hypothèse | Modèle `complete / partial / component` + `role` + `needs` / `benefits_from` issu de #149/#151 | Lead (discovery) |
| Recommandation expert | Tout le §2 au §7 ci-dessous | Recipe Expert (ce document) |
| Décision Lead | À prendre après cette review : figer ou amender le contrat minimal §6 | Lead |
| Arbitrage PO | Points listés §5 (notamment `salad`, `bread`, `unknown` explicite, sémantique `needs` multiple) | @PierreCsn, requis avant implémentation |
| Contrat implémentable | Le seul §6 **après** arbitrage PO | Core / Dev |

Règle rappelée par #169 : une recommandation détaillée d'agent n'est pas une décision produit.
Ce document ne doit être consommé par #150 / #152 / #160 / #156 qu'**après** arbitrage PO (voir §8).

## 2. Ce qui est confirmé (avec preuves corpus)

### 2.1 La trichotomie `complete / partial / component` couvre les usages réels

Testée contre les 10 familles imposées par #169 :

| Cas imposé | Recette testée | Classement expert | Preuve textuelle |
|---|---|---|---|
| Porc caramel + riz + légume | `porc-au-caramel` | `partial / main` | Dernière ligne : « Servir […] accompagné par exemple d'un bol de riz blanc » — riz ni quantifié ni cuit dans la recette |
| Steak + accompagnement | `faux-filet-boeuf-sous-vide` | `partial / main` | Aucun féculent ni légume dans la recette ; `flavors.pairing` cite lui-même « pommes de terre grenailles, haricots verts » comme horizon d'accompagnement |
| Curry **avec** riz intégré | `curry-poulet-fruits-riz` | `complete` | Riz quantifié (`riz long blanc 250 g`) + cuit dans le déroulé (panier cuisson) + poulet + fruits : protéine + féculent + garniture dans un seul graphe d'exécution |
| Curry **sans** riz intégré | `saute-de-porc-au-curry` | `partial / main` | « Servir […] accompagné de riz basmati ou thaï » sans quantité ni cuisson : le riz est un horizon, pas un composant |
| Cas mixte discriminant | `curry-poulet-express` | `complete` (limite, voir §4.1) | Riz quantifié (`riz basmati 240 g`) et instruction de cuisson en parallèle, même si cuisson séparée en casserole. **Règle proposée** : féculent quantifié + instruction = `complete` ; féculent mentionné sans quantité = `partial` |
| Soupe entrée | `veloute-asperge-cerfeuil` (6 portions, sans légumineuse ni féculent) | `partial` ou `component` selon contexte (voir §4.2) | Aucun apport de satiété structurel ; `crème 200 g` seule ne fait pas un repas |
| Soupe repas | `veloute-butternut-lentilles-corail-curry` (lentilles corail 100 g + pommes de terre 100 g + crème) | `complete` (repas léger) | Féculent + légumineuse déjà dedans : le critère « protéine + féculent + garniture » est à lire de façon végétarienne souple, sinon on déclasse à tort tout le corpus soupe végétale |
| Salade-repas | `salade-cesar` (poulet 300 g + œufs + croûtons 100 g + parmesan) | `complete` | Protéine + féculent (croûtons) + crudités : autonome à 4 portions |
| Salade d'accompagnement | `salade-grecque` (aucune protéine rassasiante, aucun féculent) | `component / vegetable` | « Servir […] avec du pain de campagne » : elle appelle elle-même un complément |
| Gratin accompagnement | `gratin-chou-fleur` (6 portions, chou-fleur + béchamel) | `component` | Ni protéine ni féculent consistant ; typique side de rôti |
| Gratin plat | `gratin-poulet-brocolis` (poulet 600 g + brocolis + sauce + emmental, 6 portions) | `complete` | Protéine + légume + fromage ; le féculent manque mais le plat se suffit en repas du soir — cf. §4.2 sur la tolérance du soir |
| Pizza | `pizza-margherita` (portions: 1, pâte 250 g + tomate + mozzarella) | `complete` | Féculent (pâte) + garniture ; `benefits_from: [vegetable]` serait du zèle de diététicien, pas un besoin structurel |
| Ramen | `tantanmen-ramen-epice` (porc + nouilles 250 g + épinards + maïs + bouillon) | `complete` | L'archétype du `complete` : tout est déjà dans le bol |
| One-pot | `one-pot-poulet-riz-legumes`, `one-pot-orzo-crevettes-citron`, `one-pot-curry-lentilles-coco`, `jambalaya-poulet` | `complete` (tous) | Protéine + féculent + légume dans un seul récipient ; c'est la famille qui justifie à elle seule l'existence de `complete` |
| Repas multi-composants | `lu-rou-fan-porc-taiwanais` (porc + œufs, service « sur un bol de riz blanc » non quantifié) | `partial / main` | La dernière étape impose le riz sans le fournir : `needs: [starch]` canonique |
| Composants | `riz-basmati-au-four` (starch), `sauce-bearnaise` (sauce), `oignons-caramelises-balsamique` (condiment — ses propres tags disent `condiment`), `pesto-ail-des-ours` (sauce) | `component` + rôle idoine | Le corpus contient déjà les trois natures ; `riz-blanc-long-casserole` taggé `accompagnement` confirme l'usage auteur existant |

**Recommandation expert : conserver la trichotomie.** Elle classe sans forcer les 10 familles, y compris les cas limites, à condition d'accepter §4 (sensibilité portion/contexte documentée, pas modélisée).

### 2.2 `unknown` comme absence de métadonnée suffit — ne pas créer de valeur `unknown`

État de fait : 162/162 recettes n'ont pas de clé `meal:`. L'absence est donc déjà l'état « inconnu ».
Ajouter une valeur littérale `unknown` que les auteurs devraient écrire explicitement n'apporte rien et crée deux façons de dire « je ne sais pas » (absence vs valeur), donc des incohérences de validation et de requêtage pour Core/MCP.

**Recommandation expert : pas de valeur `unknown` dans le contrat.** Convention : clé absente = non qualifié. Les consommateurs (#160, #156) traitent l'absence comme « inconnu, ne pas bloquer l'UX ».

### 2.3 `needs` / `benefits_from` : la distinction requis/conseillé est culinairement réelle

`porc-au-caramel` → riz requis, légume conseillé. `faux-filet` → garniture requise (un steak seul n'est pas un repas dans la culture CookiGram), sauce conseillée. `lu-rou-fan` → riz requis. La paire requis/conseillé n'est pas une invention : elle correspond à « le repas est structurellement incomplet sans X » vs « X l'améliore ».

## 3. Ce qui doit être simplifié

### 3.1 `required: true` dans `needs` est redondant — le rejeter

La forme objet proposée en #151 :

```yaml
needs:
  - role: starch
    required: true
```

n'apporte aucune information : tout élément de `needs` est requis **par définition**, sinon il serait dans `benefits_from`. Le booléen ne peut jamais valoir `false` sans contradiction sémantique, et aucune recette du corpus ne justifie une nuance intermédiaire (pas de « demi-requis » observé).

**Recommandation expert : forme plate, listes de rôles simples.**

```yaml
meal:
  completeness: partial
  role: main
  needs: [starch]
  benefits_from: [vegetable]
```

Ne réintroduire la forme objet que si un besoin **actuel et nommé** l'exige (aujourd'hui : aucun — les contraintes temps/équipement relèvent du scheduler #51, pas de l'auteur de recette). Toute extension future devra repasser par Recipe Expert + arbitrage PO.

### 3.2 Taxonomie `role` : 7 valeurs → 4 valeurs

La liste #149 (`main, starch, vegetable, sauce, salad, bread, condiment`, plus `starter, dessert` évoqués) mélange **fonction dans le repas** et **type d'aliment**, et chaque valeur en trop est un coût de qualification du corpus + de validation Core + de surface MCP.

| Valeur proposée | Verdict expert | Justification corpus |
|---|---|---|
| `main` | **Garder** | Cœur du repas : `porc-au-caramel`, `faux-filet`, `saute-de-porc-au-curry`, `lu-rou-fan` |
| `starch` | **Garder** | 10 recettes `riz-*` + `pommes-anna`, `pommes-de-terre-grenailles-romarin-sous-vide` : famille nombreuse et homogène |
| `vegetable` | **Garder** | Légumes vapeur/rôtis/poêlées ; couvre aussi les salades d'accompagnement (voir `salad`) |
| `sauce` | **Garder** | `sauce-bearnaise`, `pesto-ail-des-ours`, `sauce-au-poivre-vert`, `sauce-tahini-yaourt-citron` : famille réelle |
| `salad` | **Retirer** | Voir §3.3 : format, pas fonction |
| `bread` | **Retirer** | Voir §3.4 : simple forme de `starch` |
| `condiment` | **Reporter (hors contrat minimal)** | Un seul vrai cas (`oignons-caramelises-balsamique`, qui se déclare lui-même `condiment` dans ses tags). Distinction sauce/condiment réelle mais marginale : trancher plus tard, autoriser `sauce` par défaut d'ici là |
| `starter` / `dessert` | **Retirer** | Position dans le menu ≠ rôle compositionnel. Si un jour nécessaire, c'est un axe `course` séparé, hors contrat (voir §7) |

### 3.3 `salad` n'est pas un rôle — c'est un format (contre-exemples)

Le corpus prouve que « salade » traverse les trois complétudes :

- `salade-cesar` → `complete` (repas) ;
- `salade-grecque` → `component / vegetable` (accompagnement) ;
- `salade-de-lentilles` (lardons + vinaigrette, tiède) → selon portion : entrée, side ou plat léger — classer `salad` ne dit rien de sa fonction ;
- `salade-de-pois-chiches` (+ feta) → repas végétarien léger plausible, donc `complete` limite.

Un rôle `salad` obligerait en plus à trancher absurdement : une poêlée de légumes servie froide devient-elle `salad` ? Une salade César chaude au poulet est-elle un `vegetable` ? Le tag `salade` existe déjà dans le frontmatter pour la recherche ; en faire aussi un rôle crée deux classifications parallèles qui divergeront.

**Recommandation expert : pas de rôle `salad`.** Les salades d'accompagnement sont `component / vegetable`. Les salades-repas sont `complete` (sans rôle obligatoire, ou `role: main` — arbitrage PO §5.3).

### 3.4 `bread` n'est pas un rôle — c'est un `starch` (contre-exemple)

Le corpus ne contient aucune recette de pain autonome à qualifier (`pains-pita-maison`, `focaccia-thermomix`, `brioche-butchy` : le pain y est ingrédient ou boulangerie, pas composant de repas). Quand du pain accompagne (`salade-grecque` + « pain de campagne », `bo-kho` + « baguette »), il joue exactement la fonction féculent. Un rôle distinct n'a aucun exemple réel qui l'exige.

**Recommandation expert : pas de rôle `bread`.** Le pain-composant est `component / starch`.

## 4. Ce qui reste incertain / cas limites documentés

### 4.1 `curry-poulet-express` : la frontière `complete / partial` tient à une règle, pas à une intuition

Riz quantifié dans les ingrédients + cuisson instruite (même séparée) → `complete`. Sans cette règle, deux auteurs classeront différemment la même recette. La règle « féculent quantifié + instruction = complete » (§2.1) lève l'ambiguïté et se valide mécaniquement (présence d'un ingrédient féculent avec quantité). **À confirmer par le Lead** comme règle de rédaction.

### 4.2 Portions et contextes changent le statut — documenter, ne pas modéliser

Contre-exemples réels où le statut bascule :

- **Soupe** : `veloute-asperge-cerfeuil` en entrée (portion recette : 6) vs en repas (portion doublée + pain + fromage). Même texte, deux statuts.
- **Gratin** : `gratin-chou-fleur` side d'un rôti (6 portions familiales) vs plat unique d'un dîner léger (portion doublée). `gratin-poulet-brocolis` : `complete` le soir, `partial` (sans féculent) à midi pour un gros appétit.
- **Salade** : `salade-cesar` en plat (recette nominale) vs en entrée (demi-portion).
- **Pizza** : `pizza-margherita` (`portions: 1`) : repas pour un, entrée à partager pour deux — le frontmatter ne peut pas le dire.

**Recommandation expert : la complétude modélise l'intention éditoriale nominale de l'auteur** (« telle que rédigée, pour ses portions nominales, cette recette vise tel statut »), **pas une propriété intrinsèque de la recette.** L'écrire noir sur blanc dans le contrat évite que Core/MCP ne traitent `complete` comme une garantie. Aucune machinerie « complétude conditionnelle aux portions » : YAGNI pur (aucun consommateur actuel ne la réclame — voir §8).

### 4.3 Steak : `needs` à un ou deux éléments ?

`faux-filet-boeuf-sous-vide` appelle pommes de terre **et** haricots verts (son propre `flavors.pairing`). Faut-il `needs: [starch, vegetable]` ou `needs: [starch]` + `benefits_from: [vegetable]` ? Le garde-fou #151 (« ne pas imposer plusieurs compléments ») pousse vers la seconde forme, mais elle euphémise : un steak + riz sans légume reste un repas bancal. **Point d'arbitrage PO** (§5.4) : l'expert recommande d'autoriser 1 à 2 entrées dans `needs` (le cas steak le justifie) tout en recommandant une seule en pratique courante.

### 4.4 Dhal et velouté enrichi : le triplet « protéine + féculent + garniture » ne s'applique pas tel quel au végétarien

`dhal-lentilles-corail-coco` (lentilles + coco + épinards, « servir avec un riz basmati chaud » non quantifié) : `partial` par la règle du riz, mais sur le fond presque complet — la lentille est à la fois protéine et féculent. `veloute-butternut-lentilles-corail-curry` : `complete` assumé alors qu'il n'y a pas de « protéine » au sens carné. **Recommandation expert : formuler le critère `complete` en termes de satiété/couverture (féculent ou légumineuse + garniture + matière grasse/protéine au sens large), pas en triplet carné.** Sinon tout le corpus végétarien est systématiquement déclassé.

## 5. Décisions nécessitant arbitrage PO (bloquantes avant contrat)

1. **Rôle `salad` supprimé** (§3.3) — si le PO veut une entrée « salade » dans l'UX catalogue, qu'elle vienne des tags existants, pas du modèle meal.
2. **Rôle `bread` supprimé** (§3.4).
3. **Rôle des salades-repas et one-pots `complete`** : `role` absent (recommandation expert : un `complete` n'a pas besoin de rôle — il *est* le repas) vs `role: main` obligatoire. L'expert recommande **rôle optionnel, absent par défaut sur `complete`**.
4. **`needs` multi-entrées autorisé** (cas steak §4.3) : oui (recommandation expert, max 2) ou un seul + le reste en `benefits_from`.
5. **Pas de valeur `unknown` explicite** (§2.2) : confirmer que l'absence de clé = inconnu dans tous les consommateurs.
6. **Forme plate imposée** pour `needs` / `benefits_from` (§3.1) : confirmer le rejet définitif de la forme objet pour ce cycle.
7. **Définition `complete` élargie au végétarien** (§4.4).

## 6. Contrat minimal recommandé (après arbitrage PO — seul § implémentable)

```yaml
meal:
  completeness: complete | partial | component   # requis si clé meal: présente
  role: main | starch | vegetable | sauce         # optionnel ; absent par défaut sur complete
  needs: [starch | vegetable | sauce]             # seulement si partial ; 1 entrée recommandée, 2 max
  benefits_from: [starch | vegetable | sauce]     # seulement si partial ; optionnel
```

Règles de validation :

- `meal` entièrement optionnel ; clé absente = non qualifié (jamais bloquant).
- `complete` : ni `needs` ni `benefits_from` autorisés (un repas autonome n'a pas de besoin structurel ; sinon c'est un `partial`).
- `component` : ni `needs` ni `benefits_from` ; `role` **requis** (un composant sans rôle est inexploitable par #150/#156).
- `partial` : `role: main` recommandé (défaut si absent) ; `needs` requis (1 entrée, 2 max) ; `benefits_from` optionnel.
- Les valeurs de `needs` / `benefits_from` réutilisent le vocabulaire `role` **moins `main`** (un plat ne « requiert » pas un autre plat ; documenter cette restriction).
- Règle de rédaction « riz quantifié + instruction = complete » (§4.1).
- Définition `complete` : « la recette, telle que rédigée et à ses portions nominales, vise à pouvoir être servie comme repas autonome sans accompagnement structurellement attendu ». Mention explicite : intention éditoriale nominale, pas garantie intrinsèque ni équilibre nutritionnel (cf. #149 : la nutrition reste une dimension indépendante).

Stratégie de migration (rétro-compatible) :

- Aucune migration obligatoire des 162 recettes.
- Qualification au fil de l'eau + en priorité les composants canoniques (1 riz, 1 purée/pomme de terre, 1 légume vapeur, 1 salade verte, 2 sauces) dès que #152 les désigne.
- Les consommateurs doivent fonctionner avec `meal` absent (cf. §8).

## 7. Volontairement hors contrat pour l'instant

- Forme objet de `needs` (`role:`, `required:`, futures contraintes temps/équipement) — YAGNI, pas d'usage actuel.
- Axe `course` (`starter` / `dessert` / position menu) — autre dimension, autre issue si besoin.
- Rôle `condiment` — 1 seul cas réel ; réévaluer quand #152 aura tranché le statut des micro-préparations.
- Rôle `bread`, rôle `salad` — rejetés (§3.3, §3.4), pas reportés.
- Complétude conditionnelle (portion/contexte/heure du repas) — documentée §4.2, non modélisée.
- Contraintes d'exécution dans `needs` (charge active, maintien au chaud, minute) — appartient à #51/#154, pas à l'auteur `.gram`.
- Score nutritionnel ou accord sensoriel dans `meal` — #98 et epic nutrition restent des dimensions indépendantes.
- Valeur `unknown` explicite — refusée (§2.2).

## 8. Conséquences pour les chantiers aval

- **#150 (Epic Meal Composition)** : ne peut figer son moteur sur la forme objet de `needs` ni sur 7 rôles. Séquence recommandée : arbitrage PO sur §5 → contrat §6 → alors seulement composition déterministe. En attendant, tout prototype consomme le contrat minimal **ou** l'absence de clé.
- **#152 (composants `.gram`)** : le contrat minimal rend le statut composant exprimable (`component` + `role` requis). Priorité expert : qualifier d'abord ~6 composants canoniques réutilisables plutôt que d'ouvrir le catalogue à des doublons (10 variantes de riz déjà présentes : `riz-*` × 10 — règle anti-duplication indispensable avant toute création).
- **#160 (Meal Planner, prototype parallèle)** : déjà cadré pour accepter `unknown`/absent et ne pas redéfinir la sémantique — cette review le confirme : le planner **ne doit pas** inventer sa propre complétude en attendant le contrat, et doit isoler un adapter. Aucun blocage : l'absence de `meal:` est un état normal, pas une erreur.
- **#156 (MCP)** : exposer `meal` tel quel (opaque, optionnel) ; ne pas en dériver de logique métier côté MCP (`check_meal`, `suggest_components` restent des calculs Core déterministes futurs, pas des inférences LLM). Aucun tool MCP ne doit exiger `meal:` présent. Le requêtage par rôle (`find_components(role="starch")`) reste valide avec 4 rôles seulement — simplifie le catalogue de tools.

## 9. Alternatives rejetées et pourquoi

| Alternative | Rejetée parce que |
|---|---|
| Valeur `unknown` explicite | Double l'absence existante ; bruit auteur + validation pour zéro usage |
| `needs` objet avec `required: true` | Information nulle (définition même de `needs`) ; complexité sans consommateur |
| Rôles `salad` / `bread` | Format/type, pas fonction ; zéro exemple exigeant ; divergence avec les tags existants |
| Axe `course` fusionné dans `role` | Mélange position-menu et fonction-composition ; besoin non démontré |
| `needs` enrichi exécution (temps/équipement) | Appartient au scheduler, pas à l'auteur ; surcharge de qualification sans moteur pour la consommer |
| Migration obligatoire du corpus | 162 recettes à qualifier sans contrat figé = churn + conflits multi-agents ; l'optionnel + qualification au fil de l'eau suffit |
| Modéliser portion/contexte | Aucun consommateur actuel ; documented-uncertainty > premature-machinery |

---

*Document produit sans modifier aucune recette ni aucun code, conformément au mandat #169.*
