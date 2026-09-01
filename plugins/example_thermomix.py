"""Example plugin contract. Conservative suggestions only, never device control."""


def enrich(recipe):
    for step in recipe.steps:
        if step.action.casefold() == "mixer" and step.timers:
            step.plugins["thermomix"] = {
                "label": "Suggestion Thermomix",
                "instruction": f"{step.timers[0]['label']} · vitesse douce (à confirmer selon le modèle)",
            }

