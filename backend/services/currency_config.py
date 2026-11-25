"""
Centralized Currency Configuration for MediClaim AI (India Context)

All monetary conversions and currency displays in the application reference
this single configuration module. The underlying ML models and raw dataset
maintain their numerical representations internally to ensure statistical integrity.
"""

# Configurable Exchange Rate (1 USD to INR)
USD_TO_INR = 95.43

CURRENCY_CODE = "INR"
CURRENCY_SYMBOL = "₹"
CURRENCY_NAME = "Indian Rupee"

def convert_usd_to_inr(usd_val):
    """Converts a USD numerical value to INR."""
    if usd_val is None:
        return 0.0
    return float(usd_val) * USD_TO_INR

def format_inr(amount, include_symbol=True, decimals=2):
    """
    Formats a number using the Indian Numbering System (e.g. ₹12,66,396.18).
    Grouping rule: last 3 digits, then groups of 2 digits.
    """
    if amount is None:
        return "₹0" if include_symbol else "0"
    
    amount = float(amount)
    is_negative = amount < 0
    amount = abs(amount)

    if decimals > 0:
        parts = f"{amount:.{decimals}f}".split(".")
        integer_part = parts[0]
        decimal_part = "." + parts[1]
    else:
        integer_part = str(int(round(amount)))
        decimal_part = ""

    if len(integer_part) <= 3:
        formatted_int = integer_part
    else:
        last3 = integer_part[-3:]
        remaining = integer_part[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        formatted_int = ",".join(groups) + "," + last3

    sign = "-" if is_negative else ""
    symbol = f"{CURRENCY_SYMBOL}" if include_symbol else ""
    return f"{sign}{symbol}{formatted_int}{decimal_part}"

def format_compact_inr(amount, include_symbol=True):
    """
    Formats large currency amounts into executive-friendly Indian units:
    - Crores (Cr) for values >= 1,00,00,000 (10^7)
    - Lakhs (L) for values >= 1,00,000 (10^5)
    - Standard Indian formatted for smaller values
    """
    if amount is None:
        return "₹0" if include_symbol else "0"
    
    amount = float(amount)
    is_negative = amount < 0
    val = abs(amount)
    symbol = f"{CURRENCY_SYMBOL}" if include_symbol else ""
    sign = "-" if is_negative else ""

    if val >= 10000000:  # 1 Crore
        cr_val = val / 10000000.0
        return f"{sign}{symbol}{cr_val:.2f} Crore"
    elif val >= 100000:  # 1 Lakh
        lakh_val = val / 100000.0
        return f"{sign}{symbol}{lakh_val:.2f} Lakh"
    elif val >= 1000:
        return f"{sign}{format_inr(val, include_symbol=include_symbol, decimals=0)}"
    else:
        return f"{sign}{format_inr(val, include_symbol=include_symbol, decimals=2)}"

def format_usd_to_inr(usd_val, compact=False, decimals=2):
    """Converts a USD amount to INR and returns the formatted Indian currency string."""
    inr_val = convert_usd_to_inr(usd_val)
    if compact:
        return format_compact_inr(inr_val)
    return format_inr(inr_val, decimals=decimals)
