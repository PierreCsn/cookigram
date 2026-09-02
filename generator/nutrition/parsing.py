"""Quantity and token parsing for recipe ingredients."""

from __future__ import annotations

import re

from .models import ParsedQuantity

UNICODE_FRACTION_VALUES: dict[str, float] = {
    "¼": 0.25,
    "½": 0.5,
    "¾": 0.75,
    "⅓": 1 / 3,
    "⅔": 2 / 3,
    "⅛": 1 / 8,
    "⅜": 3 / 8,
    "⅝": 5 / 8,
    "⅞": 7 / 8,
}

UNQUANTIFIED_TERMS = {
    "",
    "au gout",
    "au goût",
    "selon gout",
    "selon goût",
    "selon le gout",
    "selon le goût",
    "plus selon le gout",
    "plus selon le goût",
    "selon les gouts",
    "selon les goûts",
    "selon convenance",
    "facultatif",
    "a volonte",
    "à volonté",
    "quelques gouttes",
    "un filet",
    "selon preferences",
    "selon préférences",
}


def parse_value_token(token: str) -> float | None:
    """Parses a quantity token: '2', '0,5', '1/2', '1 1/2' or '1½'.

    Returns None when the token contains anything but a valid quantity.
    """
    token = token.strip()
    if not token:
        return None

    # Check for unicode fractions
    for char, value in UNICODE_FRACTION_VALUES.items():
        if char in token:
            whole = token.replace(char, "").strip()
            if not whole:
                return value
            whole_num = parse_value_token(whole)
            if whole_num is not None:
                return whole_num + value
            return None

    # Mixed numbers or fraction strings
    total = 0.0
    for part in token.split():
        part = part.replace(",", ".")
        if "/" in part:
            numerator, _, denominator = part.partition("/")
            if not re.fullmatch(r"\d+(?:\.\d+)?", numerator) or not re.fullmatch(r"\d+(?:\.\d+)?", denominator):
                return None
            try:
                den_val = float(denominator)
                if den_val == 0:
                    return None
                total += float(numerator) / den_val
            except ValueError:
                return None
        elif re.fullmatch(r"\d+(?:\.\d+)?", part):
            try:
                total += float(part)
            except ValueError:
                return None
        else:
            return None
    return total


def parse_range_or_value(token: str) -> float | None:
    """Parses a quantity that may be a range: '3 1/2 à 4', '1-2', '2 à 2 1/2', or a plain value."""
    token = token.strip()
    if not token:
        return None

    # Range with "à" or "a": "3 1/2 à 4", "2 à 3"
    if " à " in token or " a " in token:
        delimiter = " à " if " à " in token else " a "
        left, _, right = token.partition(delimiter)
        v1 = parse_value_token(left)
        v2 = parse_value_token(right)
        if v1 is not None and v2 is not None:
            return (v1 + v2) / 2.0

    # Range with hyphen: "1-2"
    hyphen_match = re.match(r"^(\d+(?:[.,]\d+)?)\s*-\s*(\d+(?:[.,]\d+)?)$", token)
    if hyphen_match:
        v1 = parse_value_token(hyphen_match.group(1))
        v2 = parse_value_token(hyphen_match.group(2))
        if v1 is not None and v2 is not None:
            return (v1 + v2) / 2.0

    return parse_value_token(token)


def eval_fraction(token: str) -> float:
    """Backwards-compatible single-token parser (decimal or plain fraction)."""
    value = parse_value_token(token)
    return float(value) if value is not None else 0.0


NUMBER_RE = r"(?:(?=.*[\d¼½¾⅓⅔⅛⅜⅝⅞])[\d\s.,/¼½¾⅓⅔⅛⅜⅝⅞-]+(?:\s*à\s*[\d\s.,/¼½¾⅓⅔⅛⅜⅝⅞]+)?)"


