"""
This module provides basic arithmetic operations including addition, 
subtraction, multiplication, and division.
"""


def add(a, b):
    """
    Adds two numbers and returns the sum.

    Args:
        a (float/int): The first number.
        b (float/int): The second number.

    Returns:
        float/int: The sum of a and b.
    """
    return a + b


def subtract(a, b):
    """
    Subtracts b from a and returns the result.

    Args:
        a (float/int): The number to subtract from.
        b (float/int): The value to subtract.

    Returns:
        float/int: The difference of a and b.
    """
    return a - b


def multiply(a, b):
    """
    Multiplies two numbers and returns the product.

    Args:
        a (float/int): The first factor.
        b (float/int): The second factor.

    Returns:
        float/int: The product of a and b.
    """
    return a * b


def divide(a, b):
    """
    Divides a by b.

    Args:
        a (float/int): The dividend.
        b (float/int): The divisor.

    Returns:
        float: The quotient.

    Raises:
        ValueError: If b is zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
