# CookiGram — Product Principles

> **Document de référence produit**  
> *Dernière mise à jour : 3 septembre 2026*  
> *Product Owner (User #1) : Pierre (@PierreCsn)*  
> *Product Lead : AI Assistant*  
> *Décision de référence : PDR-0001*

---

## 1. Cooking first (La cuisine avant tout)
L'expérience vécue en cuisinant activement sur le plan de travail a la priorité absolue sur toute considération esthétique secondaire ou métrique théorique.
* **Lisibilité à 1 mètre** : instructions contrastées, étapes atomiques sans pavés de texte indigestes.
* **Mains prises ou mouillées** : cibles tactiles généreuses (44 px min), défilement vertical naturel sans pièges gestuels ni chevauchements d'éléments d'action (`.cook-nav`).
* **Zéro friction opérationnelle** : les minuteurs, les réglages d'appareils (Thermomix) et les sous-étapes doivent être immédiatement accessibles sans navigation complexe.

## 2. Mobile & tablette en cuisine (Mobile first)
Le smartphone posé sur le plan de travail et la tablette sur son support sont les scénarios d'usage réels et primaires.
* **Aucun débordement horizontal** : la navigation doit être infaillible à 360 px, 390 px, 768 px et 820 px.
* **Respect des zones de sécurité** (`safe-area-inset`) : les barres de contrôles ne doivent jamais rogner les contenus.
* **Mode hors-ligne garanti** : la PWA doit charger instantanément en cuisine sans dépendre d'une connexion Wi-Fi capricieuse.

## 3. Simplicité et frugalité
Éviter l'enflure fonctionnelle, les dépendances superflues et les abstractions inutiles.
* **Architecture statique & modulaire** : pas de framework lourd côté client, JavaScript ES natif, CSS compartimenté, rapidité d'exécution.
* **Chaque interaction doit avoir une utilité tangible** : refuser les gadgets UI qui n'aident pas à cuisiner plus vite ou mieux.

## 4. Identité visuelle singulière et cohérente
CookiGram cultive une identité graphique chaleureuse et reconnaissable.
* **Illustrations originales** : privilégier le langage d'illustrations culinaires original plutôt que des photos génériques d'Internet.
* **Mise en valeur sur tous les écrans** : l'illustration ne doit pas être masquée sur mobile mais intégrée harmonieusement (bannière responsive, ratio respecté sans troncature punitive).
* **Icônes d'ingrédients cohérentes** : décliner l'identité manga culinaire en mini-icônes « spot illustration » (24-32 px, contours nets) pour scroller rapidement les listes d'ingrédients en cuisine sans surcharger le texte narratif.

## 5. Recettes structurées et données déterministes
L'information culinaire est un actif calculable et pérenne.
* **Format Gram comme source de vérité** : chaque recette est écrite en `.gram`, versionnée sous Git et validée strictement au build.
* **Nutrition traçable** : données CIQUAL vérifiées, transparence sur les approximations, tolérance zéro pour les valeurs inventées.
* **Réglages précis pour robots** : paramètres clairs (temps, température, vitesse, sens inverse, Varoma) intégrés nativement.

## 6. Le Product Owner comme utilisateur n°1
Le produit est conçu d'abord et avant tout pour les besoins, habitudes et retours qualitatifs de son créateur.
* **La pratique du terrain l'emporte sur la théorie** : un *"C'est pénible quand je cuisine"* est le signal produit le plus puissant qui soit.
* **Les meilleures pratiques sont des indices, pas des dogmes** : quand une recommandation d'expert entre en friction avec l'usage réel du PO, le compromis est explicité et le PO tranche.

## 7. Les spécialistes conseillent, le Product Lead orchestre
SEO, Performance, Accessibilité, Design et Architecture sont des conseillers d'excellence.
* Les recommandations spécialisées sont challengées au prisme de l'expérience culinaire globale.
* Le Product Lead filtre, synthétise, priorise et apporte des options argumentées au Product Owner sans lui imposer de fatigue décisionnelle.
* L'ordre des priorités de développement est fixé par les jalons GitHub et l'issue épinglée **#35**.
