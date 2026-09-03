---
name: cooking-execution
description: Règles et directives d'assistance à l'exécution en cuisine pour CookiGram.
always_on: true
---

# Directives d'Exécution Culinaire CookiGram

## Règle Absolue
* **La recette canonique `.gram` est la source de vérité.**
* Interdiction stricte de modifier silencieusement les ingrédients, quantités, températures, durées ou techniques d'une recette.
* Toute inexactitude ou omission dans la recette est signalée comme anomalie `RECIPE DATA` à l'Expert Recette.

## Unité de Travail
Chaque étape doit répondre clairement aux questions opérationnelles :
* **QUOI** (Action)
* **AVEC QUOI** (Ingrédients de l'étape)
* **COMBIEN** (Quantités ajustées aux portions)
* **AVEC QUEL ÉQUIPEMENT** (Ustensiles, bols, accessoires robot)
* **COMMENT / RÉGLAGES** (Vitesse, sens inverse, puissance)
* **DURÉE / MINUTEUR** (Minuteur interactif)
* **CHECKPOINT** (État observable de fin d'étape)

## Taxonomie Obligatoire (Règle 24)
Toute constatation doit être qualifiée sous l'une des 6 étiquettes :
* `PRESENTATION` : Donnée existante mal affichée ou masquée.
* `STRUCTURE` : Donnée textuelle non extraite par le parseur.
* `GRAM` : Manque de syntaxe dans la spécification du langage Gram.
* `ENGINE` : Manque de logique applicative (JS / templates).
* `RECIPE DATA` : Donnée manquante ou incohérente dans la recette d'origine.
* `PRODUCT DECISION` : Choix d'expérience utilisateur nécessitant l'arbitrage du Product Owner.
