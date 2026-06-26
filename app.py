

def divide_indeterminate(a, b):
    if b == 0 and a == 0:
        return float('nan')
    elif b == 0:
        raise ValueError("Cannot divide by zero.")
