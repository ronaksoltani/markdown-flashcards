from datetime import date

from markdown_flashcards.scheduler import next_review, parse_markdown


def test_parser_handles_multiline_answers_and_stable_ids():
    source = "Q: What is a path?\nA: A filesystem location.\nIt can be relative.\n"
    first, second = parse_markdown(source), parse_markdown(source)
    assert len(first) == 1 and first[0].id == second[0].id
    assert "relative" in first[0].answer


def test_correct_and_incorrect_reviews_schedule_differently():
    today = date(2026, 1, 1)
    assert next_review(0, True, today)["due"] == "2026-01-02"
    assert next_review(3, False, today)["due"] == "2026-01-01"
