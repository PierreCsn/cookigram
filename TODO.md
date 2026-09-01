# Roadmap CookiGram

Dernier audit : 1er septembre 2026.

## État du projet au moment de l'audit

- 23 recettes et 146 ingrédients référencés.
- 28 tests Python réussis.
- Couverture Python : 86 %.
- Ruff, Biome et génération complète du site réussis.
- Site généré : environ 4,5 Mo.
- Le worktree contient déjà de nombreux changements non commités : les consolider
  avant d'entamer un chantier transversal.

## P0 — Stabiliser les parcours principaux

- [x] Corriger le redimensionnement des portions dans `static/app.js` :
  initialiser `step` depuis `portionPicker.dataset.step` avant son utilisation.
- [x] Corriger la checklist et la liste de courses : remplacer la variable globale
  implicite `recipeSlug` par une valeur issue de `checklistEl.dataset.recipe` ou
  d'un attribut explicite de la page.
- [x] Vérifier qu'une erreur dans une fonctionnalité n'empêche pas
  l'initialisation des fonctionnalités suivantes (blocs initialisés via
  `initFeature`, gardes `speechSynthesis` fiabilisées).
- [x] Ajouter un test navigateur pour modifier le nombre de portions et vérifier
  le recalcul, les limites min/max et la persistance après rechargement.
- [x] Ajouter un test navigateur pour cocher, restaurer et réinitialiser la liste
  d'ingrédients.
- [x] Ajouter un test navigateur pour ouvrir la fenêtre de courses et copier ou
  partager la sélection.

> Note (2 sept. 2026) : les variables non déclarées `step`, `recipeSlug` et
> `steps` dans `app.js` ont été corrigées ; le mode cuisine ne levait plus de
> `ReferenceError`.

### Critère de sortie P0

- [ ] La recherche, les portions, la checklist, les courses et le mode cuisine
  fonctionnent sans erreur JavaScript sur une fiche recette représentative.

## P1 — Mettre en place un vrai filet de sécurité

- [x] Ajouter Playwright, avec une configuration adaptée au site statique.
- [ ] Couvrir au minimum les scénarios de bout en bout suivants :
  - [ ] recherche et filtres du catalogue ;
  - [x] changement du nombre de portions ;
  - [x] checklist et évaluation des courses ;
  - [ ] navigation dans le mode cuisine ;
  - [ ] démarrage, pause, reprise et remise à zéro d'un minuteur ;
  - [ ] comportement sans les API optionnelles de voix, partage et Wake Lock ;
  - [ ] installation et navigation hors ligne de la PWA.
- [x] Ajouter un contrôle de syntaxe JavaScript explicite à la CI
  (`node --check` sur `app.js` et `sw.js`).
- [ ] Faire échouer la CI sur les erreurs console non attendues des tests
  navigateur.
- [ ] Faire dépendre le déploiement GitHub Pages de la réussite de la CI, ou
  fusionner build, tests et déploiement dans un pipeline ordonné.
- [x] Aligner les versions Python annoncées dans le README et celles testées par
  la matrice CI, notamment Python 3.13.
- [ ] Remplacer le badge de couverture statique par une mesure générée, ou le
  mettre à jour automatiquement.

### Critère de sortie P1

- [ ] Aucun déploiement ne peut avoir lieu si le lint, le build, les validations
  de données ou un parcours utilisateur critique échouent.

## P1 — Formaliser le contrat des recettes

- [ ] Définir un schéma canonique pour le frontmatter `.gram`.
- [ ] Valider explicitement :
  - [ ] le titre, les portions et la présence d'au moins une étape ;
  - [ ] les types et valeurs de `tags`, `prep_time` et `total_time` ;
  - [ ] la cohérence de `scaling` (`min`, `max`, `step`, raison si désactivé) ;
  - [ ] la présence du fichier image déclaré ;
  - [ ] la source, l'auteur et les crédits photographiques requis ;
  - [ ] l'existence de chaque ingrédient dans la base locale ;
  - [ ] les durées, températures et réglages d'appareil pris en charge.
- [ ] Produire des erreurs de build précises avec fichier, champ et valeur en
  cause.
- [ ] Ajouter des tests de recettes malformées et de métadonnées invalides.
- [ ] Rendre tous les chemins de données indépendants du répertoire courant ;
  utiliser une racine de projet ou injecter explicitement les chemins.
- [ ] Décider si le parseur MVP accepte les constructions Gram inconnues avec un
  avertissement ou les refuse strictement.

### Critère de sortie du contrat de données

- [ ] Une recette incomplète ou incohérente bloque le build avec un diagnostic
  immédiatement exploitable.

## P2 — Fiabiliser les calculs nutritionnels

- [ ] Séparer le référentiel nutritionnel, le parsing des quantités, les
  conversions et le calcul par recette.
- [ ] Supprimer le fallback silencieux de 10 g pour une quantité inconnue.
- [ ] Ne plus traiter tous les millilitres comme des grammes sans densité propre
  à l'ingrédient.
- [ ] Stocker dans la base les densités, poids unitaires et conversions utiles
  plutôt que des heuristiques codées en dur.
- [ ] Signaler les ingrédients ignorés et les quantités non convertibles.
- [ ] Calculer et exposer un taux de couverture nutritionnelle par recette.
- [ ] Associer les valeurs affichées à leur source et à leur niveau de confiance
  (`verified`, `estimated`, `manual`, etc.).
- [ ] N'afficher un résultat nutritionnel que si son seuil de qualité est atteint,
  ou l'accompagner clairement d'un avertissement.
