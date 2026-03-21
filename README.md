# Learning Agent

A multi-agent study tool that answers questions and generates quizzes from your lecture slides. Built with visual retrieval — it understands diagrams, formulas, and figures, not just text. See [`PRD/PRD-03-usable-learning-tool.md`](PRD/PRD-03-usable-learning-tool.md).

## Getting started

1. **Install dependencies**

   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Add your slides**

   Drop PDF slide decks into `data/decks/`.

3. **Ingest**

   ```bash
   python -m src.ingest
   ```

   Extracts slide images and builds the visual index. Run again whenever you add new decks.

4. **Run**

   ```bash
   python -m src.app
   ```

   Opens at `http://localhost:8080`.

## Usage

- Select decks from the sidebar to scope your session
- Ask questions in natural language — answers are grounded in your slides with referenced images
- Type `quiz` followed by a topic to generate a quiz
- Wrong answers prompt an inline explanation from the chat agent

i## Requirements

- Python 3.11+
- Anthropic API key in `.env` as `ANTHROPIC_API_KEY`
