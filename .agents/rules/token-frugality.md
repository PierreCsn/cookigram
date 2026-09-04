# Règle d'Or : Frugalité en Tokens & Ordonnancement des Modèles ⚡

Cette directive définit la stratégie d'ingénierie pour **maximiser la qualité et la fiabilité des réalisations tout en minimisant drastiquement la consommation de tokens** sur l'ensemble de l'écosystème CookiGram.

---

## 1. Principe Directeur : Frugalité Éclairée

> **Chaque token consommé doit apporter une valeur mesurable.**  
> Utiliser un modèle de raisonnement lourd pour lister un répertoire ou reformater une variable est un gaspillage d'énergie et de quota. La qualité découle de la rigueur architecturale, pas de la verbosité du prompt.

---

## 2. Pilier 1 : Déterminisme d'Abord (Coût : 0 Token)

Conformément à la règle d'or **PDR-0004**, tout traitement pouvant être accompli de manière déterministe doit être délégué au code local sans solliciter le LLM :

| Tâche | ❌ Mauvaise Pratique (LLM) | ✅ Bonne Pratique (0 Token) |
| :--- | :--- | :--- |
| **Validation de recette** | Demander au LLM de lire le `.gram` | Exécuter `python -m generator.recipe_check <fichier>` (0.2 s) |
| **Calculs nutritionnels** | Faire deviner les calories ou lipides | Appeler `generator.nutrition.calculator` (table CIQUAL stricte) |
| **Mise à l'échelle portions**| Faire recalculer les grammes au LLM | Algorithme de ratio déterministe dans `portions.js` |
| **Contrôle de style / Lint**| Corriger la syntaxe via un prompt | Exécuter `ruff check --fix` ou `npm run lint` |
| **Typage statique** | Demander au LLM si les types sont bons | Exécuter `mypy generator/` |

---

## 3. Pilier 2 : Matrice de Tiering des Modèles (Model Tiering)

Les agents et sous-agents doivent sélectionner le modèle adapté à la difficulté cognitive réelle de la tâche :

```text
┌────────────────────────────────────────────────────────────────────────┐
│ TIER 1 — Économique / Rapide (Flash-Lite / GPT-4o-mini / Haiku)        │
│ • Recherche de code (grep, find)         • Inspection de logs CI       │
│ • Validation syntaxique rapide           • Opérations Git standards    │
│ • Formatage et vérification de statuts   • Audits légers               │
├────────────────────────────────────────────────────────────────────────┤
│ TIER 2 — Équilibré / Nominal (Flash / Claude 3.5 Sonnet / GPT-4o)      │
│ • Implémentation logicielle courante     • Rédaction de recettes Gram  │
│ • Tests E2E Playwright                   • Ergonomie CSS / JS          │
│ • Refactoring ciblé de composants        • Métadonnées & SEO           │
├────────────────────────────────────────────────────────────────────────┤
│ TIER 3 — Raisonnement Profond (Pro / Claude 3.5 Opus / o1 / o3)         │
│ • Arbitrages d'architecture (PDR)        • Solveur CP-SAT (v3)         │
│ • Synthèse stratégique avec le PO        • Concurrence réactive PWA    │
│ • Diagnostic d'anomalies complexes       • Refonte de schémas de base  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Pilier 3 : Élagage du Contexte (Prompt & Context Pruning)

1. **Personas Compacts :**
   - Éviter les mega-prompts système (> 500 lignes).
   - Les rôles définissent une identité concise (50-80 lignes) et renvoient vers les compétences modulaires (`.agents/skills/`).

2. **Lecture Ciblée de Fichiers :**
   - Ne jamais faire un dump complet d'un fichier de 1000 lignes quand seules 20 lignes sont concernées.
   - Utiliser `grep_search` pour localiser le symbole, puis inspecter la tranche exacte (`view_file` avec `StartLine` et `EndLine`).

3. **Chargement de Compétences à la Demande :**
   - Ne charger que le `SKILL.md` directement pertinent pour l'opération en cours (ex: `cooking-mode-ux` pour le Mode Cuisine, `engine-dev` pour le compilateur).

---

## 5. Pilier 4 : Concision des Échanges Multi-Agents

* **Pas de monologues répétés :** Inutile de ré-expliquer toute la charte du projet à chaque sous-agent. Donner un objectif clair, borné et outillé.
* **Retours factuels et référencés :** Le sous-agent retourne les fichiers modifiés, les statuts de tests et les lignes de code, sans régurgiter de longs blocs d'explications superflues.
* **Liens plutôt que copies :** Toujours créer des liens markdown (`[fichier.py](file:///chemin#L10-L25)`) au lieu de coller l'intégralité du code dans le transcript.