def parse_quantity(quantity_str: str) -> ParsedQuantity:
    """Parses any CookGram quantity expression into a structured ParsedQuantity."""
    raw = quantity_str.strip()
    norm = raw.casefold()

    total_m = re.search(r",\s*sur\s+(.+?)(?:\s+au total)?$", norm)
    if total_m:
        norm = total_m.group(1).strip()


    # Unquantified check
    clean_unquant = re.sub(r"[^\w\s]", "", norm).strip()
    if clean_unquant in UNQUANTIFIED_TERMS or not clean_unquant:
        return ParsedQuantity(
            value=None,
            unit="",
            raw=raw,
            is_unquantified=True,
            notes=raw,
        )

    # 1. Pattern: count with per-piece weight/volume: "4 pièces, env. 100 g chacun"
    m_each = re.search(
        rf"^({NUMBER_RE})\s*(?:pi[èe]ces?|pcs?)?,?\s*(?:env\.\s*)?([\d\s.,/¼½¾⅓⅔⅛⅜⅝⅞]+)\s*(kg|g|gr|ml|cl|dl|l)\s*(?:chacun|par pi[èe]ce)",
        norm,
    )
    if m_each:
        count_val = parse_range_or_value(m_each.group(1))
        piece_val = parse_value_token(m_each.group(2))
        piece_unit = m_each.group(3)
        if count_val is not None and piece_val is not None:
            return ParsedQuantity(
                value=count_val,
                unit="pièce",
                raw=raw,
                per_piece_value=piece_val,
                per_piece_unit=piece_unit,
                notes=raw,
            )

    # 2. Pattern: Spoons (tablespoon, teaspoon) - check BEFORE metric so "15 % M.G." doesn't swallow spoon
    m_spoon = re.search(
        rf"({NUMBER_RE})\s*(?:c\.\s*à\s*soupe|cuill[èe]res?\s*à\s*soupe)",
        norm,
    )
    if m_spoon:
        val = parse_range_or_value(m_spoon.group(1))
        if val is not None:
            return ParsedQuantity(value=val, unit="c. à soupe", raw=raw, notes=norm)

    m_tsp = re.search(
        rf"({NUMBER_RE})\s*(?:c\.\s*à\s*caf[ée]|cuill[èe]res?\s*à\s*caf[ée])",
        norm,
    )
    if m_tsp:
        val = parse_range_or_value(m_tsp.group(1))
        if val is not None:
            return ParsedQuantity(value=val, unit="c. à café", raw=raw, notes=norm)

    # 3. Pattern: Mass or volume with optional "env." prefix, ensuring % is not preceding
    m_metric = re.search(
        rf"(?:env\.\s*|environ\s*)?({NUMBER_RE})\s*(kg|g|gr|ml|cl|dl|l)\b(?!%)",
        norm,
    )
    if m_metric:
        matched_str = m_metric.group(0)
        if "%" not in matched_str and "m.g" not in matched_str:
            val = parse_range_or_value(m_metric.group(1))
            if val is not None:
                unit = m_metric.group(2)
                if unit == "gr":
                    unit = "g"
                return ParsedQuantity(
                    value=val,
                    unit=unit,
                    raw=raw,
                    notes=norm,
                )

    # 4. Pattern: Pinches ("pincée", "pincées")
    m_pinch = re.search(
        rf"({NUMBER_RE})\s*pinc[ée]es?",
        norm,
    )
    if m_pinch:
        val = parse_range_or_value(m_pinch.group(1))
        if val is not None:
            return ParsedQuantity(value=val, unit="pincée", raw=raw, notes=norm)

    # 5. Pattern: Cloves ("gousse", "gousses")
    m_clove = re.search(
        rf"({NUMBER_RE})\s*gousses?",
        norm,
    )
    if m_clove:
        val = parse_range_or_value(m_clove.group(1))
        if val is not None:
            return ParsedQuantity(value=val, unit="gousse", raw=raw, notes=norm)

    # 6. Pattern: Tranches, portions, pots, boîtes, doses, bouquets, bottes
    m_container = re.search(
        rf"({NUMBER_RE})\s*(tranches?|portions?|pots?|bo[îi]tes?|doses?|bouquets?|bottes?)\b",
        norm,
    )
    if m_container:
        val = parse_range_or_value(m_container.group(1))
        if val is not None:
            u = m_container.group(2).rstrip("s")
            if u in ("boîte", "boite"):
                u = "boite"
            return ParsedQuantity(value=val, unit=u, raw=raw, notes=norm)

    # 7. Pattern: Branches, brins, feuilles
    m_branch = re.search(
        rf"({NUMBER_RE})\s*(?:branches?|brins?|feuilles?)\b",
        norm,
    )
    if m_branch:
        val = parse_range_or_value(m_branch.group(1))
        if val is not None:
            if "feuille" in norm:
                u = "feuille"
            elif "brin" in norm:
                u = "brin"
            else:
                u = "branche"
            return ParsedQuantity(value=val, unit=u, raw=raw, notes=norm)

    # 8. Pattern: Explicit "pièce" / "pièces"
    m_piece = re.search(
        rf"({NUMBER_RE})\s*(?:pi[èe]ces?|pcs?)\b",
        norm,
    )
    if m_piece:
        val = parse_range_or_value(m_piece.group(1))
        if val is not None:
            return ParsedQuantity(value=val, unit="pièce", raw=raw, notes=norm)

    # 9. Pattern: Number followed by adjective (petite, petit, gros, grosse, moyen, moyenne, blanc, etc.)
    m_adj = re.match(
        rf"^({NUMBER_RE})\s*(?:petite?s?|grosse?s?|moyenne?s?|blancs?|verts?|rouges?)(?:,\s*.*)?$",
        norm,
    )
    if m_adj:
        val = parse_range_or_value(m_adj.group(1))
        if val is not None:
            return ParsedQuantity(value=val, unit="pièce", raw=raw, notes=norm)

    # 10. Pattern: Bare number with optional descriptive trailing text
    m_bare = re.match(
        rf"^({NUMBER_RE})(?:,\s*.*)?$",
        norm,
    )
    if m_bare:
        val = parse_range_or_value(m_bare.group(1))
        if val is not None:
            return ParsedQuantity(value=val, unit="pièce", raw=raw, notes=norm)

    # Unrecognized
    return ParsedQuantity(
        value=None,
        unit="",
        raw=raw,
        notes=norm,
    )
