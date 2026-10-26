"""A small expression tree for what a student typed: parse it, print it back as LaTeX exactly as written, evaluate it.

Why not sympy for this? sympy rewrites as it parses (1/sqrt(13) becomes sqrt(13)/13, 5*5**(n+3) becomes 5**(n+4)), so the
working could not start from what the student wrote, and its LaTeX printer garbles unevaluated input. Here the tree keeps
the structure, the printer follows ordinary precedence, and to_sympy() evaluates it when a value is needed.

Nodes (tuples):  ("num", text)  ("sym", name)  ("neg", x)  ("group", x)  ("bin", op, a, b)  ("call", name, [args])
op is one of + - * / ^ and "imp" (implicit multiplication, written side by side as in 20(4^2x))."""
import re

import sympy as sp

import mathtext

_TOKEN = re.compile(r"\s*(?:(\d+(?:\.\d+)?)|([A-Za-z_][A-Za-z_0-9]*)|(\*\*|[-+*/(),]))")
_FUNCS = {"sqrt", "root", "cbrt"}


class ParseError(ValueError):
    pass


def _tokens(s):
    pos, out = 0, []
    s = s.strip()
    while pos < len(s):
        m = _TOKEN.match(s, pos)
        if not m:
            raise ParseError(f"unexpected text at {s[pos:pos + 10]!r}")
        pos = m.end()
        out.append(("num", m.group(1)) if m.group(1) else ("name", m.group(2)) if m.group(2) else ("op", m.group(3)))
    return out


class _Parser:
    def __init__(self, tokens):
        self.t, self.i = tokens, 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def take(self):
        tok = self.peek()
        self.i += 1
        return tok

    def expect(self, op):
        if self.take() != ("op", op):
            raise ParseError(f"expected {op!r}")

    def expr(self):
        node = self.term()
        while self.peek() in (("op", "+"), ("op", "-")):
            op = self.take()[1]
            node = ("bin", op, node, self.term())
        return node

    def term(self):
        if self.peek() == ("op", "-"):          # -1/3 is -(1/3), not (-1)/3: the minus belongs to the whole product or quotient
            self.take()
            return ("neg", self.term())
        node = self.unary()
        while True:
            kind, val = self.peek()
            if (kind, val) in (("op", "*"), ("op", "/")):
                self.take()
                node = ("bin", val, node, self.unary())
            elif kind in ("num", "name") or (kind, val) == ("op", "("):
                node = ("bin", "imp", node, self.unary())     # 20(4^2x), 4sqrt(3), 2n
            else:
                return node

    def unary(self):
        if self.peek() == ("op", "-"):
            self.take()
            return ("neg", self.unary())
        if self.peek() == ("op", "+"):
            self.take()
            return self.unary()
        return self.power()

    def power(self):
        base = self.atom()
        if self.peek() == ("op", "**"):
            self.take()
            return ("bin", "^", base, self.unary())          # right associative, exponent may be negative
        return base

    def atom(self):
        kind, val = self.take()
        if kind == "num":
            return ("num", val)
        if kind == "name":
            if val in _FUNCS and self.peek() == ("op", "("):
                self.take()
                args = [self.expr()]
                while self.peek() == ("op", ","):
                    self.take()
                    args.append(self.expr())
                self.expect(")")
                return ("call", val, args)
            if len(val) == 1 or val == "pi":
                return ("sym", val)
            raise ParseError(f"unknown name {val!r}")
        if (kind, val) == ("op", "("):
            node = self.expr()
            self.expect(")")
            return ("group", node)
        raise ParseError("unexpected end of the expression" if kind is None else f"unexpected {val!r}")


def parse(text):
    """Typed text or LaTeX -> tree. Raises ParseError (a ValueError) when the text is not a plain expression."""
    s = mathtext.to_py(text)
    if not s or len(s) > 300 or re.search(r"[^0-9A-Za-z_+\-*/().,\s]", s):
        raise ParseError("not a plain expression")
    p = _Parser(_tokens(s))
    node = p.expr()
    if p.i != len(p.t):
        raise ParseError("extra text after the expression")
    return node


# ------------------------------------------------------------------------------------------ evaluate

def to_sympy(node):
    k = node[0]
    if k == "num":
        return sp.Rational(node[1])
    if k == "sym":
        return sp.pi if node[1] == "pi" else sp.Symbol(node[1], positive=True)
    if k == "neg":
        return -to_sympy(node[1])
    if k == "group":
        return to_sympy(node[1])
    if k == "call":
        args = [to_sympy(a) for a in node[2]]
        return sp.sqrt(args[0]) if node[1] == "sqrt" else sp.cbrt(args[0]) if node[1] == "cbrt" else sp.root(args[0], args[1])
    op, a, b = node[1], to_sympy(node[2]), to_sympy(node[3])
    return {"+": a + b, "-": a - b, "*": a * b, "imp": a * b, "/": a / b, "^": a ** b}[op]


