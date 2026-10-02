from __future__ import annotations

import hashlib
import json
import re
import tempfile
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path

BOX_DAYS = (0, 1, 3, 7, 14)


@dataclass(frozen=True)
class Card:
    id: str
    question: str
    answer: str
    source: str


def parse_markdown(text: str, source: str = "<memory>") -> list[Card]:
    cards: list[Card] = []
    question: str | None = None
    answer_lines: list[str] = []

    def save() -> None:
        nonlocal question, answer_lines
        answer = "\n".join(answer_lines).strip()
        if question and answer:
            stable = hashlib.sha256(f"{question.strip()}\0{answer}".encode()).hexdigest()[:16]
            cards.append(Card(stable, question.strip(), answer, source))
        question, answer_lines = None, []

    for line in text.splitlines():
        if match := re.match(r"^\s*Q:\s*(.+?)\s*$", line, re.IGNORECASE):
            save()
            question = match.group(1)
        elif question is not None and (match := re.match(r"^\s*A:\s*(.*)$", line, re.IGNORECASE)):
            answer_lines = [match.group(1)]
        elif question is not None and answer_lines and line.strip():
            answer_lines.append(line.rstrip())
        elif question is not None and not line.strip():
            save()
    save()
    return cards


def next_review(box: int, correct: bool, today: date | None = None) -> dict[str, object]:
    if not 0 <= box < len(BOX_DAYS):
        raise ValueError(f"box must be between 0 and {len(BOX_DAYS) - 1}")
    next_box = min(box + 1, len(BOX_DAYS) - 1) if correct else 0
    interval = BOX_DAYS[next_box]
    return {"box": next_box, "due": ((today or date.today()) + timedelta(days=interval)).isoformat(),
            "interval_days": interval}


def due_cards(cards: list[Card], state: dict[str, dict[str, object]], today: date | None = None) -> list[Card]:
    day = (today or date.today()).isoformat()
    return [card for card in cards if str(state.get(card.id, {}).get("due", "")) <= day]


def load_state(path: Path) -> dict[str, dict[str, object]]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path: Path, state: dict[str, dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        json.dump(state, stream, indent=2)
        temporary = Path(stream.name)
    temporary.replace(path)


def record_result(state: dict[str, dict[str, object]], card: Card, correct: bool,
                  today: date | None = None) -> dict[str, dict[str, object]]:
    previous_box = int(state.get(card.id, {}).get("box", 0))
    state[card.id] = next_review(previous_box, correct, today) | {"question": card.question}
    return state
