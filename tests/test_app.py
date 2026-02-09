import pytest
from app import add, subtract, multiply, divide # Assuming these functions are in app.py

def test_add():
    assert add(1, 2) == 3

def test_subtract():
    assert subtract(5, 2) == 3

def test_multiply():
    assert multiply(2, 3) == 6

def test_divide():
    assert divide(6, 3) == 2
    with pytest.raises(ZeroDivisionError): # Changed from ValueError
        divide(1, 0)
