# Règle Design & Technique : Icônes d'ingrédients (Codex & Agents)

> **Statut :** Validé par le Product Owner (@PierreCsn) & le Design Expert.  
> **Objectif :** Rendre les listes et les appels d'ingrédients immédiatement scannables à 1 mètre sur le plan de travail en cuisine sans surcharger l'interface.

---

## 1. Direction artistique & Style graphique

Les icônes d'ingrédients doivent prolonger harmonieusement l'univers visuel des illustrations de CookiGram (manga culinaire contemporain, chaleureux, gourmand, type *Studio Ghibli* / *Shokugeki no Soma*).

### Directives de style :
* **Type visuel : « Spot icon » ou « Sticker culinaire »** :
  * Silhouette **immédiatement identifiable** au premier coup d'œil (ex: forme typique d'un oignon jaune avec ses radicelles, pavé de saumon avec ses stries nettes, gousse d'ail galbée).
  * **Contour encré net et lisible** : ligne d'encrage fine foncée (brun très sombre ou noir doux, pas de flou).
  * **Couleurs franches et chaleureuses** : palette restreinte de 2 à 3 teintes propres à l'aliment.
  * **Ombrage sobre (cel-shading)** : une zone de lumière franche et une ombre douce, sans micro-textures complexes.
  * **Fond transparent** obligatoire.

### ⛔ Ce qu'il ne faut PAS faire :
* **Ne JAMAIS générer une « miniature » d'une grande illustration** : à 24 px ou 32 px, les détails fins, dégradés d'aquarelle et herbes ciselées deviennent une tache floue et illisible.
* Pas de texte, lettres, étiquettes ou emballages de marque dans l'icône.
* Pas d'ombres portées extérieures démesurées.
* Pas d'effet 3D brillant ou photoréaliste façon emojis Apple/Google.

---

## 2. Spécifications techniques & Formats

* **Grille de référence d'affichage** : **24×24 px** (standard) et **32×32 px** (mode cuisine / grand format).
* **Format source privilégié** : **SVG vectoriel** (optimisé, sans balises superflues, viewBox standard `0 0 32 32`).
* **Format matriciel alternatif** : **WebP transparent 64×64 px** (densité Retina @2x), poids inférieur à **2 Ko** par icône.
* **Emplacement dans le dépôt** :  
  `static/icons/ingredients/<ingredient_id>.svg` (ou `.webp`)
* **Nommage strict** : Doit correspondre exactement à la clé de l'ingrédient déclarée dans `.gram/ingredients.yaml` (ex: `oignon`, `ail`, `huile_olive`, `beurre`, `sel`, `poivre`, `creme_fraiche`, `parmesan`, `saumon`, `riz`).

---

## 3. Règles d'intégration UI (Où les afficher ?)

### ✅ Emplacements autorisés et recommandés :
1. **Liste des ingrédients sur la fiche recette (`recipe.html`)** :  
   En début de ligne (à gauche du nom de l'ingrédient ou de la case à cocher), en taille 24×24 px. Permet un balayage visuel ultra-rapide.
2. **Bloc « Ingrédients de l'étape active » en Mode Cuisine (`cook.html` — Issue #37)** :  
   En taille 28×28 ou 32×32 px aux côtés des quantités pour une lisibilité maximale à 1 mètre avec les mains occupées.
3. **Modale d'évaluation de courses (`modal.html`)** :  
   Devant chaque article trié par rayon pour humaniser la liste de courses.

### ❌ Emplacements strictement INTERDITS :
* **Au milieu des phrases de texte dans les étapes de préparation** (ex: *« Verser les [icône] carottes et l'[icône] huile dans le bol »*).  
  *Justification UX :* Insérer des images dans le corps de texte hache la hauteur de ligne (`line-height`), perturbe la vitesse de lecture et crée un effet « message WhatsApp surchargé d'émojis ». Dans le paragraphe d'instructions, le texte doit rester pur.

---

## 4. Tolérance de repli (Graceful Degradation)

* L'application de CookiGram compte plus de 150 ingrédients.
* **Tolérance zéro au conteneur vide ou à l'image cassée** : Si un ingrédient n'a pas encore son icône dédiée, l'interface doit s'afficher en mode texte pur sans décalage, espace vide parasite ni icône d'erreur.
* **Déploiement par lots prioritaires (Règle 80/20)** :  
  Codex doit commencer par le **Lot Pilote des 35 ingrédients les plus fréquents** du corpus CookiGram :
  `oignon`, `ail`, `huile_olive`, `beurre`, `sel`, `poivre`, `creme_fraiche`, `parmesan`, `saumon`, `poulet`, `boeuf`, `porc`, `riz`, `pates`, `carotte`, `pomme_de_terre`, `echalote`, `citron`, `tomate`, `concentre_tomate`, `lait_coco`, `curry`, `champignon`, `vin_blanc`, `bouillon_volaille`, `brocoli`, `epinard`, `moutarde`, `farine`, `sucre`, `persil`, `gingembre`, `coriandre`, `piment`.
