"""app.py — CLI chat for slide RAG.

Usage:
    python app.py                  # pick decks interactively, then chat
    python app.py --deck week1     # skip deck selection, use one deck
"""

import argparse
import re
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

import anthropic

from retrieve import retrieve, build_context

DECKS_DIR = Path("data/decks")
ANSWER_LLM_MODEL = "claude-sonnet-4-6"
MAX_HISTORY_TURNS = 6

SYSTEM_PROMPT = """\
You are a tutor helping a graduate student understand course material.
You have been given a set of slides from their lecture deck.

Rules:
- Ground your answer in the provided slides whenever possible.
- If the slides are sparse or incomplete, supplement with accurate knowledge \
to fully explain the concept. Clearly indicate when you are going beyond what the slides say.
- Always cite the slide number(s) your answer draws from, e.g. [Slide 12].
- If you are uncertain, say so. Do not fabricate facts.
- Be concise but thorough. Explain the "why", not just the "what".
- Use the conversation history to answer follow-up questions naturally.\
"""

_anthropic = anthropic.Anthropic()

# ---------------------------------------------------------------------------
# Deck selection
# ---------------------------------------------------------------------------
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
        return None  # all decks

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


# ---------------------------------------------------------------------------
# Answer generation
# ---------------------------------------------------------------------------
def answer(query: str, history: list[dict], deck_filter: str | list[str] | None) -> tuple[str, list[tuple[int, str]]]:
    """
    Run the full RAG pipeline, stream the response, and return
    (response_text, citations) where citations is [(slide_num, deck_name)].
    """
    slides = retrieve(query, deck_filter)
    context = build_context(slides)
    citation_map = {int(s["metadata"]["slide_number"]): s["metadata"]["deck_name"] for s in slides}

    messages = list(history) + [{
        "role": "user",
        "content": f"Relevant slides:\n\n{context}\n\nQuestion: {query}",
    }]

    full_response = ""
    with _anthropic.messages.stream(
        model=ANSWER_LLM_MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text
    print()

    cited_nums = sorted(set(
        int(n)
        for block in re.findall(r"\[Slides? ([\d,\s]+)\]", full_response)
        for n in re.findall(r"\d+", block)
    ))
    citations = [(n, citation_map[n]) for n in cited_nums if n in citation_map]

    return full_response, citations


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Chat with your slide decks.")
    parser.add_argument("--deck", default=None, help="Use a single deck (skips interactive selection)")
    args = parser.parse_args()

    if args.deck:
        deck_filter: str | list[str] | None = args.deck
    else:
        deck_filter = select_decks()

    if isinstance(deck_filter, list):
        deck_label = ", ".join(deck_filter)
    elif isinstance(deck_filter, str):
        deck_label = deck_filter
    else:
        deck_label = "all decks"

    print(f"\nSlide RAG  —  {deck_label}")
    print("Type your question, or 'quit' to exit.\n")

    history: list[dict] = []

    while True:
        try:
            query = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not query or query.lower() in {"quit", "exit", "q"}:
            break

        print("\nAssistant: ", end="", flush=True)
        response, citations = answer(query, history, deck_filter)

        if citations:
            print("\nSources: " + "  ".join(f"[Slide {n}] {deck}" for n, deck in citations))

        print()

        history.append({"role": "user", "content": query})
        history.append({"role": "assistant", "content": response})
        if len(history) > MAX_HISTORY_TURNS * 2:
            history = history[-(MAX_HISTORY_TURNS * 2):]


if __name__ == "__main__":
    main()
