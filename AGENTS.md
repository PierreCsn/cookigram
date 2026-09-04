# Directives et règles du dépôt Recettes CookiGram 🍳

> **Dépôt officiel :** https://github.com/PierreCsn/cookigram  
> **Rôle du dépôt :** Carnet de recettes culinaires Gram, photographies, icônes et données nutritionnelles (PDR-0008).  
> **Dépôt moteur :** Le moteur de génération statique, la PWA, la CLI et la suite de tests système résident dans [`PierreCsn/cookigram-core`](https://github.com/PierreCsn/cookigram-core).

---

## 1. Chargement & Mission Fondamentale

Ce fichier est le point d'entrée pour tout agent d'assistance ou contributeur culinaire travaillant sur le corpus de recettes :
* **Découplage architectural (PDR-0008)** : Ce dépôt est purement axé sur le contenu culinaire, les images et les assets visuels. Aucun code de moteur ni de serveur n'est développé ici.
* **Le Product Owner (@PierreCsn) est l'utilisateur n°1** : CookiGram est conçu pour une exécution parfaite sur le plan de travail en cuisine réelle.
* **La recette est la source de vérité** : CookiGram aide à exécuter une recette sans créer silencieusement une autre recette.

---

## 2. 🍲 Contribution Culinaire & Standard Gram

Toute contribution de recette doit respecter scrupuleusement les standards du langage `.gram` :

### A. Hiérarchie & Granularité atomique (Issue #111) :
1. **Hiérarchie à deux niveaux :**
   * L'Étape `[Macro-action]` regroupe une phase logique de la recette (ex: `[Préparer la marinade]`, `[Cuisson des aromates]`).
   * Les sous-étapes `- ` sont les unités atomiques d'exécution sur le plan de travail.
2. **Atomisme opérationnel (1 geste ou 1 réglage machine par puce) :**
   * Ne jamais mélanger une commande robot avec un geste manuel dans la même puce. Hacher est une puce. Racler les parois à la spatule est une puce distincte. Cuire est une puce distincte.
3. **Granularité des ingrédients (Max 2 à 3 éléments par puce) :**
   * Regrouper les ajouts par familles logiques au moment de verser. Jamais de bloc de 5+ ingrédients d'un coup.
4. **Mise en place préalable :**
   * Les découpes préalables doivent être précisées dans l'ingrédient (ex: `@oignons{150 g, coupés en quatre}`).
5. **Checkpoints sensoriels observables :**
   * Indiquer systématiquement l'état visuel ou olfactif d'arrêt (« jusqu'à ce que les oignons soient translucides », « la sauce doit napper la cuillère », « belle coloration dorée »).

### B. Matériel & Règle Thermomix TM31 (Issue #40) :
* Le Thermomix TM31 ne possède pas de palier à 120°C (sa molette passe de 100°C à Varoma).
* Si une recette prescrit une cuisson à `^{120 C}`, elle doit impérativement restreindre sa compatibilité Thermomix à :
  ```yaml
  appliances:
    thermomix:
    - TM5
    - TM6
    - TM7
  ```

### C. Ingrédients & Provenance CIQUAL :
* Tout ingrédient `@nom{quantité}` doit être répertorié dans `.gram/ingredients.yaml` avec son nom canonique ou alias.
* Toute nouvelle entrée d'ingrédient doit être documentée dans `.gram/ingredient-provenance.yaml`.

---

## 3. Validation & Quality Gate Culinaire

Avant de pousser toute modification de recette :

1. **Validation atomique (< 2 s)** (si l'environnement core est disponible) :
   ```bash
   python -m generator.recipe_check recipes/<slug>.gram
   ```
   Pour valider l'ensemble du carnet :
   ```bash
   python -m generator.recipe_check
   ```

2. **Validation YAML syntaxique de secours** :
   ```bash
   python -c "import yaml, glob; [yaml.safe_load(open(f, encoding='utf-8')) for f in glob.glob('.gram/*.yaml')]"
   ```

3. **Photographies & Prompts** :
   * Image finale : placer l'illustration sous `static/images/<slug>.jpg` (ou `.webp`).
   * Si aucune image n'est disponible immédiatement, utiliser `image: images/placeholder-recipe.jpg` et consigner le prompt dans `image-prompts/<slug>.md`.

---

## 4. Procédure Git & Clôture de Tâche

1. **Travailler sur une branche dédiée** : `recipe/<slug>` ou `fix/<description>`.
2. **Valider** : Exécuter le contrôle de conformité culinaire `generator.recipe_check`.
3. **Stager & Commiter** :
   ```bash
   git add recipes/ .gram/ static/images/
   git commit -m "feat(recipe): ajouter <titre de la recette> (#<issue>)"
   ```
4. **Pousser & Ouvrir la PR** :
   ```bash
   git push -u origin <branche>
   gh pr create --repo PierreCsn/cookigram --title "..." --body "Closes #..."
   ```
5. **Propreté de l'arbre** : Vérifier `git status` pour garantir un arbre de travail 100% propre (`working tree clean`).