- [ ] Ajouter des tests pour les fractions, densités, unités, comptes, valeurs
  inconnues et mélanges de sources.
- [ ] Revoir le libellé « par portion (CIQUAL) » lorsqu'une recette contient des
  estimations ou des données provenant d'une autre source.

### Critère de sortie nutrition

- [ ] Chaque valeur affichée est traçable et son degré d'approximation est connu.

## P2 — Rendre la PWA réellement utilisable hors ligne

- [ ] Choisir et documenter une stratégie :
  - [ ] précharger toutes les recettes et leurs images ; ou
  - [ ] proposer un téléchargement hors ligne explicite par recette.
- [ ] Inclure `recipes.json` et les pages nécessaires dans la stratégie de cache.
- [ ] Ajouter une page de secours lorsqu'une ressource non téléchargée est
  demandée hors ligne.
- [ ] Définir les stratégies de cache séparément pour HTML, données, scripts,
  styles et images.
- [ ] Vérifier qu'une nouvelle version du service worker met à jour les assets
  sans laisser une interface incohérente.
- [ ] Tester l'installation fraîche, le mode avion, la mise à jour et le retour
  en ligne.
- [ ] Ajuster la promesse « consultable partout, sans connexion » si toutes les
  recettes ne sont pas disponibles après la première installation.

### Critère de sortie PWA

- [ ] Une recette déclarée disponible hors ligne reste intégralement utilisable
  en mode avion, image et mode cuisine compris.

## P2 — Réduire la dette frontend

- [ ] Découper `static/app.js` en modules par fonctionnalité :
  - [ ] thème et installation PWA ;
  - [ ] recherche et filtres ;
  - [ ] portions et parsing des quantités ;
  - [ ] checklist et courses ;
  - [ ] partage et export ;
  - [ ] mode cuisine et sous-étapes ;
  - [ ] minuteurs ;
  - [ ] voix, synthèse vocale et Wake Lock.
- [ ] Donner à chaque module une fonction d'initialisation indépendante et
  tolérante à l'absence de son HTML.
- [ ] Éliminer les dépendances à des variables globales implicites.
- [ ] Ajouter des tests unitaires JavaScript pour les fonctions pures, notamment
  le parsing et le redimensionnement des quantités.
- [ ] Remettre le CSS source dans un format maintenable ; minifier uniquement lors
  du build si nécessaire.
- [ ] Découper le CSS par domaine ou composant sans multiplier inutilement les
  requêtes de production.
- [ ] Extraire les fragments de template répétés, notamment les badges et icônes
  Thermomix, dans des macros Jinja.
- [ ] Afficher des icônes de matériel nécessaire (robot, Varoma, Cookeo, etc.)
  sur les vignettes des recettes du catalogue, en plus des fiches recette.
- [ ] Formaliser l'interface des plugins et éviter de recharger chaque module pour
  chaque recette.

### Critère de sortie frontend

- [ ] Chaque fonctionnalité peut être testée et modifiée sans dépendre de l'ordre
  d'exécution d'un script monolithique.

## P3 — Qualité produit et publication

- [ ] Réaliser un audit d'accessibilité clavier et lecteur d'écran.
- [ ] Vérifier le focus et la fermeture de la fenêtre modale de courses.
- [ ] Respecter `prefers-reduced-motion` pour les animations importantes.
- [ ] Tester les parcours critiques sur Chrome Android et Safari iOS.
- [ ] Vérifier la dégradation progressive des API Web non universelles : voix,
  partage, vibration, notifications, Wake Lock et presse-papiers.
- [ ] Définir des budgets de poids pour HTML, JavaScript, CSS et images.
- [ ] Ajouter des données structurées Schema.org `Recipe`.
- [ ] Ajouter les URL canoniques, métadonnées Open Graph et cartes sociales.
- [ ] Générer un sitemap et, si utile, un flux des nouvelles recettes.
- [ ] Mesurer Lighthouse dans la CI sans imposer de seuils instables au départ.
- [ ] Documenter une courte procédure de release et de retour arrière.

## P4 — Évolution du socle

- [ ] Étudier le remplacement du parseur MVP par le compilateur Gram officiel.
- [ ] Conserver le modèle canonique interne afin de ne pas coupler templates et
  plugins au compilateur.
- [ ] Construire des tests de compatibilité entre l'ancien adaptateur et le futur
  adaptateur officiel.
- [ ] Versionner l'interface des plugins et documenter leurs entrées/sorties.
- [ ] Automatiser davantage l'import de recettes sans réduire les contrôles de
  provenance, de licence et de scaling.

## Ordre de réalisation recommandé

1. Corriger les erreurs JavaScript P0.
2. Ajouter les premiers tests Playwright.
3. Bloquer le déploiement lorsque la CI échoue.
4. Valider strictement les recettes et rendre les chemins reproductibles.
5. Fiabiliser la nutrition et l'offline.
6. Modulariser le frontend.
7. Reprendre ensuite le développement de nouvelles fonctionnalités.

## Définition de « terminé » pour une tâche

- [ ] Le comportement est couvert par un test proportionné au risque.
- [ ] Le lint, les tests et le build complet réussissent localement et en CI.
- [ ] La documentation utilisateur ou contributeur est mise à jour si nécessaire.
- [ ] La modification fonctionne sans les API navigateur optionnelles.
- [ ] Aucune donnée nutritionnelle, provenance ou licence n'est inventée ou
  dégradée silencieusement.
