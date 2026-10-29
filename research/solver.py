"""Owner-reviewed baseline solver; the RSI model may propose replacements for review."""
from math import gcd, isqrt


def solve(task: dict):
    operation = task['operation']
    if operation == 'gcd':
        return gcd(task['a'], task['b'])
    if operation == 'mod_pow':
        return pow(task['a'], task['b'], task['mod'])
    if operation == 'is_prime':
        n = task['n']
        if n < 2:
            return False
        for divisor in range(2, isqrt(n) + 1):
            if n % divisor == 0:
                return False
        return True
    raise ValueError('Unsupported mathematical operation')