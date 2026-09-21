# Regular Expressions in Python

## Why regular expressions?

A regular expression (**regex**) is a pattern that describes a *set* of
strings — instead of writing out every string you want to match, you
describe its shape once (e.g. "a digit, then three letters, then a dash").
Any time you need to search text for something that follows a pattern,
validate a format (an e-mail address, a phone number, an ID), pull
structured pieces out of unstructured text (log files, web pages, file
names, spreadsheet cells), or replace many variations of a substring at
once, a regex typically replaces dozens of lines of manual string-slicing
and `if`/`elif` chains with a single, compact, reusable pattern. Regex
syntax is nearly identical across programming languages (Python, R, Java,
JavaScript, the command line, ...) — once you know it, you can use it
almost anywhere. That makes it one of the most transferable, general-
purpose skills in a programmer's toolkit — it has nothing to do with any
one domain. Bioinformatics happens to be a very text-heavy field (DNA/RNA
sequences, FASTA/FASTQ headers, annotation files are all just text with
structure), so regex comes up constantly there too — but the skill itself
is general, which is why we start with plain, everyday text below.

This exercise has two parts. First, you'll use Python's `re` module to
search and extract patterns in plain, everyday text — regexes work exactly
the same way no matter what the text represents, so this is a general
text-searching tool you'll reach for far beyond bioinformatics (log files,
scraped data, config files, ...). Then you'll apply the same tools to a
real bioinformatics problem: demultiplexing an amplicon sequencing run,
i.e. sorting a mixed pile of DNA reads back into the samples they came
from, based on short barcode tags (MIDs) attached to each read.

Structure of the session:
1. **`re` module basics** (theory) → **Task 1** (generic text, no biology
   yet, no classes yet)
2. **MIDs and demultiplexing** (background) + **building regex logic into
   a class** (theory) → **Task 2**
3. **Task 3** — a longer task you work through independently,
   combining everything from Tasks 1 and 2.

Write your own code from scratch in a single file, `regex_exercise.py`.
Commit and push your work to your GitHub repository as
you go (e.g. one commit per finished part).

---

## `re` module basics

### Metacharacters cheat-sheet

