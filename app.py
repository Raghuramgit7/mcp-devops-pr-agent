def add(a, b):
    """Adds two numbers and returns the sum."""
    return a + b


def subtract(a, b):
    """Subtracts b from a and returns the result."""
    return a - b


def multiply(a, b):
    """Multiplies two numbers and returns the product."""
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