def strip(node):
    """Remove outer brackets."""
    while node[0] == "group":
        node = node[1]
    return node


# ------------------------------------------------------------------------------------------ print as LaTeX

_PREC = {"+": 1, "-": 1, "*": 2, "imp": 2, "/": 2, "^": 4}


def _is_atom(n):
    n = strip(n)
    return n[0] in ("num", "sym", "call")


def tex(node, parent=0, top=False):
    """LaTeX as written. `top` drops the brackets around the whole node (inside a fraction, root or exponent)."""
    k = node[0]
    if k == "num":
        return node[1]
    if k == "sym":
        return "\\pi" if node[1] == "pi" else node[1]
    if k == "group":
        inner = node[1]
        if top or _is_atom(inner):
            return tex(inner, parent, top)
        return r"\left(" + tex(inner, 0, True) + r"\right)"
    if k == "neg":
        inner = strip(node[1])
        if inner[0] == "bin" and inner[1] in ("+", "-"):      # -(a+b) needs its brackets; -(a/b) and -(x^2) do not
            return "-" + r"\left(" + tex(inner, 0, True) + r"\right)"
        return "-" + tex(inner, 3, True)
    if k == "call":
        if node[1] == "sqrt":
            return rf"\sqrt{{{tex(node[2][0], 0, True)}}}"
        if node[1] == "cbrt":
            return rf"\sqrt[3]{{{tex(node[2][0], 0, True)}}}"
        return rf"\sqrt[{tex(node[2][1], 0, True)}]{{{tex(node[2][0], 0, True)}}}"
    op, a, b = node[1], node[2], node[3]
    if op == "/":
        return rf"\frac{{{tex(a, 0, True)}}}{{{tex(b, 0, True)}}}"
    if op == "^":
        base = tex(a, 5)
        if not _is_atom(a) and strip(a)[0] != "call":
            base = base if a[0] == "group" else r"\left(" + base + r"\right)"
        return f"{base}^{{{tex(b, 0, True)}}}"
    prec = _PREC[op]
    left, right = tex(a, prec), tex(b, prec + (1 if op in "+-" else 0))
    if op == "imp":
        sep = "" if (a[0] == "num" and strip(b)[0] in ("sym", "call", "group")) or strip(a)[0] in ("sym",) else r"\,"
        out = f"{left}{sep}{right}"
    else:
        out = f"{left} {'\\times' if op == '*' else op} {right}"
    return rf"\left({out}\right)" if parent > prec and parent != 5 else out


def text_to_tex(text):
    """The student's own text as LaTeX, or the text itself if it cannot be read."""
    try:
        return tex(parse(text), 0, True)
    except ValueError:
        return str(text)


# ------------------------------------------------------------------------------------------ helpers for the solvers

def factors(node, sign=1):
    """A chain of products and quotients -> [(factor_node, +1 for multiply / -1 for divide), ...]. Brackets are opened.

    (3/4)^(-2) / (4/9)^3 * 16/27 is read left to right as a student would, so 16 is multiplied and 27 divided."""
    node = strip(node)
    if node[0] == "bin" and node[1] in ("*", "imp"):
        return factors(node[2], sign) + factors(node[3], sign)
    if node[0] == "bin" and node[1] == "/":
        return factors(node[2], sign) + factors(node[3], -sign)
    return [(node, sign)]


def terms(node, sign=1):
    """A sum -> [(term_node, +1/-1), ...]."""
    node = strip(node)
    if node[0] == "bin" and node[1] == "+":
        return terms(node[2], sign) + terms(node[3], sign)
    if node[0] == "bin" and node[1] == "-":
        return terms(node[2], sign) + terms(node[3], -sign)
    if node[0] == "neg":
        return terms(node[1], -sign)
    return [(node, sign)]


def top_split(text, sep):
    """Split typed text at a top-level separator ('=' , ',') ignoring brackets."""
    out, depth, cur = [], 0, ""
    for ch in text:
        depth += ch in "({["
        depth -= ch in ")}]"
        if ch == sep and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    return out + [cur]


def symbols(node, out=None):
    """Names of the unknowns written in the tree (not what is left after sympy has cancelled things)."""
    out = set() if out is None else out
    k = node[0]
    if k == "sym" and node[1] != "pi":
        out.add(node[1])
    elif k in ("neg", "group"):
        symbols(node[1], out)
    elif k == "call":
        for a in node[2]:
            symbols(a, out)
    elif k == "bin":
        symbols(node[2], out)
        symbols(node[3], out)
    return out
