import math

import pytest
from app import add, subtract, multiply, divide, divide_indeterminate


def test_add():
    assert add(1, 2) == 3
    assert add(-1, 1) == 0


def test_subtract():
    assert subtract(2, 1) == 1
    assert subtract(1, 1) == 0


def test_multiply():
    assert multiply(2, 3) == 6
    assert multiply(-1, 2) == -2


def test_divide():
    assert divide(6, 3) == 2
    with pytest.raises(ValueError):
        divide(1, 0)


def test_divide_indeterminate():
    # 0/0 is mathematically undefined (e.g. sin(0)/tan(0)) -> expect NaN
    result = divide_indeterminate(0, 0)
    assert math.isnan(result)

    # Non-zero numerator over zero is not indeterminate, it tends to infinity.
    # We surface that as a ZeroDivisionError rather than returning NaN.
    with pytest.raises(ZeroDivisionError):
        divide_indeterminate(1, 0)

    # Sanity check: regular division still works.
    assert divide_indeterminate(6, 3) == 2
