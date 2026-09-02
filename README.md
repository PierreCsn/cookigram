# CookiGram 🍳

[![Deploy GitHub Pages](https://github.com/PierreCsn/cookigram/actions/workflows/pages.yml/badge.svg)](https://github.com/PierreCsn/cookigram/actions/workflows/pages.yml)
[![Coverage](https://img.shields.io/badge/coverage-87%25-brightgreen.svg)](#tests-et-qualité)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](pyproject.toml)
[![Gram Language](https://img.shields.io/badge/Gram-Gram%20Language-orange.svg)](https://gram-lang.org)

Carnet de recettes statique, moderne et installable (PWA), propulsé par des fichiers culinaires `.gram`.

> 🌐 **Démo en direct :** [https://pierrecsn.github.io/cookigram/](https://pierrecsn.github.io/cookigram/)  
> 🇬🇧 **English documentation:** [README.en.md](README.en.md) | 🤝 **Contribuer :** [CONTRIBUTING.md](CONTRIBUTING.md)

Le projet utilise [Gram](https://gram-lang.org/fr/), un langage open source conçu pour écrire des recettes structurées, calculables et versionnables avec Git. Consultez la [documentation officielle de Gram](https://gram-lang.org/fr/docs/) pour découvrir la syntaxe complète et son écosystème.

## Fonctionnalités clés

- 📱 **PWA Offline-first** : consultable partout, sans connexion réseau, installable sur mobile & bureau ;
- 🍳 **Mode cuisine guidée pas-à-pas** : étapes grand format avec sous-étapes cochables interactives ;
- 🔍 **Recherche instantanée et filtres avancés** : recherche en temps réel par titre ou ingrédient, filtres rapides par catégorie (*volaille, poisson, porc, mijoté, curry, pâtes, gratin, soupe...*) et panneau de filtres avancés multi-tags ;
- 🎙️ **Commande vocale mains libres** : pilotez la recette (« *suivant* », « *précédent* », « *minuteur* ») sans toucher l'écran ;
- 🗣️ **Synthèse vocale intégrée** : lecture audio des instructions avec synthèse vocale naturelle du navigateur ;
- ⏱️ **Minuteurs multiples** : alertes sonores Web Audio, vibrations et reprise locale ;
- 🛒 **Évaluation intelligente des courses** : filtre le fond de placard, calcule les rayons et exporte directement vers **Google Keep** ;
- 📊 **Analyse nutritionnelle CIQUAL** : calcul automatique des calories et macronutriments (protéines, glucides, lipides) par portion ;
- 🤖 **Réglages pour robots culinaires (Thermomix)** : badges visuels compacts avec temps, température, vitesse, fouet et sens inverse ;
- 🌙 **Thème sombre & clair** : adaptation automatique aux préférences système ou bascule manuelle instantanée ;
- 🔒 **Maintien de l'écran allumé (Wake Lock)** : évite la mise en veille de l'écran pendant la cuisine.

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

Le projet est validé par une suite complète de tests automatisés atteignant **87% de couverture** :

```bash
# Exécuter les tests avec rapport de couverture
pytest --cov=generator --cov-report=term-missing

# Vérifier le style et le linting avec Ruff
ruff check generator tests
ruff format --check generator tests

# Vérifier le linting JavaScript avec Biome
npm ci
npm run lint

# Vérifier la cohérence de la base d'ingrédients et de provenance
pytest tests/test_ingredients_database.py
```

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

Créer un fichier `.gram` avec un frontmatter et une instruction par paragraphe :

```gram
---
title: Ma recette
portions: 4
prep_time: 15 min
total_time: 50 min
tags: [rapide]
source: https://example.com/ma-recette
author: Nom de l'auteur
scaling:
  enabled: true
  min_portions: 2
  max_portions: 8
  step: 1
  note: Les temps de cuisson restent inchangés.
---

[Cuire] Cuire les @pommes de terre{800 g} au #four{} pendant ~{35 min} à ^{190 C}.
```

Le générateur utilise un modèle canonique interne. L'adaptateur Gram du MVP
prend en charge actions, ingrédients, matériel, minuteurs et températures. Son
remplacement futur par le compilateur officiel ne modifiera ni les templates ni
les plugins.

`prep_time` et `total_time` sont affichés sur la fiche ; le temps de
préparation apparaît également dans le catalogue. Ils sont exportés dans
`_site/recipes.json` avec le reste du modèle canonique.

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

## GitHub Pages

Dans le dépôt GitHub, ouvrir **Settings → Pages → Source** et sélectionner
**GitHub Actions**. Chaque push sur `main` reconstruit et publie le site.
