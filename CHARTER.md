# CookiGram — Charte Fondatrice & Manifeste Open-Source

> **« Le Système d'Exploitation de la Cuisine · Local-First, Libre et Conçu pour le Plan de Travail »**  
> *Fondateur & Utilisateur n°1 : Pierre Cousin (@PierreCsn)*  
> *Licence : MIT (Open Source & Logiciel Libre)*  
> *Date d'adoption : 3 septembre 2026*  
> *Décision de référence : PDR-0004*

---

## 1. Pourquoi CookiGram existe

Cuisiner est l'un des actes les plus concrets, créatifs et régénérants de notre quotidien. C'est une activité physique : on touche des ingrédients, on manie des couteaux, on écoute le crépitement d'une poêle, on sent les effluves d'un bouillon, on surveille une cuisson.

Pourtant, le monde numérique a profondément dégradé ce moment :
* Les sites de recettes sont devenus des pièges publicitaires illisibles, saturés de bannières clignotantes, de vidéos intrusives et d'anecdotes verbeuses conçues pour manipuler les moteurs de recherche.
* Les applications culinaires commerciales enferment les recettes dans des bases propriétaires, exigent des abonnements mensuels, vendent vos données comportementales et vous interrompent en pleine cuisson pour vous vendre des ustensiles.
* Les systèmes dits « intelligents » délirent sur des plannings impossibles ou demandent de peser son frigo comme un contrôleur de gestion.

**CookiGram est né d'un refus de ce modèle.**  
CookiGram existe pour être le **copilote silencieux, élégant et infaillible** de votre cuisine : l'outil qui libère votre esprit, organise vos préparations et vous redonne le plaisir pur de cuisiner sans stress.

---

## 2. Le concept du « Produit Égoïste Éclairé »

CookiGram n'a pas été conçu pour satisfaire des investisseurs, cocher des critères d'incubateurs ou maximiser un taux de clic.

> **CookiGram est construit d'abord et avant tout pour son créateur et utilisateur n°1.**

Cette philosophie — que nous appelons **le Produit Égoïste Éclairé** — s'inspire directement des plus beaux succès de l'histoire du logiciel libre :
* **Linux et Git** ont été créés par Linus Torvalds pour résoudre ses propres blocages de développement ;
* **SQLite** a été bâti par Richard Hipp pour fonctionner de façon fiable et autonome dans un sous-marin ;
* **Obsidian** est né du besoin viscéral de ses fondateurs de posséder leurs notes en fichiers texte sur leur disque dur.

En construisant CookiGram avec une exigence absolue pour vous-même :
1. **La qualité n'est jamais sacrifiée** : Vous ne tolérerez aucun bug qui vous gêne avec les mains farinées un mardi soir.
2. **L'utilité est réelle** : Chaque ligne de code sert la pratique de la cuisine, pas un persona marketing abstrait.
3. **Le partage est généreux** : Ce qui résout brillamment vos problèmes de cuisine familiale et de batch cooking résoudra naturellement ceux de milliers d'autres passionnés.

---

## 3. Les Six Piliers du Manifeste

### I. Vos recettes vous appartiennent (Le format ouvert `.gram`)
Les recettes de famille et vos plats favoris sont un patrimoine personnel inestimable. Ils ne doivent jamais être prisonniers d'une application fermée qui peut disparaître demain.
* Dans CookiGram, chaque recette est un fichier texte brut `.gram` stocké chez vous, versionné avec Git.
* Lisible à l'œil nu par un humain dans 50 ans, calculable aujourd'hui par des machines.
* Zéro format binaire obscur, zéro verrouillage propriétaire (*vendor lock-in*).

### II. Local-First & Souveraineté Totale
La cuisine ne doit pas dépendre d'une connexion Wi-Fi défaillante ou d'un serveur distant en panne.
* CookiGram fonctionne **à 100 % hors-ligne** grâce à son architecture PWA (Progressive Web App).
* Vos favoris, vos notes de dégustation, votre historique de courses et vos temps d'exécution restent **strictement confinés à votre appareil**.
* Zéro tracking, zéro compte obligatoire, zéro télémétrie invasive. Votre vie privée en cuisine est inviolable.

### III. Zéro Publicité, Zéro Compromis
L'attention du cuisinier est précieuse.
* Aucune bannière publicitaire, aucun lien d'affiliation masqué, aucune recette sponsorisée par un industriel de l'agroalimentaire.
* CookiGram est un espace pur de gastronomie, d'apprentissage et de sérénité.

### IV. Frugalité & Vitesse Instantanée (Software Craftsmanship)
Une bonne application en cuisine se fait oublier.
* Pas de framework JavaScript de 30 mégaoctets qui met 5 secondes à démarrer.
* Du code web moderne, des modules JavaScript natifs, du CSS modulaire compilé à l'éclair et un affichage instantané.
* Tout est conçu pour être **lisible à 1 mètre de distance** et manipulable d'un tap rapide avec un doigt mouillé ou à la voix.

### V. Le Déterminisme Culinaire (L'IA comme assistant, jamais comme oracle)
La cuisine repose sur la chimie, la physique et le respect des temps : un poulet mal cuit rend malade, une sauce trop attendue tranche.
* **L'IA (LLM)** intervient là où elle excelle : comprendre le langage naturel, transcrire des recettes, suggérer des associations de saveurs créatives et expliquer des tours de main.
* **Le cœur de CookiGram reste 100 % déterministe** : les calculs de portions, la nutrition CIQUAL, les minuteurs et l'ordonnancement mathématique multi-plats (solveur CP-SAT) sont garantis par des algorithmes mathématiques vérifiés sans la moindre hallucination.

### VI. Le Respect de la Recette comme Source de Vérité
L'application ne réécrit jamais arbitrairement le geste d'un chef ou la recette d'une grand-mère.
* La recette définit **ce qui doit se passer**.
* CookiGram aide le cuisinier à **comprendre, planifier et réussir l'exécution**.

---

## 4. Licence Libre & Esprit Communautaire

CookiGram est publié sous **Licence MIT** :
* Le code source et le moteur sont libres, ouverts et réutilisables par quiconque.
* Chacun est libre de cloner le dépôt, d'adapter l'outil à sa propre cuisine, d'ajouter ses propres recettes ou d'améliorer les algorithmes.

### Notre communauté idéale
CookiGram invite :
* Les passionnés de bonne chère qui cherchent la précision sans la prétention ;
* Les cuisiniers du quotidien (parents pressés, amateurs de batch cooking, adeptes de robots) en quête d'organisation ;
* Les artisans du logiciel libre qui croient que le web moderne peut être à la fois léger, beau, puissant et éthique.

---

## 5. La Promesse du Projet

> **« CookiGram restera toujours un outil pensé pour le plan de travail, taillé pour le geste de celui qui cuisine, libre de toute entrave commerciale et respectueux de ceux qui partagent le repas. »**
