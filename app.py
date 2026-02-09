def add(a, b):   #testing my agent
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

if __name__ == "__main__":
    print("Simple Calculator App")

def power(a, b):
    # This function intentionally has no docstring to test the AI agent
    return a ** b
