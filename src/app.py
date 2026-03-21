import argparse
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from src.agents.orchestrator import classify
from src.agents.qa import ask_question
from src.agents.quiz import generate_quiz, run_quiz
from src.state import SessionState

DECKS_DIR = Path("data/decks")


def list_decks() -> list[str]:
    return sorted(p.stem for p in DECKS_DIR.glob("*.pdf"))


def select_decks() -> str | list[str] | None:
    decks = list_decks()
    if not decks:
        print("No decks found in data/decks/")
        return None

    print("Available decks:")
    for i, name in enumerate(decks, 1):
        print(f"  [{i}] {name}")
    print()

    raw = input("Select decks (comma-separated numbers, or Enter for all): ").strip()
    if not raw:
        return None

    selected = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(decks):
                selected.append(decks[idx])

    if not selected or len(selected) == len(decks):
        return None
    return selected[0] if len(selected) == 1 else selected


RECENT_QUERIES_LIMIT = 3


def _ask_question(query: str, state: SessionState, deck_filter: str | list[str] | None) -> None:
    print("\nAssistant: ", end="", flush=True)
    response, citations = ask_question(query, state.history, deck_filter, on_stream=lambda token: print(token, end="", flush=False))
    if citations:
        print(f"Sources: {', '.join(f'[{c}]' for c in citations)}")
    print()
    state.add("user", query)
    state.add("assistant", response)


def main() -> None:
    parser = argparse.ArgumentParser(description="Chat with your slide decks.")
    parser.add_argument("--deck", default=None, help="Use a single deck (skips interactive selection)")
    args = parser.parse_args()

    deck_filter: str | list[str] | None = args.deck if args.deck else select_decks()

    print("\nLecture Assistant — ask a question or request a quiz. Type 'quit' to exit.\n")

    state = SessionState()

    while True:
        try:
            query = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not query or query.lower() in {"quit", "exit", "q"}:
            break

        state.add_query(query)
        intent = classify(query, recent_queries=state.recent_queries[:-1])

        if intent.type == 'quit':
            break
        
        elif intent.type == 'qa':
            _ask_question(intent.query or query, state, deck_filter)

        elif intent.type == 'quiz':
            print("\n── Quiz ─────────────────────────────────────────\n")
            quiz = generate_quiz(intent.topic or query, deck_filter=deck_filter)

            def on_wrong(q):
                if input("  Want an explanation? (y/n): ").strip().lower() == "y":
                    _ask_question(q.prompt, state, deck_filter)

            run_quiz(quiz, on_wrong=on_wrong)
            
        else:
            print("  Sorry, I can only answer questions or run quizzes about your slides.\n")


if __name__ == "__main__":
    main()
