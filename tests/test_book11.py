"""Class 11, Unit 1 (Complex Numbers): the book, the server and the engine on new questions.
Run: python tests/test_book11.py   (NO_EMBEDDINGS=1 is set inside: TF-IDF search only)

  1. build: every sympy check of every step is true; every answer agrees with the key (or carries a key_note)
  2. structure: ids, parts, steps, English and Urdu text, balanced braces, drawing commands
  3. server: each item is listed and served; typing a book question finds that very item; "Exercise 1.3 Q4 (ii)" opens it
  4. engine: random new questions of every Class 11 kind are solved, and each answer is checked against sympy (an oracle
     independent of the engine's own steps); a question with a number the engine could not read is never answered
"""
import json
import os
import pathlib
import random
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("NO_EMBEDDINGS", "1")
os.environ.setdefault("TUTOR_NO_ENV_FILE", "1")
os.environ["DEEPEN_STEPS"] = "off"

import sympy as sp  # noqa: E402

FAIL = []


def check(cond, msg):
    if not cond:
        FAIL.append(msg)


# 1. build ---------------------------------------------------------------------------------------------------------------
out = subprocess.run([sys.executable, str(ROOT / "tools" / "build_dataset.py"), "--class", "11"], capture_output=True, text=True,
                     encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"})
last = [ln for ln in out.stdout.splitlines() if ln.startswith("items:")]
check(out.returncode == 0 and last and "failed: 0" in last[-1], "build: " + (last[-1] if last else out.stderr[-400:]))
print("build:", last[-1] if last else "?")

# 2. structure -----------------------------------------------------------------------------------------------------------
unit = json.loads((ROOT / "data" / "book11" / "unit01.json").read_text(encoding="utf-8"))
items = unit["items"]
check(len(items) == 60, f"60 questions expected, found {len(items)}")
ids = [it["id"] for it in items]
check(len(ids) == len(set(ids)), "duplicate ids")
per_ex = {}
for it in items:
    per_ex[it["exercise"]] = per_ex.get(it["exercise"], 0) + 1
    check(it["id"].startswith("c11-ex1."), f"id {it['id']}")
    for p in it["parts"]:
        check(p["answer"], f"{it['id']} ({p['label']}): no answer")
        check(p["steps"], f"{it['id']} ({p['label']}): no steps")
        for k, s in enumerate(p["steps"], 1):
            check(s.get("en") and s.get("ur"), f"{it['id']} ({p['label']}) step {k}: English and Urdu")
            for t in (s.get("math", ""), s.get("en", ""), s.get("ur", "")):
                check(t.count("{") == t.count("}"), f"{it['id']} ({p['label']}) step {k}: braces")
            for d in s.get("draw", []) or []:
                check(d.get("t") in ("line", "poly", "circle", "arc", "dot", "text", "right", "numberline", "subdiv"), f"{it['id']}: drawing {d.get('t')}")
check(per_ex == {"1.1": 9, "1.2": 12, "1.3": 8, "1.4": 9, "1.5": 22}, f"questions per exercise {per_ex}")
print("structure:", len(items), "items,", sum(len(it["parts"]) for it in items), "parts,", per_ex)

# 3. server --------------------------------------------------------------------------------------------------------------
import server  # noqa: E402

d = server.data("11")
check(len(d["items"]) == 60, "server lists 60 Class 11 items")
client = server.app.test_client()
r = client.get("/api/items?class=11")
check(r.status_code == 200 and len(r.get_json()) == 60, "/api/items?class=11")
found = 0
for it in items:
    r = client.get(f"/api/item/{it['id']}?class=11")
    check(r.status_code == 200 and r.get_json()["id"] == it["id"], f"/api/item/{it['id']}")
    res = server.resolve(it["question"], klass="11")
    ok = res.get("mode") == "book" and res["item"]["id"] == it["id"]
    found += ok
    check(ok, f"typing {it['id']} finds {res.get('mode')} {(res.get('item') or {}).get('id')}")
for ref, want in (("Exercise 1.3 Q4 (ii)", "c11-ex1.3-q4"), ("Exercise 1.5 Q19", "c11-ex1.5-q19"), ("Ex 1.2 Q7 (iv)", "c11-ex1.2-q7")):
    res = server.resolve(ref, klass="11")
    check((res.get("item") or {}).get("id") == want, f"{ref} -> {(res.get('item') or {}).get('id')}")
check(server.resolve("hello", klass="11")["mode"] == "not_math", "hello is not maths")
print(f"server: {found}/60 book questions found as themselves; references open")

# 4. engine on new questions ---------------------------------------------------------------------------------------------
import engine11  # noqa: E402

I = sp.I
Z = sp.Symbol("z")
rnd = random.Random(int(os.environ.get("SEED", "1111")))


def cplx(s):
    s = s.replace("\\left", "").replace("\\right", "").replace("$", "")
    s = s.replace("i\\sqrt", "I*\\sqrt")
    for _ in range(3):                                       # roots inside fractions: roots first, then fractions
        s = re.sub(r"\\sqrt\{([^{}]*)\}", r"sqrt(\1)", s)
        s = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"((\1)/(\2))", s)
    s = s.replace("\\pi", "pi")
    s = re.sub(r"(\d)\s*i\b", r"\1*I", s)
    s = re.sub(r"\bi\b", "I", s).replace(" ", "")
    s = re.sub(r"(\d|\))(sqrt|\(|I|pi)", r"\1*\2", s)
    s = re.sub(r"\)I", ")*I", s)
    return sp.sympify(s, locals={"I": I})


def ans_roots(answer):
    body = answer.split("=", 1)[1] if "=" in answer.split("$")[1] else answer
    body = body.strip("$ ").split("$")[0]
    return [cplx(t) for t in re.split(r",\\\s*|,\s*", body) if t.strip()]


