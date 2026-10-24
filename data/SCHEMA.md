# Solution dataset format

One JSON file per unit in `data/book/unitNN.json`:

```json
{
  "unit": 1,
  "title": "Real Numbers",
  "title_ur": "حقیقی اعداد",
  "items": [ <item>, ... ]
}
```

Each **item** is one book question (an exercise question or a solved example):

| field | meaning |
|---|---|
| `id` | unique id, e.g. `ex1.3-q2`, `u1-example14`, `rev1-q7` |
| `kind` | `exercise`, `example` or `review` |
| `exercise` | exercise label, e.g. `"1.3"` or `"Review 1"` (examples: omitted) |
| `number` | question / example number as a string |
| `page` | printed book page number (PDF page = page + 2) |
| `question` | question text; math inside `$...$` (KaTeX) |
| `parts` | list of parts (a question with no sub-parts has one part with `label: ""`) |

Each **part**:

| field | meaning |
|---|---|
| `label` | `"i"`, `"ii"`, ... or `""` |
| `prompt` | the sub-question text (optional) |
| `figure` | optional drawing (see below) shown before the steps |
| `steps` | ordered list of steps |
| `answer` | final answer (KaTeX) |

Each **step**:

| field | meaning |
|---|---|
| `math` | the line written on the board (KaTeX, no `$`) |
| `en` | English explanation shown on the right |
| `ur` | Urdu explanation |
| `draw` | optional list of drawing commands animated on the board |
| `check` | optional list of sympy strings that must be True, e.g. `"Eq(Rational(3840*100, 12*6400), 5)"` |

## Drawing commands (`figure` / `draw`)

Coordinates are in a logical box of width 100 and height given by `h` on the
figure (default 60). y grows downward.

- `{"t":"line","p":[x1,y1,x2,y2],"dash":false,"arrow":false}`
- `{"t":"poly","p":[x1,y1,x2,y2,...],"close":true}`
- `{"t":"circle","c":[x,y],"r":10}` / `{"t":"arc","c":[x,y],"r":10,"a":[startDeg,endDeg]}`
- `{"t":"text","p":[x,y],"s":"A"}`
- `{"t":"dot","p":[x,y]}`
- `{"t":"right","p":[x,y],"d":[dx1,dy1,dx2,dy2]}` — right-angle mark at a vertex
- `{"t":"numberline","from":-4,"to":4,"y":40,"marks":[{"v":2.236,"s":"√5"}]}`
- `{"t":"axes","x":[-5,5],"y":[-5,5]}` then `{"t":"plot","f":"2*x+1"}` / `{"t":"pt","xy":[1,3],"s":"(1,3)"}`
