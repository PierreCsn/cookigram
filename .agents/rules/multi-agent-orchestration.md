# Orchestration Tri-Agents & Stratégie des Quotas Réels (AGY, Codex, OpenCode) 🌐

Ce document définit la stratégie officielle d'affectation des travaux entre les 3 runtimes d'IA utilisés par Pierre Cousin (@PierreCsn), basée sur la réalité exacte de leurs abonnements et quotas.

---

## 1. Cartographie Réelle des Quotas & Runtimes

* **1. Codex (`gpt-5.6-luna`) — Le Workhorse Prioritaire (Quota quasi illimité) :**
  - **Profil :** Accès à l'ensemble des modèles d'abonnement OpenAI avec le modèle **`gpt-5.6-luna`** configuré.
  - **Statut de quota :** **Quasi illimité**. C'est le moteur à privilégier pour le développement intensif sans risque d'étranglement de quota.
  - **Rôle cible :** Gros chantiers d'implémentation logicielle (Senior Developer), refactorings profonds, génération massive de tests E2E et logique du solveur.

* **2. AGY (Antigravity CLI / IDE) — Le Chef d'Orchestre & Product Lead :**
  - **Profil :** Modèles Google Gemini (Gemini 2.5 Pro, Flash, Flash-Lite) pilotés dynamiquement par le Product Lead.
  - **Statut de quota :** Pilotage interne par AGY (Flash-Lite pour la recherche/CI, Flash pour le code nominal, Pro réservé aux arbitrages PO et architecture).
  - **Rôle cible :** Direction produit (Product Lead), cadrage avec @PierreCsn, coordination multi-dépôts (`cookigram` / `cookigram-core`), exécution de tests en arrière-plan et surveillance CI.

* **3. OpenCode — L'Agent d'Appoint Frugal (Modèles Gratuits) :**
  - **Profil :** Raccordé à des modèles gratuits (Free Tier / modèles légers).
  - **Statut de quota :** Débit et quotas limités par les paliers gratuits (RPM/TPM bas).
  - **Rôle cible :** Tâches d'appoint bien bornées, corrections de bugs isolés, relectures, audits ponctuels ne nécessitant pas de modèle lourd. Éviter de lui confier des sessions marathon complexes pour ne pas heurter de rate-limits.

---

## 2. Matrice d'Attribution Opérationnelle des Travaux

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🔴 CHANTIERS LOURDS & CODAGE INTENSIF                                  │
│ ➔ CODEX (gpt-5.6-luna — Quota illimité)                               │
│ • Kitchen Scheduler v3 (OR-Tools, Dual-Engine #94)                     │
│ • Refonte du Mode Cuisine (#28, timers wall-clock, sticky nav)         │
│ • Génération et refonte de suites de tests Playwright                  │
│ • Transcriptions et imports massifs de recettes .gram                  │
├────────────────────────────────────────────────────────────────────────┤
│ 🔵 PILOTAGE, ARBITRAGES PO & SUPERVISION TECHNIQUE                     │
│ ➔ AGY (Antigravity — Gestion dynamique par Product Lead)               │
│ • Arbitrages de fonctionnalités et cadrage PDR avec @PierreCsn         │
│ • Enquêtes multi-workspaces et audits d'architecture                   │
│ • Contrôle qualité, surveillance de CI et validation Git multi-dépôts  │
│ • Recherche documentaire et inspection ciblée (Flash-Lite à 0 token)   │
├────────────────────────────────────────────────────────────────────────┤
│ 🟢 TÂCHES D'APPOINT & AUDITS LÉGERS                                    │
│ ➔ OPENCODE (Modèles gratuits)                                          │
│ • Petits correctifs de style CSS ou templates isolés                   │
│ • Audits sémantiques et métadonnées SEO rapides                        │
│ • Vérification de fiches recettes uniques                              │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Coordination sans Conflit : Le Verrou Distribué `claims.json`

Puisque **Codex**, **AGY** et **OpenCode** interviennent sur le même dépôt :
1. **Règle absolue :** Aucun agent ne modifie de code sans avoir posé un claim officiel dans [`.agents/claims.json`](../claims.json) sur une issue approuvée (`potential-dev-work`).
2. **Clôture et Handover :**
   - À chaque fin de tâche ou en cas de pause, l'agent commite un chunk atomique, met à jour `claims.json` et pousse sur Git.
   - Si Codex termine un gros refactoring, AGY peut immédiatement prendre le relais pour lancer la vérification `verify-pipeline` et faire le point avec Pierre Cousin sans aucune friction.
