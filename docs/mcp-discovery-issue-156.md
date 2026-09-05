# Discovery MCP — issue #156

**Statut :** rapport de cadrage, version `0.1.0`  
**Date :** 2026-09-05  
**Périmètre :** dépôt public `PierreCsn/cookigram` ; aucun changement dans `cookigram-core`, aucun serveur de production

## Résumé exécutif

MCP est à positionner comme une façade d’intégration fine au-dessus de services métier stables, et non comme un nouveau moteur culinaire. Le modèle reste :

```text
assistant / agent = intention, dialogue, orchestration
MCP              = transport et exposition de capacités
cookigram-core   = parsing, validation et calcul déterministes
.gram            = vérité culinaire publiée
```

La première surface doit rester volontairement petite : `search_recipes`, `get_recipe`, puis `validate_recipe`. Ce sont des outils READ/ANALYZE sans effet de bord, adaptés à un POC. La composition, les courses consolidées, la faisabilité et le planning ne doivent être exposés qu’après stabilisation des services #151/#152/#154/#51. WRITE est interdit par défaut.

Cette discovery ne fige ni le contrat métier de ces services, ni un schéma MCP final, ni un déploiement. Elle définit des garde-fous et des questions à trancher dans des sous-issues séparées.

## 1. État de l’architecture audité

Le dépôt public contient les recettes `recipes/*.gram`, les bases `.gram/ingredients.yaml` et `.gram/ingredient-provenance.yaml`, les médias et la documentation. Il ne contient ni parseur complet, ni PWA, ni tests applicatifs. Le core privé reçoit un `--content-dir`, parse et valide le corpus, puis construit la PWA. Cette frontière est documentée dans [`docs/PUBLIC-CONTRACT.md`](PUBLIC-CONTRACT.md), [`README.md`](../README.md) et dans `cookigram-core/docs/ARCHITECTURE.md`.

Le contrat public actuellement épinglé est `cookigram-contract v1.0.0` ; il porte sur la validation/compilation du corpus, pas sur une API runtime. Le core expose aujourd’hui des briques internes réutilisables, notamment :

| Capacité observée dans le core | Réutilisation MCP envisagée | Limite actuelle |
| --- | --- | --- |
| `parse_recipe` et `Recipe/Step` | projection canonique de `get_recipe` | DTO/API stable à définir |
| validation de contrat et `recipe_check` | `validate_recipe` | provenance du résultat et version à formaliser |
| `consolidate_menu` / audit matériel | futur `compose_meal` ou analyse | composition métier #151/#152 non stabilisée |
| `evaluate_recipe_shopping` | futur résultat de courses | périmètre mono-recette ; pas un contrat MCP |
| `smart_pairing` | classement secondaire de candidats | ne décide ni complétude ni besoin |

Ces fonctions ne sont pas des endpoints : MCP ne doit pas les recopier ni faire de parsing ad hoc du dépôt. Une couche d’application dans le core (ou un package partagé validé par ses propriétaires) devra fournir des ports stables et des DTO sérialisables. La façade MCP ne doit connaître ni les chemins arbitraires du filesystem, ni les détails des dataclasses internes.

## 2. Dépendances et ordre de livraison

### #149 — prérequis sémantique accepté

La décision PO associée à #149 est conservée : `meal` est facultatif, `completeness` vaut `complete | partial | component`, l’absence signifie `unknown` et jamais `complete`, et `role` est une dimension séparée. La taxonomie v1 publiée dans la discussion est `main`, `starch`, `vegetable`, `sauce`, `salad`, `bread`, `condiment`. `complete` ne signifie pas équilibré nutritionnellement.

MCP doit donc exposer la valeur éditoriale telle qu’elle est validée ; il ne doit pas l’inférer depuis les tags, le titre ou les ingrédients.

### #151 — encore en discovery

`needs` et `benefits_from` sont proposés comme relations éditoriales par rôle, mais leur contrat n’est pas encore finalisé ni intégré au contrat public. MCP ne doit pas inventer de besoins et ne doit pas faire croire que la composition est disponible parce que le nom d’un outil a été imaginé.

### #152 — contenu composable non canonisé

Les composants simples doivent d’abord devenir des recettes `.gram` réelles, avec quantités, durée, équipement et méthode déterministes. Une liste de noms d’accompagnements générée par le serveur serait une duplication fragile de la vérité éditoriale.

### #154 et #51 — faisabilité puis ordonnanceur

La faisabilité doit consommer la composition et les contraintes d’exécution avant le scheduler. Les règles #91/#93/#95 et le futur solveur #51 ne doivent pas être réinterprétés par un agent ou un serveur MCP. Un futur outil de planning devra retourner le résultat du service déterministe, y compris les conflits explicites.

## 3. Positionnement et catalogue initial

### Classes de permission

| Classe | Sens | v0 |
| --- | --- | --- |
| READ | lire des données canoniques publiques | autorisée |
| ANALYZE | demander un calcul déterministe sans mutation | autorisée sous limites |
| WRITE | créer/modifier/importer/persister | refusée par défaut |

