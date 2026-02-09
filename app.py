import os

def add(a, b):
    """
    Adds two numbers and returns the sum.
    """
    return a + b

def insecure_function(data):
    """
    Executes a shell command to echo the provided data.
    Warning: This function is vulnerable to command injection and is intended for security testing.
    """
    # SECURITY ISSUE: Potential command injection for Bandit to find
    os.system("echo " + data)
    return True

def power(a, b):
    """
    Calculates the result of raising the base (a) to the power of the exponent (b).
    """
    # DOC ISSUE: No docstring for Doc-Checker to find
    return a ** b

if __name__ == "__main__":
    # SYNTAX ISSUE: Missing colon (:) for Fixer to find
    print("Bot Test")