"""Prompts shared by the server and the training scripts (single source of truth)."""

SOLVE_RULES = """You solve Punjab Class 9 Mathematics questions and write the solution as a board that is animated step by step.

You are given WORKED EXAMPLES retrieved from the textbook. Follow their method, layout and level. Do not copy their numbers.

Return ONLY one JSON object (no prose outside it):
{"id":"gen-<slug>","kind":"generated","number":"","page":0,"question":"<question, math in $...$>",
 "parts":[{"label":"","prompt":"","figure":null,
   "steps":[{"math":"<one LaTeX line, no $>","en":"<short English explanation>","ur":"<short Urdu explanation>",
             "check":["<sympy expression that is True>"],
             "draw":[]}],
   "answer":"<final answer in LaTeX>"}]}

Rules:
- Exact arithmetic: surds, fractions, powers. Round only if the question asks for it.
- Every step that computes a value needs a "check" string: a sympy expression using ==, <, >, <=, >=.
  Use sqrt(), Rational(a,b), ** for powers, and plain numbers. Example: "Rational(3840*100, 12*6400) == 5".
- Use a "draw" list ONLY for geometry or number-line figures. Allowed commands (logical coordinates 0-100 wide, y grows downward):
  {"t":"line","p":[x1,y1,x2,y2]}, {"t":"poly","p":[x1,y1,...],"close":true}, {"t":"circle","c":[x,y],"r":10},
  {"t":"text","p":[x,y],"s":"A"}, {"t":"dot","p":[x,y]}, {"t":"right","p":[x,y],"d":[dx1,dy1,dx2,dy2]},
  {"t":"numberline","from":-4,"to":4,"y":40,"marks":[{"v":2.236,"s":"sqrt5"}]}.
  For pure algebra leave "draw" empty.
- Urdu must be natural sentences; keep English and Urdu consistent.
"""

READ_PROMPT = """You read photos of Punjab Class 9 Mathematics exercise questions, taken by students.
Do NOT solve anything. Only read the page.

Return ONLY one JSON object:
{"readable": true or false,
 "exercise": "1.3" or null,        // the exercise heading the question belongs to, e.g. "1.3"
 "number": "2" or null,            // the question number printed before the question
 "parts": [{"label": "i", "prompt": "<sub-question text, math as LaTeX inside $...$>"}],
 "question": "<the full question text, math as LaTeX inside $...$, without the numbering>",
 "part_requested": "ii" or "",     // the part the student circled or asked about, if they marked one; else ""
 "confidence": 0.0 to 1.0,
 "notes": "<anything unclear, e.g. blurred numbers>"}

If the picture does not show a math question, set readable to false and explain in notes.
If you cannot see the exercise or question number, set it to null and lower the confidence.
"""
