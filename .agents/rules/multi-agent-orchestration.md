# Orchestration Tri-Agents & Gestion Stratégique des Quotas (AGY, OpenCode, Codex) 🌐

Ce document standardise la collaboration opérationnelle entre les trois runtimes d'agents autonomes utilisés sur CookiGram : **Antigravity (AGY)**, **OpenCode** et **Codex**.

---

## 1. Profils des Runtimes & Écosystèmes de Quotas

Chaque agent dispose de modèles de prédilection, de fenêtres de contexte et de réservoirs de quotas distincts :

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. AGY (Antigravity CLI / IDE)                                         │
│ • Moteur : Google Gemini (Gemini 2.5 Pro, Flash, Flash-Lite)          │
│ • Forces : Contexte géant (1M+ tokens), sous-agents natifs (tree),     │
│   scheduler, gestion multi-dépôts, exécution de tâches d'arrière-plan. │
│ • Quota : Quotas Google API (TPM / RPM par palier d'organisation).     │
├────────────────────────────────────────────────────────────────────────┤
│ 2. OpenCode                                                            │
│ • Moteur : Multi-Fournisseurs (Claude 3.5 Sonnet, DeepSeek, Gemini...) │
│ • Forces : Précision chirurgicale sur le code frontend & CSS (Claude),  │
│   flexibilité de bascule sur des modèles très économiques (DeepSeek).  │
│ • Quota : Quotas distincts par clé d'API (Anthropic, DeepSeek, etc.).  │
├────────────────────────────────────────────────────────────────────────┤
│ 3. Codex (OpenAI CLI / Agents)                                         │
│ • Moteur : OpenAI (GPT-4o, GPT-4o-mini, o1-mini, o3-mini)              │
│ • Forces : Rigueur extrême de formatage YAML/JSON, validation syntaxique│
│   stricte, génération de tests unitaires et scripts autonomes.        │
│ • Quota : Quotas OpenAI API (Usage Tiers / Monthly Limits).           │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Matrice d'Affinité & Répartition Optimale des Quotas

Pour éviter de saturer un quota coûteux sur des tâches secondaires, les rôles sont distribués selon leurs forces naturelles :

| Domaine de Travail | Agent Recommandé | Modèle Privilégié | Justification Quota & Performance |
| :--- | :--- | :--- | :--- |
| **Product Lead & Coordination** | **AGY** | `gemini-2.5-pro` | Exploite la vision macro, le scheduler et la gestion multi-espaces (`/home/pierrecsn/Work/...`) sans consommer de tokens sur d'autres quotas. |
| **Recherche, Veille & Audit Rapide** | **AGY** | `gemini-2.5-flash-lite` | Consommation ultra-frugale (Tier 1) avec fenêtre de contexte massive pour ingérer du code ou des sitemaps. |
| **Ingénierie Frontend & UX (PWA, CSS)** | **OpenCode** | `claude-3-5-sonnet` | La finesse de Claude 3.5 Sonnet sur les styles CSS (`clamp()`, cibles tactiles, Dark Mode) évite les itérations inutiles. |
| **Dev Moteur Déterministe (Python)** | **OpenCode** ou **AGY** | `gemini-2.5-flash` | Rapport qualité/vitesse idéal pour l'implémentation de modules Python typés (`generator/`). |
| **Recettes `.gram` & Données CIQUAL** | **Codex** ou **OpenCode** | `gpt-4o-mini` / `flash` | Modèle rapide à faible coût parfait pour la conformité rigoureuse du schéma YAML et des tags Gram. |
| **Tests E2E & Stabilité (Playwright)** | **OpenCode** ou **AGY** | `gemini-2.5-flash` | Analyse rapide des traces de navigation sans saturer les quotas lourds. |

---

## 3. Protocole de Continuité & Bascule en Cas de Quota Atteint (Failover)

Si un agent atteint un plafond de quota (`429 RateLimitError` ou épuisement mensuel) :

1. **Aucun blocage de chantier :**
   Le travail ne s'arrête pas. Grâce au registre distribué [`.agents/claims.json`](../claims.json), l'état exact du travail est conservé.
2. **Procédure de Relève (Handover) :**
   * L'agent bloqué met à jour `claims.json` avec l'état courant et commite son travail partiel sur sa branche Git active.
   * L'agent de relève (ex: OpenCode prenant le relais d'AGY, ou Codex prenant le relais d'OpenCode) consulte `.agents/STATUS.md`, tire la branche et poursuit l'implémentation.
3. **Bascule de Fournisseur au sein d'OpenCode :**
   * Si le quota Anthropic (Claude) est temporairement saturé, OpenCode bascule automatiquement sur `google/gemini-2.5-flash` ou `deepseek/deepseek-chat` via `opencode.json`.

---

## 4. Règle d'Or d'Interopérabilité : Source Unique de Vérité

Pour que les 3 runtimes soient interchangeables sans friction :
* **Interdiction de dupliquer la documentation :**
  Les règles métier résident **exclusivement** dans `.agents/roles/`, `.agents/skills/` et `.agents/rules/`.
* **Adaptateurs légers par outil :**
  - **AGY** lit `GEMINI.md` et `.agents/`
  - **OpenCode** lit `opencode.json` et `.opencode/agents/` (qui pointent vers `.agents/`)
  - **Codex** lit `AGENTS.md` et `.agents/`
* **Validation Déterministe Transversale :**
  Tous les agents exécutent la même commande de contrôle atomique :
  ```bash
  python -m generator.recipe_check
  ```
  Le verdict de conformité est mathématique et identique quel que soit l'agent ou le modèle.
