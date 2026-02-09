def add(a, b):
    """
    Adds two numbers together.

    Args:
        a (int or float): The first number.
        b (int or float): The second number.

    Returns:
        int or float: The sum of a and b.
    """
    return a + b

def subtract(a, b):
    """
    Subtracts the second number from the first.

    Args:
        a (int or float): The number to subtract from.
        b (int or float): The number to subtract.

    Returns:
        int or float: The difference between a and b.
    """
    return a - b

def multiply(a, b):
    """
    Multiplies two numbers together.

    Args:
        a (int or float): The first number.
        b (int or float): The second number.

    Returns:
        int or float: The product of a and b.
    """
    return a * b

def divide(a, b):
    """
    Divides the first number by the second.

    Args:
        a (int or float): The dividend.
        b (int or float): The divisor.

    Returns:
        int or float: The result of the division.

    Raises:
        ZeroDivisionError: If the divisor b is zero.
    """
    return a / b

if __name__ == "__main__":
    print("Simple Calculator App")

def power(a, b):
    """
    Calculates the power of a to b.

    Args:
        a (int or float): The base number.
        b (int or float): The exponent.

    Returns:
        int or float: The result of a raised to the power of b.
    """
    # This function intentionally has no docstring to test the AI agent
    return a ** b
