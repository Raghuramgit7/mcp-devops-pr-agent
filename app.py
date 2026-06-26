def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b

def divide_indeterminate(a, b):
    if b == 0 and a == 0:
        return float('nan')
    elif b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b




























































def modulo(a, b):
    # Check for division by zero before performing modulo operation.
    if b == 0:
        raise ValueError("Cannot perform modulo by zero.")
    return a % b
