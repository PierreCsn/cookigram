"""Thermomix parameter extractor for CookGram.

Parses time, temperature/Varoma, reverse direction (sens inverse), and speeds (cuillère, 1-10, turbo, pétrin)
to generate Cookomix-style visual badges with icons.
"""

import re


def parse_thermomix_settings(text: str, timers: list, temperatures: list) -> dict | None:
    raw = text.lower()

    # Detect if this step contains Thermomix instructions
    has_tmx = (
        "thermomix" in raw
        or "bol" in raw
        or "varoma" in raw
        or "vitesse" in raw
        or "sens inverse" in raw
        or "mijotage" in raw
        or "pulvéris" in raw
        or "hach" in raw
    )
    if not has_tmx and not timers and not temperatures:
        return None

    # Time label
    time_label = timers[0]["label"] if timers else ""
    if not time_label:
        m_time = re.search(r"(\d+(?:[.,]\d+)?\s*(?:s|sec|min|h))\b", raw)
        if m_time:
            time_label = m_time.group(1)

    # Temperature label
    temp_label = temperatures[0] if temperatures else ""
    if temp_label and not temp_label.endswith("°C") and temp_label.endswith("C"):
        temp_label = temp_label[:-1].strip() + "°C"
    if not temp_label:
        if "varoma" in raw:
            temp_label = "Varoma"
        else:
            m_temp = re.search(r"(\d+)\s*(?:°\s*c|degr[ée]s?)", raw)
            if m_temp:
                temp_label = f"{m_temp.group(1)}°C"

    # Reverse direction
    has_reverse = "sens inverse" in raw or "rotation inverse" in raw

    # Speed
    speed_val = ""
    speed_type = ""
    if "cuill" in raw or "mijotage" in raw:
        speed_val = "cuillère"
        speed_type = "spoon"
    elif "turbo" in raw:
        speed_val = "turbo"
        speed_type = "turbo"
    elif "pétrin" in raw or "épi" in raw:
        speed_val = "pétrin"
        speed_type = "dough"
    else:
        m_spd = re.search(r"vitesse\s*(\d+(?:[.,]\d+)?)", raw)
        if m_spd:
            speed_val = m_spd.group(1)
            speed_type = "blade"

    # If at least 2 parameters or a speed is found, generate the settings badge
    if speed_val or (time_label and temp_label) or has_reverse:
        return {
            "time": time_label,
            "temp": temp_label,
            "reverse": has_reverse,
            "speed": speed_val,
            "speed_type": speed_type or "blade",
        }
    return None


def enrich(recipe):
    is_tmx_recipe = (
        "thermomix" in recipe.tags
        or "thermomix" in recipe.metadata.get("appliances", {})
    )
    for step in recipe.steps:
        full_text = step.text + " " + " ".join(step.substeps)
        if is_tmx_recipe or "thermomix" in full_text.lower():
            settings = parse_thermomix_settings(full_text, step.timers, step.temperatures)
            if settings:
                step.plugins["thermomix_settings"] = settings
