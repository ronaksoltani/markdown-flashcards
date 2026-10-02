import argparse
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from .scheduler import due_cards, load_state, parse_markdown, record_result, save_state


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review Markdown Q/A cards using a Leitner schedule.")
    commands = parser.add_subparsers(dest="command", required=True)
    review = commands.add_parser("review")
    review.add_argument("notes", type=Path)
    review.add_argument("--state", type=Path, default=Path("progress.json"))
    args = parser.parse_args(argv)
    files = [args.notes] if args.notes.is_file() else sorted(args.notes.rglob("*.md"))
    if not files:
        parser.error("no Markdown files found")
    cards = [card for file in files for card in parse_markdown(file.read_text(encoding="utf-8"), str(file))]
    state = load_state(args.state)
    queue = due_cards(cards, state)
    console = Console()
    if not queue:
        console.print("[green]No cards are due. Nice work.[/green]")
        return 0
    for number, card in enumerate(queue, start=1):
        console.print(Panel(card.question, title=f"Card {number}/{len(queue)}"))
        Prompt.ask("Think of your answer, then press Enter", default="")
        console.print(Panel(card.answer, title="Answer"))
        correct = Confirm.ask("Did you recall it?", default=False)
        record_result(state, card, correct)
        save_state(args.state, state)
    console.print(f"Reviewed {len(queue)} card(s). Progress saved to {args.state}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
