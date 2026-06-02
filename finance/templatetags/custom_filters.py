from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def fcfa(value):
    try:
        value = float(value)
    except:
        return value
    
    # Format avec séparateur de milliers espace
    formatted = f"{value:,.0f}".replace(",", " ")

    return formatted 


@register.filter
def format_number(value):
    """
    - 8825.00 -> 8 825
    - 8825.50 -> 8 825,5
    - 8825.75 -> 8 825,75
    """
    if value is None:
        return ""

    try:
        val = Decimal(value).normalize()

        # Séparer partie entière / décimale
        int_part = int(val)
        decimal_part = abs(val - int_part)

        # Format milliers avec espace
        int_str = f"{int_part:,}".replace(",", " ")

        if decimal_part == 0:
            return int_str

        # Supprimer les zéros inutiles
        decimal_str = str(decimal_part).lstrip("0").rstrip("0").rstrip(".")
        decimal_str = decimal_str.replace(".", ",")

        return f"{int_str}{decimal_str}"

    except Exception:
        return value
