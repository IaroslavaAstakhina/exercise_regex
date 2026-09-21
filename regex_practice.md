# Extra regex practice (optional, not graded)

> Sits next to `02_regex_task_draft.md` for students who finish Task 1
> early or want more warm-up before/after the lab. Not part of the graded
> tasks — no need to submit this. Uses only `re.match`/`re.search`/
> `re.fullmatch`/`re.findall`/`re.sub`, same depth as the main exercise.
> Solutions are at the bottom — try each one yourself first.

---

## Set A: a list of names

```python
names = [
    "anna", "jana", "kamil", "norbert", "pavel",
    "petr", "stanislav", "zuzana", "hana", "ondrej",
]
```

1. Find the name `"kamil"` exactly.
2. Find all names containing the letter `"n"` at least once.
3. Find all names containing a double letter (e.g. `"nn"`, `"ll"` — any
   letter repeated twice in a row).
4. Find all names starting with `"p"`.
5. Find all names that are `"anna"` or `"hana"`.
6. Find all names starting with `"z"` and ending with `"a"`.
7. Find all names that are exactly 5 letters long.

---

## Set B: e-mail-like strings

```python
emails = [
    "alice@example.com", "bob.smith@company.org", "not-an-email",
    "carol123@school.edu", "dave@@broken.com", "eve@sub.domain.net",
    "frank@company", "grace_h@example.com",
]
```

1. Find all strings that contain an `@`.
2. Find all strings that look like `something@something.something`
   (at least one character, an `@`, at least one character, a `.`, at
   least one character — no need to validate real e-mail rules beyond
   that).
3. Find all strings whose domain (part after `@`) is `example.com`.
4. Replace every `@` with `" at "` (a common trick for displaying an
   e-mail address without it being auto-linked).
5. Find all strings where the part before `@` contains a digit.

---

## Set C: a mini shopping receipt

```python
receipt_lines = [
    "2x Coffee ......... 4.50",
    "1x Sandwich ........ 3.20",
    "3x Water Bottle .... 1.80",
    "SUBTOTAL ........... 9.50",
    "TAX ................ 0.95",
    "TOTAL .............. 10.45",
]
```

1. Find all lines that describe a purchased item (start with a quantity
   like `2x`, `1x`, `3x`).
2. Extract the quantity (as a string, e.g. `"2"`) from each item line.
3. Extract the price (the number at the end) from every line, item or not.
4. Find the `TOTAL` line specifically (not `SUBTOTAL`) — careful, `"TOTAL"`
   is a substring of `"SUBTOTAL"` too.
5. Replace every run of dots (`.......`) with a single space, on every
   line.

---

## Solutions

<details>
<summary>Set A</summary>

```python
import re

print([n for n in names if re.fullmatch(r"kamil", n)])
print([n for n in names if re.search(r"n", n)])
print([n for n in names if re.search(r"(.)\1", n)])
print([n for n in names if re.match(r"p", n)])
print([n for n in names if re.fullmatch(r"anna|hana", n)])
print([n for n in names if re.fullmatch(r"z.*a", n)])
print([n for n in names if re.fullmatch(r".{5}", n)])
```
</details>

<details>
<summary>Set B</summary>

```python
import re

print([e for e in emails if re.search(r"@", e)])
print([e for e in emails if re.fullmatch(r"[^@]+@[^@]+\.[^@]+", e)])
print([e for e in emails if re.search(r"@example\.com$", e)])
print([re.sub(r"@", " at ", e) for e in emails])
print([e for e in emails if re.search(r"\d", e.split("@")[0])])
```

Note: question 2 uses `[^@]+` (not `@`) rather than the tempting `.+`.
`.` matches *any* character including `@`, so `.+@.+\..+` would wrongly
accept `"dave@@broken.com"` (the greedy first `.+` just eats past the
extra `@`). `[^@]+` correctly refuses to cross a second `@`.
</details>

<details>
<summary>Set C</summary>

```python
import re

print([l for l in receipt_lines if re.match(r"\d+x", l)])
print([re.match(r"(\d+)x", l).group(1) for l in receipt_lines if re.match(r"\d+x", l)])
print([re.search(r"\d+\.\d+$", l).group() for l in receipt_lines])
print([l for l in receipt_lines if re.match(r"TOTAL", l)])
print([re.sub(r"\.+", " ", l) for l in receipt_lines])
```

Note: questions 2-3 above use `.group()`/`.group(1)` to pull the matched
text out of the match object — a small step beyond `re.findall` that's
handy to know, even though the main exercise doesn't require it.
</details>
