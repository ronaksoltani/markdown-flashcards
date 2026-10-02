# Markdown Flashcards

Review question-and-answer cards from Markdown files with a simple Leitner spaced-repetition schedule. Review state is saved locally as JSON; answers and notes remain on your machine.

## Quick start

Create a note using this format:

```markdown
Q: What does `pathlib.Path` represent?
A: A filesystem path with methods for common path operations.
```

Then run:

```bash
python -m venv .venv
python -m pip install -e .
flashcards review ./notes
```

Type `y` when you recalled the answer or `n` when you missed it. Correct cards move to longer intervals; missed cards return to the first box. Override the state path with `--state`.

## Learning notes

Practice Markdown parsing, stable card IDs, JSON persistence, pure scheduling functions, and an interactive CLI loop. The included schedule is deliberately small and explainable; it is not a claim about an optimal memory model.

## Development

```bash
python -m pip install -e ".[dev]"
pytest
```

## License

MIT. See [LICENSE](LICENSE).