Le premier catalogue est donc :

1. `search_recipes` — READ : recherche bornée dans l’index canonique, avec filtres explicites (texte, tags, rôle/complétude si publiés).
2. `get_recipe` — READ : lecture d’une recette par slug stable, avec ingrédients, étapes, équipements, métadonnées et provenance utile.
3. `validate_recipe` — ANALYZE : validation d’une recette ou d’un artefact explicitement autorisé par le service core ; retour structuré des erreurs, sans correction automatique.

Le nom, les champs exacts, les codes d’erreur et l’enveloppe MCP restent provisoires jusqu’à la définition des ports du core. Une réponse doit toutefois indiquer au minimum : `contract_version`, `source_revision` ou `content_sha`, `data_status` (`known`/`unknown`) et les erreurs structurées. Une donnée absente reste absente ; elle ne devient pas une supposition du LLM.

Hors v0 : `compose_meal`, `suggest_components`, `generate_shopping_list`, `check_execution_feasibility`, `schedule_meal`, `get_cooking_plan` et toute commande d’exécution. Ils seront réévalués après #151/#152/#154/#51 et après stabilisation de services core testables.

## 4. Resources et URI

Les resources sont une projection en lecture, pas un accès au disque. Les formes suivantes sont des candidates à tester, pas un contrat figé :

```text
cookigram://corpus
cookigram://recipes/{slug}
cookigram://ingredients/{ingredient-slug}
```

Règles proposées :

- URI opaques, normalisées et stables ; le slug est un identifiant logique, jamais un chemin de fichier fourni par le client ;
- aucune URI `file:`, traversal, glob ou lecture d’un chemin arbitraire ;
- `corpus` doit être paginé ou résumé, jamais injecté en totalité par défaut ;
- resources publiques et resources utilisateur doivent avoir des namespaces distincts ; `cookigram://meals/current` et `equipment/my-kitchen` sont reportés jusqu’à un vrai modèle de session et d’identité ;
- chaque resource porte une révision de contenu et un type média ; la canonicalisation `.gram` complète est préférable à une vue réécrite par le serveur, avec éventuellement une projection compacte documentée ;
- les données nutritionnelles, sources et licences sont exposées selon leur disponibilité et leurs droits, jamais complétées silencieusement.

Le serveur doit privilégier la recherche et `get_recipe` pour limiter les réponses volumineuses. Une resource ne doit pas devenir un second contrat public concurrent du contrat `.gram`.

## 5. Permissions, authentification et transports

### Local — stdio

Le mode stdio est le premier candidat pour Codex/OpenCode et les agents de développement. Il peut lire un checkout explicitement configuré ou un corpus emballé en lecture seule. Le processus doit recevoir une racine de contenu autorisée, refuser les chemins transmis dans les arguments et ne jamais hériter de secrets non nécessaires. Le stdio ne constitue pas une frontière de sécurité suffisante si l’agent local est déjà compromis.

### Distant — MCP via HTTP

Le distant est reporté après définition d’un service core déployable. Il requiert au minimum TLS, authentification de client, contrôle d’audience et expiration des jetons, séparation tenant/utilisateur, quotas et révocation. Les scopes doivent être capability-based (`recipes:read`, puis un scope ANALYZE séparé) ; aucun scope WRITE n’est créé pour le POC. Le serveur ne doit jamais transmettre les secrets du core ni ceux du fournisseur LLM.

### Politique d’autorisation

L’autorisation est vérifiée avant résolution de resource ou exécution d’outil, avec deny-by-default, allowlist d’outils, taille maximale de requête, nombre de résultats, timeout et budget de calcul. Les appels ANALYZE sont idempotents et sans effet de bord. Toute future mutation devra avoir une façade authoring séparée ou un profil explicite, confirmation humaine, audit trail et mécanisme de dry-run/rollback ; elle ne doit pas être ajoutée au serveur utilisateur par commodité.

## 6. Versionnement, sécurité et observabilité

Le protocole MCP, le contrat public `.gram`, le contrat des ports métier et la projection MCP sont quatre versions distinctes. Il faut exposer les versions et révisions sans les confondre : `protocol_version`, `api_version`, `contract_version`, `core_sha` et `content_sha` lorsque disponibles. Une évolution incompatible crée une nouvelle version de façade ou de capability ; elle ne modifie pas silencieusement le sens de `validate_recipe`.

Mesures de sécurité obligatoires avant un POC partageable : validation stricte des types et enums, limites de taille/temps, refus des URLs d’import et des chemins arbitraires, sanitation des erreurs, absence de secrets dans les resources, protection contre boucles d’agent et répétitions coûteuses, et isolation des données utilisateur. Les résultats doivent signaler les incertitudes et la provenance plutôt que les masquer.

Observabilité minimale : identifiant de requête, outil/capability, version, durée, statut, taille de réponse, code d’erreur et métriques de quota. Les logs ne contiennent ni tokens, ni recettes privées, ni contenu complet par défaut. Les appels WRITE futurs devront être auditables avec acteur, cible, confirmation et résultat ; READ/ANALYZE peuvent être échantillonnés avec politique de rétention documentée.

