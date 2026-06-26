import math

def divide_indeterminate(a, b):
    if b == 0 and a == 0:
        return float('nan')
    elif b == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return a / b
