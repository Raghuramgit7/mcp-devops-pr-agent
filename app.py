"""
This module provides basic arithmetic operations including addition, 
subtraction, multiplication, division, and modulo.
It also includes a specialized division function to handle indeterminate forms.
"""

def add(a, b):
    """
    Adds two numbers and returns their sum.

    Args:
        a (int | float): The first number.
        b (int | float): The second number.

    Returns:
        int | float: The sum of `a` and `b`.
    """
    return a + b

def subtract(a, b):
    """
    Subtracts the second number from the first.

    Args:
        a (int | float): The number to subtract from (minuend).
        b (int | float): The number to subtract (subtrahend).

    Returns:
        int | float: The difference of `a` and `b`.
    """
    return a - b

def multiply(a, b):
    """
    Multiplies two numbers and returns their product.

    Args:
        a (int | float): The first factor.
        b (int | float): The second factor.

    Returns:
        int | float: The product of `a` and `b`.
    """
    return a * b

def divide(a, b):
    """
    Divides the first number by the second.

    Args:
        a (int | float): The dividend.
        b (int | float): The divisor.

    Returns:
        float: The quotient of `a` divided by `b`.

    Raises:
        ValueError: If the divisor `b` is zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b

def divide_indeterminate(a, b):
    """
    Divides `a` by `b`, handling indeterminate forms (0/0).

    If both `a` and `b` are zero, returns `float('nan')` (Not a Number).
    If only `b` is zero (and `a` is not zero), raises a `ValueError`.

    Args:
        a (int | float): The dividend.
        b (int | float): The divisor.

    Returns:
        float: The quotient of `a` divided by `b`, or `float('nan')` if `a` and `b` are both zero.

    Raises:
        ValueError: If the divisor `b` is zero and the dividend `a` is non-zero.
    """
    if b == 0 and a == 0:
        return float('nan')
    elif b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b

def modulo(a, b):
    """
    Computes the remainder of the division of `a` by `b`.

    Args:
        a (int | float): The dividend.
        b (int | float): The divisor.

    Returns:
        int | float: The remainder of `a` divided by `b`.

    Raises:
        ValueError: If the divisor `b` is zero.
    """
    # Check for division by zero before performing modulo operation.
    if b == 0:
        raise ValueError("Cannot perform modulo by zero.")
    return a % b