## 7. Assistant vocal : client futur, pas chantier de cette issue

L’assistant vocal est un bon client de référence : il exerce la lecture contextuelle, la faible latence et la synchronisation avec une session de cuisine. Il ne doit toutefois pas devenir la raison de créer prématurément des outils d’état ou des mutations.

Pour une étape future, les commandes déterministes fréquentes (`répète`, `suivant`, minuteur) devraient être traitées par une session d’exécution CookiGram, le LLM ne servant qu’à comprendre/formuler. `current_step`, timers, `complete_step`, retard et replanification nécessitent un état de session et un modèle d’autorisation qui n’existent pas dans ce dépôt public. Le POC vocal peut donc être évalué conceptuellement avec `get_recipe` et des questions contextuelles en lecture ; il n’implémente ni microphone, ni wake word, ni TTS, ni progression de recette dans #156.

## 8. POC minimal et critères de sortie

### POC proposé

Un client MCP standard local stdio appelle `search_recipes`, sélectionne un slug, appelle `get_recipe`, puis `validate_recipe`. Le corpus est le dépôt public en lecture seule et la validation est déléguée au core/contrat autorisé, pas réalisée par le client. Le scénario de démonstration doit pouvoir répondre à « trouve une recette de porc et donne-moi sa structure validée », avec provenance et absence de complétion implicite.

### Critères de sortie de la discovery

- ports/services core responsables des trois opérations identifiés et acceptés par les mainteneurs core ;
- projection JSON/MCP versionnée, y compris erreurs, provenance et inconnus ;
- matrice READ/ANALYZE/WRITE et politique stdio/distant approuvées ;
- threat model et limites de charge écrits ;
- corpus de fixtures et tests de contrat cross-repository définis ;
- décision sur `cookigram-mcp` utilisateur versus façade authoring séparée ;
- #151, #152, #154 et les éléments nécessaires de #51 suffisamment stabilisés pour que MCP ne réinterprète pas le domaine ;
- démonstration POC reproductible sans accès filesystem arbitraire ni WRITE ;
- critères de non-régression : aucune modification des règles #149, aucune invention de quantité/durée/équipement, et validation publique/core cohérente.

## 9. Prérequis manquants et sous-issues proposées

1. **#156.1 — Inventorier/valider les ports métier core** : façade de lecture, validation et provenance ; aucun transport MCP.
2. **#156.2 — Contrat d’échange et projections** : DTO, erreurs, pagination, inconnus, `content_sha/core_sha`, compatibilité `.gram` v1 ; revue conjointe public/core.
3. **#156.3 — Stabiliser le modèle composition** : consommer les décisions #149, puis conclure #151/#152 avant toute tool de composition.
4. **#156.4 — Threat model et matrice d’autorisation** : stdio sandboxé, HTTP/TLS, scopes, quotas, logs et non-divulgation.
5. **#156.5 — POC MCP READ/ANALYZE stdio** : trois outils, fixtures, tests de contrat et client de démonstration ; aucun WRITE et aucun déploiement.
6. **#156.6 — Décision de distribution** : package local, service distant ou deux façades ; critères de coût, disponibilité, offline et ownership.
7. **#156.7 — Client vocal expérimental** : uniquement après session d’exécution et contrats `current_step`/timers ; push-to-talk avant mains libres, avec commandes déterministes hors LLM.

Les sous-issues 1–2 et 4 sont des prérequis techniques ; 3 dépend de la roadmap produit ; 5 est le premier chantier d’implémentation limité ; 6–7 peuvent rester séparées. Aucun de ces items n’autorise à modifier `cookigram-core` depuis ce worktree.

## Références auditées

- [Issue #156](https://github.com/PierreCsn/cookigram/issues/156) — vision et hypothèse MCP.
- [Issue #149](https://github.com/PierreCsn/cookigram/issues/149) — décision PO sur complétude et rôles.
- [Issues #151](https://github.com/PierreCsn/cookigram/issues/151), [#152](https://github.com/PierreCsn/cookigram/issues/152) et [#154](https://github.com/PierreCsn/cookigram/issues/154) — discoveries non stabilisées.
- [Issue #51](https://github.com/PierreCsn/cookigram/issues/51) — Kitchen Scheduler v3.
- [`docs/PUBLIC-CONTRACT.md`](PUBLIC-CONTRACT.md), [`README.md`](../README.md) et [`AGENTS.md`](../AGENTS.md) — frontière et contrôles disponibles dans ce dépôt.
- `cookigram-core` privé : `docs/ARCHITECTURE.md`, `docs/CONTRACT.md`, `generator/models.py`, `generator/gram.py`, `generator/schema.py`, `generator/recipe_check.py`, `generator/menu_basket.py`, `generator/shopping.py`, `generator/smart_pairing.py` (branche `main`, audités le 2026-09-05).
