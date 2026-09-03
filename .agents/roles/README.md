# Rôles et Profils d'Agents CookiGram 🍳

Ce dossier rassemble les profils système, personas et directives opérationnelles pour chaque agent ou modèle d'IA intervenant sur le projet **CookiGram**.

---

## Utilisation par les modèles et agents d'IA

Chaque fichier de ce dossier correspond à un rôle spécialisé dans l'équipe multi-agents. Lorsqu'un agent ou modèle démarre une tâche :
1. Consulter les directives générales du projet dans [`AGENTS.md`](../../AGENTS.md) et [`PRODUCT_PRINCIPLES.md`](../../PRODUCT_PRINCIPLES.md).
2. Charger et adopter le profil correspondant à sa spécialité ci-dessous.
3. Respecter scrupuleusement le workflow, la gouvernance produit et les règles de validation associées.

---

## Profils d'Agents

| Rôle | Fichier | Description & Responsabilités |
| :--- | :--- | :--- |
| **Senior Development Agent** | [`senior-developer.md`](senior-developer.md) | Ingénieur logiciel senior chargé de l'implémentation rigoureuse, incrémentale et vérifiée des tâches approuvées (workflow : *synchronize → understand → select approved work → investigate → plan → implement → test → visually verify → commit → push → update GitHub → synchronize again*). |

---

## Spécialités de l'équipe multi-agents CookiGram

* **Product** : Product Owner (@PierreCsn) & Product Lead (arbitrages et priorités fonctionnelles)
* **Recipe quality** : Qualité, exactitude et conformité des recettes Gram
* **Cooking execution** : Expérience d'assistance pas-à-pas en cuisine et interactions physiques
* **Web Design / UX** : Ergonomie mobile, design system et hiérarchie visuelle
* **SEO** : Découvrabilité, sitemap, balises canoniques, métadonnées et Schema.org
* **Accessibility** : Conformité WCAG 2.2 AA, contrastes et accessibilité moteur/visuelle
* **Performance** : Core Web Vitals (LCP, CLS, INP) et frugalité statique
* **Security** : Intégrité des dépendances, protection des données et validation des entrées
* **QA** : Couverture de tests, validation de non-régression et scénarios Playwright
* **Illustrations** : Icônes d'ingrédients SVG et illustrations culinaires
* **Development** : Senior Development Agent (implémentation logicielle)