| Symbol | Meaning | Example → matches |
|---|---|---|
| `.` | any single character (except newline) | `a.c` → `abc`, `axc` |
| `^` | start of the string | `^ab` → `abc`, not `xab` |
| `$` | end of the string | `bc$` → `abc`, not `bcx` |
| `*` | zero or more repetitions | `ab*` → `a`, `ab`, `abbb` |
| `+` | one or more repetitions | `ab+` → `ab`, `abbb`, not `a` |
| `?` | zero or one repetition | `ab?c` → `ac`, `abc` |
| `{n}` / `{m,n}` / `{m,}` | exactly `n` / between `m` and `n` / `m` or more repetitions | `a{2,3}` → `aa`, `aaa` |
| `[...]` | one character from a set/range | `[abc]`, `[0-9]`, `[a-zA-Z]` |
| `[^...]` | one character **not** in the set | `[^0-9]` → any non-digit |
| `\d` `\D` | digit / non-digit | `\d+` → `123` |
| `\w` `\W` | word character (`[a-zA-Z0-9_]`) / non-word | `\w+` → `hello_1` |
| `\s` `\S` | whitespace / non-whitespace | `\s+` → spaces, tabs |
| `(...)` | group (for `|`, or to apply a quantifier to a sequence) | `(ab)+` → `ab`, `abab` |
| `\|` | alternation ("or") | `cat\|dog` → `cat`, `dog` |
| `\` | escape a metacharacter to match it literally | `\.` → a literal `.` |

### `re` functions

| Function | Behaviour | Example |
|---|---|---|
| `re.match(pattern, s)` | matches only at the **start** of `s` | `re.match(r"ab", "abcdef")` → matches `"ab"`; `re.match(r"ab", "xabc")` → `None` |
| `re.fullmatch(pattern, s)` | matches the **entire** string | `re.fullmatch(r"ab+", "abb")` → matches `"abb"`; `re.fullmatch(r"ab+", "abbx")` → `None` |
| `re.search(pattern, s)` | matches **anywhere** in `s` | `re.search(r"cd", "abcdef")` → matches `"cd"` |
| `re.findall(pattern, s)` | returns **all** non-overlapping matches | `re.findall(r"\d+", "a1 b22 c333")` → `["1", "22", "333"]` |
| `re.sub(pattern, repl, s)` | replaces matches with `repl` | `re.sub(r"\d+", "#", "a1 b22 c333")` → `"a# b# c#"` |

What each one actually returns:

- **`match`, `fullmatch`, `search`** — a `Match` object if the pattern
  matched, or `None` if it didn't. A `Match` object is truthy, but it is
  **not** the matched text — always check with `if re.search(...):`,
  and call `.group()` on the result to get the matched substring back as
  a plain string, e.g. `re.search(r"cd", "abcdef").group()` → `"cd"`.
  Calling `.group()` on `None` crashes, so only do it after confirming
  the match succeeded.
- **`findall`** — a plain `list` of strings, one per match, in the order
  they were found (`[]` if there were no matches — no `None` case here).
  No `.group()` needed; the strings are already extracted for you.
- **`sub`** — a plain `str`: the input string with every match replaced.
  If nothing matched, you get the original string back unchanged (never
  `None`).

---

## Task 1: warm-up

To show that regex has nothing to do with DNA specifically, this task
works on a small server log — the same functions apply to any text you'd
want to search through.

```python
log_lines = [
    "2024-01-15 10:02:11 INFO Server started on port 8080",
    "2024-01-15 10:03:47 ERROR Failed to connect to database",
    "2024-01-16 08:15:00 WARNING Disk usage at 85%",
    "2024-01-16 14:22:39 ERROR Timeout while fetching https://example.com/api",
    "2024-01-17 09:00:05 INFO User admin logged in from 192.168.1.10",
    "2024-01-17 11:41:18 DEBUG Cache cleared successfully",
    "2024-01-18 03:12:56 ERROR Connection refused from 192.168.1.55",
    "2024-01-18 23:59:02 INFO Backup completed in 42s",
]
```

Write regex-based expressions (using `re.match`/`re.search`/`re.fullmatch`/
`re.findall`, your choice per case) that:

1. Find all lines logged on `2024-01-16`.
2. Find all lines that are an `ERROR` or a `WARNING`.
3. Find all IPv4 addresses (four groups of 1-3 digits separated by dots)
   that appear anywhere in the log — only 2 of the 8 lines contain one.
4. Find all lines ending in a number of seconds, e.g. `...in 42s`.
5. Find all lines that mention a URL (starts with `http://` or `https://`).
6. **(Optional)** Check whether a single line, e.g. `log_lines[0]`, matches
   the full expected format `YYYY-MM-DD HH:MM:SS LEVEL message` from start
   to end.

Print each result. Plain functions/expressions are fine.

---

## MIDs and demultiplexing

From here on, we leave generic text behind and apply the same regex tools
to a real bioinformatics problem.

To sequence several samples in one run, each sample's reads are tagged with
a short **MID** (Multiplex IDentifier) barcode, attached before (forward
MID) and after (reverse MID) the actual sequence of interest. A full read
looks like:

```
forward_MID + <sequence of interest> + reverse_complement(reverse_MID)
```

DNA is double-stranded, and the two strands are complementary and
antiparallel — each strand runs 5' → 3' in the *opposite* direction to
the other. A MID pair is attached to the two ends of the double-stranded
fragment. Using the same `forward_mid`/`reverse_mid` as in the code below,
the two strands, base-paired, look like this:

