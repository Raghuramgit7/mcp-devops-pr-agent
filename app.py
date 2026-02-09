import os

def add(a, b):
    return a + b

def insecure_function(data):
    # SECURITY ISSUE: Potential command injection for Bandit to find
    os.system("echo " + data)
    return True

def power(a, b):
    # DOC ISSUE: No docstring for Doc-Checker to find
    return a ** b

if __name__ == "__main__"
    # SYNTAX ISSUE: Missing colon (:) for Fixer to find
    print("Bot Test")