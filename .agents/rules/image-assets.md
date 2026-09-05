# Règle — Assets d’illustration recette

Toute recette qui déclare `image_generation.prompt_file` doit avoir une
illustration publiée sous `static/images/` avant sa PR. Le placeholder système
est réservé aux recettes sans asset final et ne doit pas rester associé à un
prompt existant.

Avant livraison :

1. générer et contrôler l’image selon `.agents/skills/generate-recipe-image/` ;
2. enregistrer le prompt final dans `image-prompts/<slug>.md` et les métadonnées
   de génération dans le frontmatter ;
3. exécuter `python scripts/audit-recipe-images.py --check` ;
4. si la génération est différée, créer une issue d’asset visuel dédiée et
   reporter son numéro dans la PR.

L’audit accepte une recette sans `image_generation` utilisant le placeholder,
mais signale tout prompt existant dont l’image est absente ou placeholder.
