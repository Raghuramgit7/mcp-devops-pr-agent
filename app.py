"""
This module provides a specialized division function that handles indeterminate forms.
"""

def divide_indeterminate(a, b):
    """
    Divides 'a' by 'b' with explicit handling for indeterminate forms (0/0)
    and division by zero.

    Returns NaN when both 'a' and 'b' are zero (0/0, an indeterminate form).
    Raises ValueError when only 'b' is zero and 'a' is non-zero (division by zero).
    Otherwise, performs standard division.

    Args:
        a (float/int): The dividend.
        b (float/int): The divisor.

    Returns:
        float: The quotient of a and b, or float('nan') if a and b are both zero.

    Raises:
        ValueError: If 'b' is zero and 'a' is non-zero.
    """
    if b == 0 and a == 0:
        return float('nan')
    elif b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b
