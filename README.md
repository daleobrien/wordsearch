# wordsearch

Create wordsearch puzzles from a list of words.

You can optionally supply a second list of *hidden* words. These are placed into
the puzzle just like the real answers, but they are **left out of the search
key**, so the solver has to pick the correct word out of several near-matches.

## Requirements

- [uv](https://docs.astral.sh/uv/) — used to manage the environment. The project
  targets Python 3.14 (see `.python-version`), which `uv` will fetch for you.

## Running

`wordsearch` is exposed as a project script, so you can run it straight from a
checkout with `uv run`:

```sh
uv run wordsearch words.txt
```

Pass a hidden word list as the second argument to make the puzzle harder:

```sh
uv run wordsearch words.txt hidden.txt
```

The repo ships with an example list (`words.txt`, animal names) and a hidden list
(`hidden.txt`, deliberate near-miss spellings).

### Word lists

Each list is a plain-text file with one word per line:

```
Aardvark
Albatross
Alpaca
```

- The **word list** words are placed in the grid and listed in the key.
- The **hidden word list** words are placed in the grid but omitted from the key.

Words are upper-cased when placed in the grid.

### Options

| Option | Description |
| --- | --- |
| `-h`, `--help` | Show the help message and exit. |
| `-l LEVEL`, `--level LEVEL` | Number of text directions to use, `1`–`8` (default: `4`). |
| `-p FILE`, `--pdf FILE` | Also write the puzzle to a PDF file at `FILE`. |

Lower levels produce easier puzzles. Directions are added in this order as the
level increases:

| Level | Direction |
| --- | --- |
| 1 | left to right |
| 2 | top to bottom |
| 3 | diagonal, downward |
| 4 | diagonal, upward |
| 5 | upwards |
| 6 | backwards |
| 7 | diagonal, upward & backwards |
| 8 | diagonal, downward & backwards |

So the default level of `4` uses left-to-right, top-to-bottom and both diagonals.
A level of `1` limits every word to left-to-right, making a much easier puzzle:

```sh
uv run wordsearch -l 1 words.txt
```

## Output

The program prints three sections to the terminal:

1. **The puzzle** — the full grid of letters the solver works from.
2. **The key** — the list of words to find, laid out in columns.
3. **The solution** — the same grid with only the key words filled in, for
   checking answers.

### PDF output

Pass `-p`/`--pdf` with a filename to also write the puzzle to a PDF (the text
output is still printed). The PDF has two pages: the puzzle with its word key on
page one, and the solution on page two, ready to print.

```sh
uv run wordsearch -p example.pdf words.txt hidden.txt
```

Rendering is done with [ReportLab](https://pypi.org/project/reportlab/), a
project dependency, on A4 paper.

## Example

Create a small word list and run the tool:

```sh
$ printf 'apple\ngrape\nlemon\nmelon\npeach\nberry\n' > fruit.txt
$ uv run wordsearch -l 4 fruit.txt

┌───┬───┬───┬───┬───┬───┬───┐
│ X │ U │ R │ A │ L │ M │ P │
├───┼───┼───┼───┼───┼───┼───┤
│ O │ W │ B │ P │ E │ E │ E │
├───┼───┼───┼───┼───┼───┼───┤
│ H │ H │ G │ P │ M │ L │ A │
├───┼───┼───┼───┼───┼───┼───┤
│ A │ X │ R │ L │ O │ O │ C │
├───┼───┼───┼───┼───┼───┼───┤
│ W │ T │ A │ E │ N │ N │ H │
├───┼───┼───┼───┼───┼───┼───┤
│ V │ O │ P │ N │ Y │ P │ Z │
├───┼───┼───┼───┼───┼───┼───┤
│ I │ B │ E │ R │ R │ Y │ B │
└───┴───┴───┴───┴───┴───┴───┘

 apple  grape  melon
 berry  lemon  peach

┌───┬───┬───┬───┬───┬───┬───┐
│   │   │   │ A │ L │ M │ P │
├───┼───┼───┼───┼───┼───┼───┤
│   │   │   │ P │ E │ E │ E │
├───┼───┼───┼───┼───┼───┼───┤
│   │   │ G │ P │ M │ L │ A │
├───┼───┼───┼───┼───┼───┼───┤
│   │   │ R │ L │ O │ O │ C │
├───┼───┼───┼───┼───┼───┼───┤
│   │   │ A │ E │ N │ N │ H │
├───┼───┼───┼───┼───┼───┼───┤
│   │   │ P │   │   │   │   │
├───┼───┼───┼───┼───┼───┼───┤
│   │ B │ E │ R │ R │ Y │   │
└───┴───┴───┴───┴───┴───┴───┘
```

In order, that is: the puzzle grid, the key (words to find), and the solution
grid — for instance `apple` runs down the middle column and `berry` runs across
the bottom row. The filler letters are chosen at random, so each run produces a
different grid.

## Development

```sh
uv sync                            # create/update the virtual environment
uv run wordsearch words.txt        # run the CLI

uv run python -m wordsearch.main -h   # run the module directly
```

The single entry point is `main()` in `src/wordsearch/main.py`, wired up as
`wordsearch = "wordsearch.main:main"` in `pyproject.toml`.

### Programmatic use

A built `Grid` can be rendered directly with `grid.to_pdf(path)`, which accepts
optional `title` and `solution` arguments (e.g. `grid.to_pdf(path,
 solution=False)` for a puzzle-only PDF).
