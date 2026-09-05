# Validation publique du contrat `.gram`

## État au 5 septembre 2026

Le contrat formel est décrit dans `cookigram-core/docs/CONTRACT.md`, version
`1.0`, et le schéma exécuté se trouve encore dans `cookigram-core/generator/`.
Cette spécification et ce code sont dans le dépôt privé. Aucun dépôt
`cookigram-contract`, package Python, release ou autre artefact public n'est
actuellement disponible.

La CI de ce dépôt ne doit donc pas copier le parser du core ni exécuter un
contrôle YAML simplifié présenté comme une validation `.gram`. Le job
`recipe-check` échoue explicitement tant que l'artefact officiel n'est pas
publié. Cela rend le blocage visible et empêche une PR de fork d'obtenir un
faux vert.

## Chemins de validation

| Contexte | Validation | Secret privé |
| --- | --- | --- |
| PR, y compris depuis un fork | Contrat public versionné (à activer dès sa publication) | Non |
| Push de confiance / exécution hors PR | `cookigram-core` épinglé par `.core-version`, `recipe_check` et build | Oui |

Le workflow ne transmet donc jamais `CORE_SSH_KEY` à une exécution de PR.
L'intégration privée reste complémentaire : elle vérifie le build et les
règles propres au moteur, mais ne remplace pas le contrat public.

## Pré-requis pour débloquer la validation des forks

Le dépôt `cookigram-core` doit publier, sous licence compatible, un artefact
installable ou une action réutilisable contenant le parser, le schéma et les
règles structurelles du contrat `1.0`, avec une version immuable. L'artefact
doit exposer une commande de validation retournant `0` si le contrat est
respecté et `1` sinon.

Après publication, le job public devra installer cette version exacte et
valider `recipes/` avec `.gram/ingredients.yaml` et
`.gram/ingredient-provenance.yaml`. Un test partagé devra alors utiliser une
recette invalide et vérifier que le contrat public et le core la rejettent sur
les règles communes.