```
5' – AGCTTCGA ... GACCTGCA – 3'
3' – TCGAAGCT ... CTGGACGT – 5'
```

The top strand carries `forward_mid` at its 5' end and
`reverse_complement(reverse_mid)` at its 3' end; the bottom strand is just
its base-for-base complement (that's what makes it double-stranded).

The sequencer only ever reads **one strand at a time**, always 5' → 3'.
Reading the *top* strand 5'→3' gives you `forward_mid ...
revcomp(reverse_mid)` (left to right, as drawn above). But the *bottom*
strand's own 5' end is on the **right** — reading it 5'→3' means going
right to left, which gives `reverse_mid ... revcomp(forward_mid)`. Since
the sequencer picks whichever strand happens to load, with no control
over which one, the exact same physical DNA fragment shows up in the
output FASTA file as **one of two different strings**:

```python
forward_mid = "AGCTTCGA"
reverse_mid = "TGCAGGTC"
insert      = "CGTTAGGCAT"   # the actual sequence of interest

# sense strand was sequenced (starts with the forward MID):
"AGCTTCGACGTTAGGCATGACCTGCA"   # forward_mid + insert + reverse_complement(reverse_mid)

# antisense strand was sequenced (starts with the reverse MID):
"TGCAGGTCCGTTAGGCATTCGAAGCT"   # reverse_mid + insert + reverse_complement(forward_mid)
```

Both strings represent the **same** sample and the same underlying insert
— only the second half of each read differs, and it's always the reverse
complement of the *other* MID (not of the one it starts with). Both
orientations must be checked; a read is not "wrong" just because it came
out the other way round.

---

## Task 2: `SequencingRead` class

Implement a class `SequencingRead` wrapping one sequencing read.

**Constructor** `__init__(self, read_id, sequence)`: store both as instance
attributes.

**Methods:**
- `matches_mid_pair(self, forward_mid, reverse_mid)` → `bool`: `True` if
  `self.sequence` starts with `forward_mid` **and** ends with the
  reverse complement of `reverse_mid` — built and checked as a single
  regex (anchors `^`/`$`, not two separate `.startswith()`/`.endswith()`
  calls).
- `trim_mid_pair(self, forward_mid, reverse_mid)` → `str | None`: if
  `matches_mid_pair(...)` is `True`, return the sequence with both MIDs
  removed (just the insert in between); otherwise return `None`.
- `describe(self)` → `str`: e.g. `"SequencingRead demo_1 (46 bp)"`.

You'll need a small helper function `reverse_complement(sequence)` (not a
method — it doesn't belong to any one read). A|T and C|G are
complementary bases; reverse complement = complement each base, then
reverse the string.

Demo:
```python
r1 = SequencingRead("demo_1", "AGCTTCGA" + "N" * 20 + reverse_complement("TGCAGGTC"))
print(r1.describe())
print(r1.matches_mid_pair("AGCTTCGA", "TGCAGGTC"))  # True
print(r1.matches_mid_pair("CGATCGAT", "GCTAGCTA"))  # False
print(r1.trim_mid_pair("AGCTTCGA", "TGCAGGTC"))     # 20 x "N"
```

---

## Task 3: `Demultiplexer` class and a full report

This is the main task — work through it independently, combining
everything from Tasks 1 and 2.

You'll be running this on a **real** amplicon sequencing run from a 454
Junior machine (`fishes.fna.gz`, ~104,600 reads, gzip-compressed) with its
matching MID table (`fishes_MIDs.csv`). Add [Biopython](https://biopython.org/) to your project
(`uv add biopython`) to parse the FASTA; regex is still what does the
actual demultiplexing work.

> **Note:** in this real MID table, each sample's forward and reverse MID
> happen to be the *same* sequence (unlike the Task 2 demo, which
> deliberately used two different ones). Your `assign_reads` should still
> check both orientations in general — it just means that, for this
> particular file, the second orientation check won't find anything the
> first one didn't already catch.

Implement a class `Demultiplexer`.

**Constructor** `__init__(self, fasta_path, mid_table_path)`:
- Parses the gzipped FASTA file at `fasta_path` into a list of
  `SequencingRead` objects using Biopython: open it with
  `gzip.open(fasta_path, "rt")` and iterate over
  `Bio.SeqIO.parse(handle, "fasta")`; each `record` gives you `record.id`
  and `str(record.seq)`.
- Parses the MID table at `mid_table_path` — a **semicolon**-separated CSV
  with a header row (`SampleID;FBarcodeSequence;RBarcodeSequence;
  CountryOfOrigin;Description`; `csv.DictReader(handle, delimiter=";")`
  is the easiest way in). Build a list of `(label, forward_mid,
  reverse_mid)` tuples, where `label` is `f"{SampleID}_{Description}"` —
  `SampleID` alone would work but isn't very readable, and `Description`
  alone isn't unique (a couple of species appear more than once under
  different `SampleID`s).
- Sets up `self.assigned` (a dict `label -> list of SequencingRead`,
  starting empty for every sample) and `self.unassigned` (a list,
  starting empty).

**Method `assign_reads(self)`:**
For every read, check every sample's MID pair in **both orientations**
(see Background above). On the first orientation that matches:
- trim the MIDs off (reuse `trim_mid_pair`, don't re-slice manually),
- store a new `SequencingRead` with the trimmed sequence in
  `self.assigned[label]`,
- move on to the next read (don't keep checking other samples).

If no sample matches in either orientation, append the original read to
`self.unassigned`.

**Method `report(self)`** → `str`: one line per sample,
`"{label}\t{count}"`, plus a final `"unassigned\t{count}"` line.

**Method `write_fasta(self, output_dir)`:** for every sample with at least
one assigned read, write a FASTA file `{output_dir}/{label}.fasta`
containing its (trimmed) reads.

Run it on the provided data:
```python
demux = Demultiplexer("fishes.fna.gz", "fishes_MIDs.csv")
demux.assign_reads()
print(demux.report())
demux.write_fasta("demux_output")
```

**Expected result** (verify your output matches this — exact formatting of
`report()` is up to you, but the counts must match):

| label | reads |
|---|---|
| `21_Paracheirodon_axelrodi` | 4351 |
| `22_Poecilia_sphenops` | 2826 |
| `23_Hypostomus_plecostomus` | 1438 |
| `29_Otocinclus_affinis` | 4066 |
| `32_Otocinclus_affinis` | 4545 |
| `44_Plecostomus_Gold` | 5271 |
| `46_Gold_Black_Molla` | 4145 |
| `55_V4` | 4576 |
| `51_Colisa_lalia_blood_red_K574_samecci` | 4829 |
| `52_Colisa_lalia_blood_red_K574_samicky` | 4125 |
| `28_Panaqolus_changae` | 15306 |
| `43_Poecilia_sphenops` | 2465 |
| `30_Surubim_Lima` | 4817 |
| `40_Sewelia` | 3501 |
| `61_Xiphophorus_maculatus` | 4410 |
| `35_Pseudotropheus_Cheni` | 3943 |
| `39_Xenopus_laevis_Albin` | 5 |
| `57_Gyrinocheilus` | 7996 |
| `unassigned` | 22033 |

104,648 reads total. About 21% end up unassigned — that's expected for a
real sequencing run (adapter/primer noise, sequencing errors right at the
MID boundary, reads that are too short to contain a full MID, etc.), not a
bug in your code. Don't try to force every read into a sample.

> Reminder from the Background section: some reads for a given sample will
> be tagged `forward_mid ... revcomp(reverse_mid)`, others
> `reverse_mid ... revcomp(forward_mid)`. If your counts are off, check
> you're testing *both* orientations per sample, not just one — even
> though, as noted above, this particular MID table won't actually show a
> difference between them.
