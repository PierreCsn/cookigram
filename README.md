# CookiGram 🍳

[![Deploy GitHub Pages](https://github.com/PierreCsn/cookigram/actions/workflows/pages.yml/badge.svg)](https://github.com/PierreCsn/cookigram/actions/workflows/pages.yml)
[![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)](#tests-et-qualité)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](pyproject.toml)
[![Gram Language](https://img.shields.io/badge/Gram-Gram%20Language-orange.svg)](https://gram-lang.org)

> **Le Système d'Exploitation de la Cuisine · Local-First, Libre et Conçu pour le Plan de Travail.**

🌐 **Démo en direct :** [https://pierrecsn.github.io/cookigram/](https://pierrecsn.github.io/cookigram/)  
📜 **Manifeste & Charte :** [CHARTER.md](CHARTER.md) | 🎯 **Principes Produit :** [PRODUCT_PRINCIPLES.md](PRODUCT_PRINCIPLES.md) | 🗺️ **Roadmap v1–v10 :** [Issue #51](https://github.com/PierreCsn/cookigram/issues/51) | 🤝 **Contribuer :** [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Philosophie : Le « Produit Égoïste Éclairé »

CookiGram n'a pas été conçu pour maximiser des clics publicitaires ou vendre des abonnements. Il est construit d'abord et avant tout pour son créateur et utilisateur n°1 ([CHARTER.md](CHARTER.md)), selon les principes du logiciel libre et du **Local-First** :

* **Vos recettes vous appartiennent** : Chaque recette est un fichier texte brut [`.gram`](https://gram-lang.org/fr/) stocké chez vous, versionné avec Git, calculable par des machines et lisible dans 50 ans sans format propriétaire.
* **Local-First & 100% Hors-Ligne** : Fonctionne sans réseau 4G sur votre plan de travail grâce à l'architecture PWA. Zéro compte forcé, zéro tracking, confidentialité absolue.
* **Zéro Publicité, Zéro Sponsoring** : Aucun encart commercial, aucune recette sponsorisée pour préserver la sérénité en cuisine.
* **Frugalité & Vitesse Instantanée** : Pas de framework JavaScript obèse : du HTML sémantique, des ES Modules natifs, du CSS modulaire et un affichage instantané lisible à 1 mètre.
* **Déterminisme Culinaire** : L'IA (LLM) aide à comprendre et formuler, mais les calculs nutritionnels, les portions, les minuteurs et l'ordonnancement mathématique sous contraintes sont garantis à 100 % par des algorithmes stricts sans hallucination.

---

## Fonctionnalités clés

- 📱 **PWA Offline-first complète** : 38 recettes emblématiques consultables partout, sans connexion réseau, installable sur mobile & bureau ;
- 🍳 **Mode cuisine guidée pas-à-pas (Cooking First)** :
  - **Ingrédients pour cette étape** : carte contrastée isolant les ingrédients requis (« Nécessaire maintenant ») au-dessus de chaque action ;
  - **Sous-étapes interactives** : décomposition en gestes atomiques avec cases à cocher persistées localement ;
  - **Mains libres total** : commande vocale (*« suivant »*, *« précédent »*, *« minuteur »*) et synthèse vocale naturelle ;
  - **Maintien de l'écran allumé (Wake Lock)** : l'écran ne s'éteint jamais pendant la préparation ;
- ⏱️ **Minuteurs intégrés & durées composées** : alertes sonores Web Audio mélodieuses, vibrations et gestion des durées scalaires ou composées ;
- 🌶️ **Aide à la décision anti-fatigue** :
  - Affichage du **temps total d'exécution** en gras sur les cartes pour arbitrer en 2 secondes ;
  - Nombre de portions réelles et badge d'indicateur de piquant (`🌶️`) pour les repas familiaux ;
  - Recherche instantanée par titre ou ingrédient et filtres par catégories culinaires ;
- 🤖 **Réglages pour robots culinaires (Thermomix)** : badges visuels Cookomix (durée, température, Varoma, sens inverse, vitesse cuillère ou lames, accessoires) ;
- 📊 **Analyse nutritionnelle CIQUAL traçable** : calcul automatique des calories et macronutriments (protéines, glucides, lipides) par portion issu de l'ANSES ;
- 🛒 **Évaluation intelligente des courses** : filtre les basiques de placard, classe les ingrédients par rayon et exporte en 1 clic vers **Google Keep** ;
- 🧠 **Outillage et compétences d'ingestion IA** : skill d'agent standardisé ([`import-recipe-gram`](.agents/skills/import-recipe-gram/SKILL.md)), contrat de schéma strict (`generator/schema.py`) et réconciliation d'ingrédients (`.gram/ingredients.yaml`) ;
- 🌙 **Thème sombre & clair** : adaptation automatique aux préférences système ou bascule manuelle instantanée ;
- 🌐 **SEO & Données structurées** : Schema.org `Recipe` JSON-LD avec sous-étapes (`HowToStep` / `HowToDirection`), Open Graph, `sitemap.xml`, canonicals, et flux RSS (`feed.xml`).

---

## Savoir-faire et import assisté par LLM / IA

L'une des forces majeures de CookiGram réside dans son architecture pensée pour et avec les agents IA (LLM). Le projet intègre un savoir-faire complet pour permettre à un modèle de langage (Claude, Gemini, GPT, etc.) de sourcer, structurer et intégrer des recettes sans dégradation de qualité :

- **Skill d'importation standardisée** ([import-recipe-gram](.agents/skills/import-recipe-gram/SKILL.md)) : guide pas-à-pas pour les agents (syntaxe Gram, étapes atomiques, sous-étapes, réglages robots, extraction d'images libres de droits et mentions légales) ;
- **Contrat canonique strict** (`generator/schema.py`) : validation déterministe au build bloquant toute recette incomplète, mal typée ou incohérente ;
- **Réconciliation automatique de la base d'ingrédients** (`.gram/ingredients.yaml`) : vérification systématique de l'existence de chaque ingrédient, résolution des synonymes et traçabilité de la provenance (`.gram/ingredient-provenance.yaml`) ;
- **Fiabilisation des données culinaires** : durées, températures, grammages réels et portions calibrées pour éviter les approximations et garantir un rendu parfait dans le mode cuisine guidée et le calcul nutritionnel.


## Démarrage rapide et développement

```bash
# 1. Cloner le dépôt et configurer l'environnement virtuel
git clone https://github.com/PierreCsn/cookigram.git
cd cookigram
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate sous Windows

# 2. Installer les dépendances (avec outils de dev)
pip install -e '.[dev]'

# 3. Construire le site statique
python -m generator.build

# 4. Prévisualiser localement
python -m http.server 8000 -d _site
```

Ouvrir [http://localhost:8000](http://localhost:8000) dans votre navigateur. Les recettes se trouvent dans `recipes/`.

## Tests et qualité

Le projet est validé par une suite complète de tests automatisés (Python & JavaScript) atteignant **89% de couverture**.

> **Environnement CI unifié :** L'intégration continue (`ci.yml`) s'exécute sur une version unique **Python 3.12** (alignée avec les jobs Playwright E2E et de déploiement GitHub Pages), divisant le temps de pipeline par trois. La compatibilité descendante avec Python 3.11+ est garantie statiquement via Ruff (`target-version = "py311"`) et Mypy (`python_version = "3.11"`).

```bash
# Tests unitaires Python avec rapport de couverture
pytest --cov=generator --cov-report=term-missing

# Tests unitaires JavaScript (fonctions pures, parsing de quantités, normalisation vocale)
npm run test:unit

# Tests end-to-end Playwright (simulateur de parcours navigateur et mode hors ligne)
npm run test:e2e

# Vérifier le style et le linting Python avec Ruff
ruff check generator plugins tests
ruff format --check generator plugins tests

# Vérifier le linting JavaScript avec Biome
npm run lint

# Contrôler la syntaxe JavaScript
node --check static/app.js
node --check static/sw.js
for f in static/js/modules/*.js; do node --check "$f"; done

# Vérifier la cohérence de la base d'ingrédients et de provenance
pytest tests/test_ingredients_database.py
```

## Architecture frontend modulaire

L'interface de CookiGram est conçue sans framework lourd, selon une architecture en modules ES natifs (`type="module"`) et un découpage CSS par domaine :

- **Modules JavaScript (`static/js/modules/`)** :
  - `utils.js` : isolation de l'initialisation des fonctionnalités (`initFeature`) et notifications toast ;
  - `theme.js` : bascule sombre/clair, écoute des préférences système, prompt d'installation PWA et enregistrement du Service Worker ;
  - `portions.js` : parsing robuste des quantités culinaires (fractions, décimales, nombres mixtes), redimensionnement dynamique des portions et formatage ;
  - `checklist.js` : liste interactive des ingrédients cochables avec persistance `localStorage` par recette et variante ;
  - `shopping.js` : évaluation de placard, tri par rayon, sélection des fonds de placard et export formaté pour Google Keep (cases à cocher natives) ;
  - `search.js` : recherche textuelle instantanée normalisée (sans accents) et panneau de filtres multi-tags ;
  - `cook.js` : mode cuisine guidé pas-à-pas, sous-étapes cochables, opérations en parallèle et navigation clavier ;
  - `timers.js` : minuteurs interactifs avec synthèse sonore Web Audio multi-tons (carillon mélodieux et vibrations) ;
  - `voice.js` : synthèse vocale naturelle des étapes (`SpeechSynthesis`), reconnaissance vocale mains-libres (`SpeechRecognition`) et maintien de l'écran allumé (`WakeLock`) ;
  - `variants.js` : basculement dynamique et synchronisation de l'URL pour les méthodes alternatives.

- **Styles CSS par composant (`static/css/`)** :
  - Les styles sources sont découpés de manière lisible et maintenable en fichiers dédiés (`variables.css`, `base.css`, `topbar.css`, `catalogue.css`, `recipe.css`, `ingredients.css`, `modal.css`, `cook.css`, `timers.css`, `thermomix.css`) ;
  - Lors de la génération (`generator/build.py`), ces composants sont automatiquement concaténés dans `output/assets/app.css` afin de ne générer **aucune requête HTTP superflue** en production.

- **Macros Jinja réutilisables (`templates/macros.html`)** :
  - Centralisation du rendu des badges Thermomix (`tmx_badge`) et des vignettes d'appareils (`appliance_tags`), garantissant un affichage cohérent du catalogue au mode cuisine.


## Base d'ingrédients Gram

La base locale se trouve dans `.gram/ingredients.yaml`. Après l'ajout d'une
recette, la maintenir avec le CLI officiel :

```bash
gram db sync
gram db lint
gram db enrich
gram db validate --strict
```

Les densités et données nutritionnelles proposées par `gram db enrich` doivent
être relues avant d'être conservées.

La provenance et le niveau de confiance sont suivis dans
`.gram/ingredient-provenance.yaml`. CIQUAL/ANSES est privilégié pour les
aliments génériques français ; Open Food Facts sert aux produits de marque.
Une valeur choisie par un humain peut être marquée `manual` et `locked: true`
afin qu'aucun agent ne la remplace automatiquement.

## Ajuster le nombre de portions

Chaque recette déclare ses règles dans son frontmatter :

```yaml
portions: 4
scaling:
  enabled: true
  min_portions: 2
  max_portions: 8
  step: 1
  note: Les temps de cuisson ne sont pas recalculés.
```

Pour une recette précise qui ne peut pas être redimensionnée :

```yaml
scaling:
  enabled: false
  reason: Quantités calibrées pour le bol et le programme du Thermomix TM31.
```

La PWA recalcule les quantités numériques et mémorise le choix sur l'appareil.
Les temps et températures ne sont jamais ajustés silencieusement.

Les recettes d'appareil demandent une attention particulière. Si la source
propose plusieurs rendements mais modifie certaines quantités ou certains
réglages de façon non linéaire, CookiGram conserve une variante vérifiée et
désactive le calcul automatique. La raison doit être écrite dans
`scaling.reason`. Une prise en charge future pourra enregistrer plusieurs
variantes officielles plutôt que de les approximer.

## Ajouter une recette

Créer un fichier `.gram` avec un frontmatter YAML complet et des instructions découpées en étapes logiques :

```gram
---
title: Poulet rôti au citron
portions: 4
prep_time: 15 min
total_time: 1 h 05 min
spiciness: 0
description: Poulet doré à la peau croustillante, jus court parfumé au citron et éclats d'ail en chemise.
tags: [poulet, four, familial]
source: https://example.com/poulet-citron
author: Nom de l'auteur
scaling:
  enabled: true
  min_portions: 2
  max_portions: 8
  step: 1
  note: Les temps de cuisson restent inchangés.
flavors:
  pairing: [poulet, citron, ail, thym]
  notes: [rôti, acidulé, herbacé]
  harmony: "L'acidité vive du citron dégraisse la chair du poulet tandis que le thym infuse le jus court."
  tips: "Arroser le poulet avec son jus à mi-cuisson pour une peau dorée."
conservation:
  fridge_days: 3
  freezable: true
  reheat: "15 min au four à 150°C"
---

[Préchauffer] Préchauffer le #four{} à ^{200 C}.

[Assaisonner]
- Frotter le @poulet{1.5 kg} avec le @gros sel{1 c. à soupe} et le @thym frais{4 brins}.
- Glisser le @citron{1 pièce} coupé en deux et l'@ail{6 gousses} à l'intérieur.

[Rôtir] Enfourner sur une #plaque{} et cuire ~{50 min} jusqu'à ce que la peau soit bien dorée.
```

### Règles d'or d'une recette CookiGram

1. **Balisage systématique des ingrédients par étape (Cooking First)** : Chaque ingrédient incorporé à une étape **doit impérativement être balisé** `@ingrédient{quantité}` dans la ligne d'action ou de sous-étape (`- `). C'est ce balisage qui alimente la carte *« Ingrédients pour cette étape »* en Mode Cuisine.
2. **Intégrité temporelle** : `prep_time` et `total_time` doivent être renseignés et distincts (`total_time` englobe la préparation, les cuissons au four ou Varoma, et les temps de repos indispensables).
3. **Piquant décisionnel** : `spiciness: 0..3` (0: non épicé, 1: doux, 2: relevé, 3: pimenté).
4. **Description évocatrice** : 100 à 120 caractères décrivant saveurs et textures clés (pas de texte générique).
5. **Minuteurs stricts** : Durées scalaires uniques (`~{90 s}`, `~{4 min}`, `~{1 h}`).

### Déclarer un appareil et sa validation

Pour une recette liée à un appareil, séparer ce que dit la source de ce qui a
réellement été vérifié dans CookiGram :

```yaml
appliances:
  thermomix: [TM31, TM5, TM6, TM7]
source_appliances:
  thermomix: [TM5, TM6, TM7]
required_equipment:
  - Thermomix TM31, TM5, TM6 ou TM7
  - Varoma avec plateau vapeur
appliance_validation:
  TM31:
    status: human-tested
    portions: 6
    note: Version 6 portions testée par le propriétaire du projet sur un TM31.
```

`source_appliances` conserve la compatibilité annoncée par la source,
`appliances` liste les modèles utilisables après adaptation documentée et
`required_equipment` est affiché avant le démarrage. Une validation
`human-tested` ne doit être ajoutée qu'après le retour explicite de la personne
qui a cuisiné la recette, avec le rendement réellement testé.

### Variantes de préparation

Une recette peut proposer plusieurs méthodes sans recopier ses métadonnées ni
son tronc commun. Les variantes se déclarent dans le frontmatter. La première
est utilisée par défaut si aucune n'a `default: true`; une seule variante au
maximum peut être marquée par défaut. Les identifiants utilisent des lettres
minuscules, des chiffres et des tirets et sont uniques dans la recette.

Les étapes susceptibles d'être adaptées reçoivent un identifiant stable avec
la syntaxe `[identifiant | Titre de l'étape]`. Une variante peut ensuite les
`replace`, les `remove`, ou insérer des étapes `before`/`after`. Les références
inconnues et les identifiants dupliqués font échouer le build.

Exemple condensé de `roti-de-porc-sauce-echalote.gram` :

```gram
---
title: Rôti de porc sauce échalote
portions: 4
prep_time: 10 min
total_time: 1 h 15 min
appliances:
  thermomix: [TM31, TM5, TM6, TM7]
variants:
  - id: thermomix-varoma
    name: Thermomix / Varoma
    description: La méthode vapeur d'origine.
    default: true

  - id: sous-vide-four
    name: Sous-vide + finition au four
    description: Cuisson régulière, puis coloration et sauce en parallèle.
    prep_time: 20 min
    total_time: 4 h 35 min
    appliances:
      thermomix: [TM31, TM5, TM6, TM7]
      sous_vide: true
      oven: true
    equipment:
      remove: [Varoma]
      add: [machine sous vide, thermoplongeur, four avec gril]
    ingredients:
      remove: [eau, bouillon de légumes]
      replace:
        rôti de porc:
          name: rôti de porc
          quantity: 800 g
      add:
        - name: huile d'olive
          quantity: 1 c. à soupe
    steps:
      replace:
        steam-cook: |
          [sous-vide-cook | Cuire le rôti sous vide]
          - Cuire le @rôti de porc{800 g} dans un #sac sous vide{} ~{4 h} à ^{60 C}.
          - Récupérer le jus du sac, puis sécher soigneusement le rôti.
        make-sauce: |
          [finish-in-parallel | Colorer le rôti et réduire la sauce]
          - Lancer les deux opérations au même moment.
          || oven | Four : Colorer le rôti à ^{240–250 C} pendant ~{6 min} à ~{10 min}.
          || thermomix | Thermomix : Réduire les @échalotes{4 pièces}, le @jus de cuisson sous vide{tout le jus}, le @vin blanc{170 g} et la @maïzena{10 g} pendant ~{8 min}.
          - Finir la sauce pendant que le rôti repose.
      after:
        make-sauce:
          - |
            [optional-note | Vérifier la sauce]
            Rectifier l'assaisonnement avant de servir.
---

[prepare-roast | Préparer le rôti]
- Piquer le @rôti de porc{800 g} avec les @gousses d'ail{2 pièces}.
- Installer le #Varoma{}.

[steam-cook | Cuisson vapeur au Varoma]
Cuire ~{45 min} à ^{Varoma}.

[make-sauce | Préparer la sauce échalote]
Cuire les @échalotes{4 pièces} avec le @vin blanc{170 g} et la @maïzena{10 g}.

[serve | Tranchage et service]
Trancher, napper de sauce et servir.
```

Les listes `ingredients` et `equipment` sont facultatives : CookiGram les
recalcule d'abord à partir des étapes résolues, puis applique les opérations
`remove`, `replace` et `add`. Cela permet aussi de corriger explicitement un
élément qui n'apparaît pas dans le texte. Les temps et `appliances` héritent de
la recette et peuvent être redéfinis variante par variante.

Une ligne parallèle suit la forme
`|| identifiant | Libellé : instruction`. Les opérations sont regroupées
visuellement et restent cochables séparément en mode cuisine.

Le lien direct d'une méthode est
`/recipes/roti-de-porc-sauce-echalote/?variant=sous-vide-four` (et le même
paramètre fonctionne sur `cook/`). Sans paramètre, la méthode par défaut est
affichée. Une valeur inconnue revient à la méthode par défaut et l'URL est
nettoyée. La progression est mémorisée par identifiant d'étape : une étape
réutilisée conserve son état, tandis qu'une étape remplacée ne récupère pas
aveuglément l'état d'une étape portant le même numéro.

### Ajouter une photo

Placer l'image optimisée dans `static/images/`, puis déclarer son chemin relatif
aux assets dans le frontmatter. Les initiales du titre restent le fallback si
`image` est absent.

```yaml
image: images/ma-recette.jpg
image_credit:
  author: Nom du photographe
  source: https://example.com/page-de-la-photo
  license: CC BY-SA 4.0
  license_url: https://creativecommons.org/licenses/by-sa/4.0/
  modifications: Image redimensionnée et recadrée.
```

Pour une image sous licence avec attribution, conserver le nom de l'auteur, la
page source, la licence et les modifications éventuelles. La fiche recette
affiche automatiquement ces informations sous la photo.

### Générer une illustration originale

Le skill `.agents/skills/generate-recipe-image/` définit l'identité visuelle
CookiGram : illustration culinaire manga semi-réaliste, chaleureuse, horizontale
et fidèle à la recette. Il interdit d'utiliser comme référence une photo tierce
dont les droits ne sont pas établis, sépare clairement un simple test d'un
remplacement publié et documente l'outil, le prompt et la sélection humaine.

Gemini CLI découvre directement ce skill depuis `.agents/skills/`. Après un
ajout ou une modification, utiliser `/skills reload`, puis vérifier sa présence
avec `/skills list`. Si l'agent ne dispose pas d'un générateur d'images, le skill
lui demande de produire le prompt final sans prétendre avoir créé le fichier.

### Importer une recette du Web avec un agent

Le skill `.agents/skills/import-recipe-gram/` explique aux agents comment :

1. consulter la source originale et relever l'auteur ;
2. reformuler les instructions sans inventer les informations manquantes ;
3. associer chaque ingrédient à `.gram/ingredients.yaml` et compléter la
   provenance ;
4. décider explicitement si les portions sont calculables ;
5. exécuter les tests et générer le site.

Une page protégée peut nécessiter une capture ou un export fourni par
l'utilisateur. Les réglages d'un appareil ne doivent jamais être déduits d'une
recette incomplète.

## Intégration continue (CI) & GitHub Pages

Dans le dépôt GitHub, chaque pull request et chaque push sur `main` déclenche le workflow d'intégration continue (`ci.yml`) :
* **Validation unifiée** : Les suites de tests unitaires, de typage, de linting et de parcours E2E sont exécutées sous **Python 3.12** et **Node.js 22**.
* **Déploiement conditionnel** : GitHub Pages (`pages.yml`) ne reconstruit et ne publie le site en production que si tous les contrôles de la CI ont réussi avec succès.

## Fonctionnement hors ligne

Le build génère un service worker versionné qui précharge le catalogue,
`recipes.json`, toutes les fiches et tous les modes cuisine, les scripts, les
styles et les images. Après une première visite terminée, les 38 recettes sont
donc utilisables en mode avion, image comprise.

Les navigations HTML utilisent une stratégie **network-first** pour obtenir la
dernière version en ligne, avec repli sur le cache hors ligne. Les autres assets
utilisent **cache-first**. Le hash des assets change le nom du cache à chaque
version et l'ancien cache est supprimé lors de l'activation du nouveau service
worker.

## 🗺️ Feuille de route & Jalons de maturité (Kitchen OS)

CookiGram ne cherche pas à être un simple afficheur de recettes web, mais le **Système d'Exploitation de la Cuisine (Kitchen OS)**. Son développement s'articule autour de grands paliers d'expérience orientés vers le plan de travail ([PDR-0003](decisions/PDR-0003-validation-roadmap-strategique-v1-v10.md) & [ROADMAP_STRATEGIQUE.md](ROADMAP_STRATEGIQUE.md)) :

| Jalon | Nom | Statut | Expérience Cuisinier & Valeur Produit |
| :--- | :--- | :---: | :--- |
| **v1** | **Recipe OS** | ✅ **Livré** | **Le socle déterministe** : Fiches recettes canoniques `.gram`, portions dynamiques sans approximation, analyse nutritionnelle CIQUAL traçable, moteur de recherche instantané et fonctionnement 100% hors-ligne. |
| **v2** | **Cooking Copilot** | 🔶 **Sprint Actif** | **Le copilote du plan de travail** : Mode cuisine plein écran lisible à 1 mètre, minuteurs persistants avec alarme Web Audio, interactions vocales mains-libres, profil sensoriel (accords & piquant) et reconnaissance des ustensiles. |
| **v3** | **Kitchen Scheduler** | ⏳ *Prochain cap* | **Le chef d'orchestre multi-préparations** : Ordonnancement mathématique sous contraintes (solveur Google CP-SAT). Synchronisation automatique du four, des plaques et du robot pour que tous les plats d'un dîner soient prêts ensemble sans stress ([Issue #51](https://github.com/PierreCsn/cookigram/issues/51)). |
| **v4** | **Smart Meal Planner** | ⏳ *Planifié* | **La semaine sans charge mentale** : Planification des repas, mutualisation des ingrédients anti-gaspillage, liste de courses consolidée par rayons et export vers notes. |
| **v5+** | **Kitchen Intelligence** | ⏳ *Exploration* | **L'inventaire pragmatique & Local-First** : Suggestions intelligentes selon les restes du réfrigérateur et le fond de placard, personnalisation locale et respect absolu de la vie privée. |

---

## Licence

Ce projet est distribué sous [Licence libre MIT](LICENSE).  
Copyright (c) 2026 Pierre Cousin.
