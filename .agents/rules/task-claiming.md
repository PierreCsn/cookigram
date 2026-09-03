# Règle impérative : Verrouillage des tâches (Task Claiming) & Anti-Doublons

> **Règle absolue :** Aucun développeur ou agent ne doit commencer à coder sans avoir préalablement vérifié et posé un verrou explicite (*Claim*) sur la tâche. L'invention de travail non validé par le Product Owner est strictement interdite.

---

## 1. Prérequis pour entamer un travail
Un développeur ne peut prendre en charge une tâche que si :
1. Une **issue GitHub existe** sur le dépôt `PierreCsn/cookigram`.
2. L'issue porte le label **`potential-dev-work`** (donnant le feu vert officiel du Product Lead / Product Owner).
3. L'issue **N'EST PAS DÉJÀ RÉCLAMÉE** par un autre développeur (vérifier dans `.agents/claims.json` et l'absence du label `in-progress` sur GitHub).

---

## 2. Procédure de Claim obligatoire (Avant la première ligne de code)
Dès qu'un développeur choisit une tâche approuvée :
1. **Poser le Claim dans `.agents/claims.json`** :
   Ajouter son entrée dans `active_claims` avec son nom d'agent, l'issue, son workspace, le nom de sa branche et un timestamp ISO.
2. **Poser le label sur GitHub** :
   ```bash
   gh issue edit <id> --add-label "in-progress"
   gh issue comment <id> --body "Je prends en charge cette tâche sur la branche `feat/...`."
   ```
3. **Créer sa branche git isolée** :
   ```bash
   git checkout -b feat/<nom-court-de-la-feature>
   ```

---

## 3. Règle pour les autres développeurs : INTERDICTION DE DOUBLON
* Si une issue a un claim actif dans `claims.json` ou le label `in-progress` :
  **AUCUN AUTRE DÉVELOPPEUR NE DOIT Y TOUCHER.**
* Choisir une autre tâche approuvée dans le backlog ou s'arrêter.

---

## 4. Timeout et Heartbeat (Watchdog de 15 minutes)
* Un développement ne doit pas rester silencieux plus de **15 minutes**.
* Si un agent n'a produit aucun commit, push ou mise à jour de claim pendant plus de 15 minutes, il est considéré comme **bloqué (*stalled*)**.
* Le watchdog libère le claim pour ne pas bloquer le projet et neutralise les processus orphelins (ex: boucle infinie, rate limit non géré).

---

## 5. Libération du Claim
1. Dès que la PR est ouverte, passer le statut du claim à `pr_open`.
2. Dès que la PR est mergée dans `main`, déplacer l'entrée vers `completed_claims` et retirer le label `in-progress` de l'issue.

---

## 6. Protocole de vérification pré-PR (Qualité & Anti-Régression)
Avant d'ouvrir ou de fusionner toute PR, le développeur ou l'agent doit impérativement exécuter en local :
```bash
# 1. Vérification du contrat de données, des recettes et des icônes
pytest tests/test_schema.py tests/test_ingredients_database.py tests/test_ingredient_icons.py

# 2. Vérification du formatage et du linter
ruff check generator plugins tests
ruff format --check generator plugins tests
```

Tout ajout d'ingrédient dans `.gram/ingredients.yaml` doit obligatoirement respecter :
1. **Intégrité YAML** : Indentation rigoureuse à 2 ou 4 espaces (aucun décalage de bloc `nutrition`).
2. **Provenance** : Enregistrement miroir dans `.gram/ingredient-provenance.yaml` avec statut (`verified`, `estimated`, `manual`).
3. **Couverture d'icône** : Vérification que l'ingrédient résout bien une icône (`pytest tests/test_ingredient_icons.py`).