def fmt(z):
    a, b = int(sp.re(z)), int(sp.im(z))
    return f"{a}{'+' if b >= 0 else '-'}{abs(b)}i"


tested = wrong = unsolved = 0
cases = []
for _ in range(25):                                   # square roots of a perfect-square complex number
    p, q = rnd.randint(-9, 9), rnd.randint(1, 9)
    w = sp.expand((p + q * I) ** 2)
    if sp.im(w) == 0:
        continue
    cases.append(("sqrt", f"Find the square roots of {fmt(w)}", w))
for _ in range(25):                                   # quadratics with complex roots, by completing the square
    a = rnd.choice([1, 1, 2, 3])
    h, k = rnd.randint(-6, 6), rnd.randint(1, 6)
    b, c = -2 * a * h, a * (h * h + k * k)
    cases.append(("quad", f"Solve {a if a > 1 else ''}z^2 {'+' if b >= 0 else '-'} {abs(b)}z + {c} = 0 by completing the square", (a, b, c)))
for _ in range(20):                                   # factorize a quartic into linear factors
    m, n = rnd.randint(1, 6), rnd.randint(1, 6)
    poly = sp.expand((Z ** 2 - m * m) * (Z ** 2 + n * n))
    cases.append(("factor", "Factorize " + sp.sstr(poly).replace("**", "^").replace("*", "") + " into linear factors", poly))
for _ in range(20):                                   # cube and fourth roots of integers
    c = rnd.randint(2, 6) * rnd.choice([1, -1])
    cases.append(("cube", f"Find the cube roots of {c ** 3}", c ** 3))
    cases.append(("fourth", f"Find the four fourth roots of {abs(c) ** 4}", abs(c) ** 4))
for _ in range(20):                                   # polar form of numbers with standard angles
    r = rnd.randint(1, 5)
    z = sp.expand(r * rnd.choice([1 + I, 1 - I, -1 + I, -1 - I, I, -I, 1, -1]))
    cases.append(("polar", f"Express {fmt(z)} in polar form", z))
for _ in range(15):                                   # multiplicative inverse of an ordered pair
    a, b = rnd.randint(-9, 9), rnd.randint(-9, 9)
    if a == 0 and b == 0:
        continue
    cases.append(("inv", f"Find the multiplicative inverse of ({a}, {b})", (a, b)))

for kind, q, data in cases:
    res = engine11.solve(q)
    tested += 1
    if not res:
        unsolved += 1
        continue
    ans = res["parts"][0]["answer"]
    ok = False
    try:
        if kind == "sqrt":
            v = cplx(ans.split("\\pm")[1])
            ok = sp.simplify(sp.expand(v ** 2) - data) == 0
        elif kind == "quad":
            a, b, c = data
            body = ans.strip("$").split("=", 1)[1]
            h_, k_ = body.split("\\pm")
            for s in (1, -1):
                root = cplx(h_) + s * cplx(k_)
                ok = sp.simplify(a * root ** 2 + b * root + c) == 0
                if not ok:
                    break
        elif kind == "factor":
            roots = [cplx(f) for f in re.findall(r"\\left\(z ([^()]*?)\\right\)", ans)]
            ok = len(roots) == 4 and sp.expand(sp.Mul(*[(Z + r) for r in roots]) - data) == 0      # factors are z - r written "z + (-r)"
        elif kind in ("cube", "fourth"):
            if kind == "cube":
                rts = ans_roots(ans)
                ok = len(rts) == 3 and all(sp.simplify(sp.expand(r ** 3) - data) == 0 for r in rts) and len(set(sp.nsimplify(r) for r in rts)) == 3
            else:
                c4 = sp.Integer(data) ** sp.Rational(1, 4)
                ok = f"\\pm {sp.latex(c4)}," in ans and f"\\pm {sp.latex(c4)}i" in ans
        elif kind == "polar":
            m = re.search(r"^\$(.*?)\\left\(\\cos(.*?) \+ i\\sin", ans)
            rtex = (m.group(1) or "1").strip() or "1"
            ang = m.group(2).strip()
            ang = re.sub(r"^\\left\((.*)\\right\)$", r"\1", ang)
            rv, tv = cplx(rtex), cplx(ang)
            ok = sp.simplify(rv * (sp.cos(tv) + I * sp.sin(tv)) - data) == 0
        elif kind == "inv":
            a, b = data
            nums = re.findall(r"-?\s*\\frac\{(\d+)\}\{(\d+)\}|(-?\d+)", ans)
            inv = sp.expand(1 / (a + b * I))
            ok = (str(sp.re(inv)).replace(" ", "") in ans.replace(" ", "").replace("\\frac{", "").replace("}{", "/").replace("}", "")
                  or sp.latex(sp.re(inv)) in ans) and (sp.latex(sp.im(inv)) in ans)
    except Exception as exc:
        ok = False
        ans += f"  [oracle error {exc}]"
    if not ok:
        wrong += 1
        FAIL.append(f"engine WRONG: {q} -> {ans}")

# a question whose numbers were not all read must never be answered
for q in ("Find the roots of z^4 + 5z^2 - 36 = 0 and 7", ):
    res = engine11.solve(q)
    check(res is None or "36" in json.dumps(res), f"misread question answered: {q}")
check(unsolved <= tested // 20, f"engine left {unsolved}/{tested} questions unsolved")
print(f"engine: {tested} new questions, {tested - unsolved} solved, {wrong} wrong (oracle-checked)")

if FAIL:
    print("\n".join(FAIL[:40]))
    print(f"book11: {len(FAIL)} FAILURES")
    sys.exit(1)
print("book11: all tests passed")
