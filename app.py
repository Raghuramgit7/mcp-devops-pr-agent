import math

def divide_indeterminate(a, b):
    """
    Divides a by b with explicit handling for indeterminate forms.

    Returns float('nan') when both operands are zero (0/0 is mathematically
    undefined, e.g. sin(0)/tan(0)). Raises ZeroDivisionError when only the
    denominator is zero (e.g. 1/0, which tends to infinity).

    Args:
        a (float/int): The dividend.
        b (float/int): The divisor.

    Returns:
        float: a / b, or float('nan') when both a and b are zero.

    Raises:
        ZeroDivisionError: If b is zero and a is non-zero.
    """
    if b == 0 and a == 0:
        return float('nan')
    elif b == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return a / b