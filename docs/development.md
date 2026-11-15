# Development

[Back to the README](../README.md)

```sh
uv sync                            # create/update the virtual environment
uv run wordsearch words.txt        # run the CLI

uv run python -m wordsearch.main -h   # run the module directly
```

The single entry point is `main()` in `src/wordsearch/main.py`, wired up as
`wordsearch = "wordsearch.main:main"` in `pyproject.toml`.

## Programmatic use

A built `Grid` can be rendered directly with `grid.to_pdf(path)`, which accepts
optional `title` and `solution` arguments (e.g. `grid.to_pdf(path,
 solution=False)` for a puzzle-only PDF).

## How a puzzle is made

`Grid` in `src/wordsearch/main.py` does the work. The grid starts as a square
as wide as the longest word. The words, hidden ones included, are placed
longest first, each at a random position in one of the directions the level
allows; a word may cross another where their letters agree. If a word can't be
placed, placement starts again, and every fifth failed try the grid grows by one
cell each way. The empty cells are then
filled with random letters. The solution grid keeps only the key words, so the
hidden near-misses look like filler there.

## The cover

`docs/cover.png` is the puzzle and solution pages of a level 8 PDF made from
`words.txt` and `hidden.txt`, side by side on a 1280 by 640 card.
