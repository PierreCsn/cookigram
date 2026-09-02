# Règle Git : Commit et Push systématiques

Tout travail ou tâche achevé doit être systématiquement validé, commité et poussé sur le dépôt distant (`git push`).

## Checklist de fin de travail obligatoire :
1. Valider la qualité :
   - Python : `ruff check generator tests`, `pytest`
   - JavaScript : `npm run lint`, `npm test`
   - Build : `python -m generator.build`
2. Stager les modifications : `git add <fichiers>`
3. Créer un commit explicite : `git commit -m "..."`
4. Pousser sur le remote : `git push`
5. Vérifier `git status` : l'arbre de travail doit être 100% propre (`working tree clean`).
