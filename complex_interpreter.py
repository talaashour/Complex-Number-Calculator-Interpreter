
import sys
from fractions import Fraction


class ParseError(Exception):
    pass

class Token:
    def __init__(self, kind, text, pos):
        self.kind, self.text, self.pos = kind, text, pos

    def __repr__(self):
        return f"Token({self.kind}, {self.text!r}, pos={self.pos})"


SINGLE = {'(': 'LPAREN', ')': 'RPAREN', '+': 'PLUS', '-': 'MINUS',
          '*': 'TIMES', '/': 'DIV',
          '\u2013': 'MINUS', '\u2212': 'MINUS'}      # en-dash / minus sign


class Scanner:
    def __init__(self, text):
        self.text, self.i = text, 0

    def next_token(self):
        t = self.text
        # skip any initial white space
        while self.i < len(t) and t[self.i] in ' \t\n\r':
            self.i += 1
        if self.i >= len(t):
            return Token('EOF', '$$', self.i)

        start, c = self.i, t[self.i]

        if c in SINGLE:                                # single-char tokens
            self.i += 1
            return Token(SINGLE[c], c, start)

        if c.isdigit():                                # read digits -> number
            while self.i < len(t) and t[self.i].isdigit():
                self.i += 1
            return Token('NUMBER', t[start:self.i], start)

        if c.isalpha():                                # read letters
            while self.i < len(t) and t[self.i].isalpha():
                self.i += 1
            word = t[start:self.i]
            if word == 'i':
                return Token('IMAG', word, start)
            raise ParseError(f"Lexical error at position {start}: "
                             f"unknown word '{word}' (only 'i' is allowed)")

        raise ParseError(f"Lexical error at position {start}: "
                         f"illegal character '{c}'")




NAMES = {'LPAREN': "'('", 'RPAREN': "')'", 'PLUS': "'+'", 'MINUS': "'-'",
         'TIMES': "'*'", 'DIV': "'/'", 'NUMBER': 'a number',
         'IMAG': "'i'", 'EOF': 'end of input'}


class Parser:
    def __init__(self, text):
        self.scanner = Scanner(text)
        self.tok = self.scanner.next_token()           # input_token

    def error(self, expected):
        found = NAMES[self.tok.kind]
        if self.tok.kind in ('NUMBER',):
            found += f" '{self.tok.text}'"
        raise ParseError(f"Syntax error at position {self.tok.pos}: "
                         f"expected {expected} but found {found}")

    def match(self, expected):
        if self.tok.kind == expected:
            tok = self.tok
            self.tok = self.scanner.next_token()
            return tok
        self.error(NAMES[expected])

    # program -> expr $$
    def program(self):
        value = self.expr()
        if self.tok.kind != 'EOF':
            self.error("an operator '+', '-', '*', '/' or end of input")
        return value

    # expr -> term expr_tail
    def expr(self):
        return self.expr_tail(self.term())

    # expr_tail -> add_op term expr_tail | epsilon
    def expr_tail(self, left):
        if self.tok.kind == 'PLUS':
            self.match('PLUS')
            return self.expr_tail(left + self.term())
        if self.tok.kind == 'MINUS':
            self.match('MINUS')
            return self.expr_tail(left - self.term())
        if self.tok.kind in ('RPAREN', 'EOF'):         # epsilon production
            return left
        self.error("an operator or ')'")

    # term -> factor term_tail
    def term(self):
        return self.term_tail(self.factor())

    # term_tail -> mult_op factor term_tail | epsilon
    def term_tail(self, left):
        if self.tok.kind == 'TIMES':
            self.match('TIMES')
            return self.term_tail(left * self.factor())
        if self.tok.kind == 'DIV':
            pos = self.tok.pos
            self.match('DIV')
            right = self.factor()
            if right == 0:
                raise ParseError(f"Runtime error at position {pos}: "
                                 f"division by zero")
            return self.term_tail(left / right)
        if self.tok.kind in ('PLUS', 'MINUS', 'RPAREN', 'EOF'):  # epsilon
            return left
        self.error("an operator or ')'")

    # factor -> '(' ( expr ')' | complex ')' )
    def factor(self):
        if self.tok.kind != 'LPAREN':
            if self.tok.kind == 'IMAG' or self.tok.kind == 'NUMBER':
                raise ParseError(
                    f"Syntax error at position {self.tok.pos}: a complex "
                    f"number must be written in parentheses as (a + bi)")
            self.error("'(' to start a complex number or sub-expression")
        self.match('LPAREN')
        if self.tok.kind == 'LPAREN':                  # grouped expression
            value = self.expr()
            self.match('RPAREN')
            return value
        if self.tok.kind in ('MINUS', 'NUMBER'):       # complex literal
            value = self.complex_body()
            self.match('RPAREN')
            return value
        self.error("a number or '(' after '('")

    # complex -> ['-'] NUMBER add_op NUMBER 'i'
    def complex_body(self):
        sign = 1
        if self.tok.kind == 'MINUS':
            self.match('MINUS')
            sign = -1
        real = sign * int(self.match('NUMBER').text)

        if self.tok.kind == 'IMAG':
            raise ParseError(
                f"Syntax error at position {self.tok.pos}: imaginary part "
                f"without a real part; write (a + bi), e.g. (0 + {real}i)")
        if self.tok.kind == 'PLUS':
            self.match('PLUS'); isign = 1
        elif self.tok.kind == 'MINUS':
            self.match('MINUS'); isign = -1
        else:
            self.error("'+' or '-' followed by the imaginary part "
                       "(both parts are required)")
        imag = isign * int(self.match('NUMBER').text)
        self.match('IMAG')
        return Complex(real, imag)


# ------------------------------------------------------------ COMPLEX TYPE#


class Complex:
    def __init__(self, re, im):
        self.re, self.im = Fraction(re), Fraction(im)

    def __add__(self, o): return Complex(self.re + o.re, self.im + o.im)
    def __sub__(self, o): return Complex(self.re - o.re, self.im - o.im)

    def __mul__(self, o):
        return Complex(self.re * o.re - self.im * o.im,
                       self.re * o.im + self.im * o.re)

    def __truediv__(self, o):
        d = o.re ** 2 + o.im ** 2
        return Complex((self.re * o.re + self.im * o.im) / d,
                       (self.im * o.re - self.re * o.im) / d)

    def __eq__(self, o):
        if isinstance(o, int):
            return self.re == o and self.im == 0
        return self.re == o.re and self.im == o.im

    def __str__(self):                                  # output as (a ± bi)
        sign = '-' if self.im < 0 else '+'
        return f"({self.re} {sign} {abs(self.im)}i)"


# ------------------------------------------------------------------- DRIVER#

def evaluate(line):
    try:
        return str(Parser(line).program())
    except ParseError as e:
        return str(e)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        print(evaluate(' '.join(sys.argv[1:])))
    else:
        print("Complex calculator. Example: (5 - 2i) - (-2 + 3i). Empty line quits.")
        while True:
            line = input('> ').strip()
            if not line:
                break
            print(evaluate(line))
