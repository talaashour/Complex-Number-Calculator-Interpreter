from complex_interpreter import evaluate

tests = [
    # (input, expected output)
    ("(5 - 2i) - (-2 + 3i)",       "(7 - 5i)"),
    ("(1 + 2i) + (3 + 4i)",        "(4 + 6i)"),
    ("(1 + 2i) * (3 - 1i)",        "(5 + 5i)"),
    ("(1 + 2i) / (3 - 1i)",        "(1/10 + 7/10i)"),
    ("((1 + 1i) + (2 + 2i)) * (0 + 1i)", "(-3 + 3i)"),
    ("(-2 + 3i)",                  "(-2 + 3i)"),
]

errors = [
    "-2i",                 # no real part, no parentheses
    "(5)",                 # missing imaginary part
    "(3 + i)",             # missing coefficient
    "(1 + 2i",             # missing closing parenthesis
    "(1 + 2i) + 7",        # bare number
    "(1 + 2i) (3 + 1i)",   # missing operator
    "(1 + 2i) # (1 + 1i)", # illegal character
    "(4 + 2i) / (0 + 0i)", # division by zero
]

for expr, expected in tests:
    got = evaluate(expr)
    print("PASS" if got == expected else "FAIL", expr, "=>", got)

print()
for expr in errors:
    print(expr, "=>", evaluate(expr))