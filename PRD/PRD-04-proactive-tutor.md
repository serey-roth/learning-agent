# PRD 04 — Proactive Learning Tutor

**Status:** Active
**Version:** 0.4
**Date:** 2026-03-20

---

## Motivation

V1 through V3 built a capable retrieval and generation system — you can ask questions, get cited answers, and take quizzes grounded in your slides. But it only works if you know what to ask. A student who doesn't know where their gaps are gets nothing from a reactive tool.

The fundamental problem is posture. The current system waits. A real tutor doesn't wait — they show up with a point of view, an agenda, and a model of what you know and don't know. They notice when you're stuck before you do. They connect new material to things you've already seen. They remember that you always miss a particular type of question.

V4 shifts the system from reactive to proactive. The upload is the trigger. The learner model is the memory. The tutor is the face.

---

## Problem

The current system is a smart search engine with a quiz on top. It has no agenda, no memory of what you know, no opinion about what you should study next. Every session starts cold. The system never initiates. It has no model of the subject and no model of you.

A student who knows what to ask gets value. A student who doesn't — which is most students, most of the time — gets nothing.

---

## Goals

- Trigger a comprehension pass on every deck upload, producing a learning brief
- Maintain a learner model updated by every interaction — chat, quiz, and upload
- Surface proactive guidance: what matters, what's hard, where to start
- Connect quiz outcomes back to chat so wrong answers drive deeper exploration
- Make the system feel like a tutor, not a search engine

---

## Non-Goals

- Calendar or course schedule integration
- Multi-user or auth
- Cloud sync or cross-device persistence
- Exam date awareness or countdown features
- External content beyond uploaded slides (web search, textbooks)

---

## User Stories

| # | As a student, I want to... | So that... |
| --- | --- | --- |
| 1 | Get a learning brief when I upload a deck | I know where to start without having to ask |
| 2 | Have the tutor surface what I haven't studied yet | I don't miss important topics by accident |
| 3 | Have wrong quiz answers feed into the conversation | I can explore what I got wrong without switching modes |
| 4 | Have the system remember what I've covered across sessions | I pick up where I left off, not from scratch |
| 5 | Get guidance that's tailored to what I actually know | The system meets me where I am, not at the beginning |
| 6 | Upload multiple decks and get a unified view | The system understands how my material fits together |

---

## Scope

**In:**

- Comprehension agent — runs on upload, produces learning brief (key concepts, difficulty, dependencies)
- Learner model — shared state updated by chat, quiz outcomes, and comprehension; persisted across sessions
- Upload as trigger — comprehension fires automatically after ingest completes
- Cross-deck pass — when multiple decks are uploaded, comprehension maps connections between them
- Chat agent — proactive and reactive; uses learner model to decide what to surface
- Quiz → chat handoff — wrong answers flow into chat context naturally
- Question type expansion — true/false, fill-in-blank, word problems, coding problems

**Out:**

- Learner model exposed as a UI view (internal only for now)
- Research agent for finding external blind spots (post-V4)
- Adaptive quiz difficulty based on performance
- Spaced repetition scheduling
- Multi-user

---

## Architecture

Three agents, one shared learner model:

**Comprehension agent** — triggered on upload. Reads the full deck, extracts key concepts, identifies likely difficulty, maps dependencies on prior material. Writes a subject map to the learner model. On multi-deck upload, runs a cross-deck pass to surface connections and conflicts.

**Chat agent** — the conversational surface. Reactive when you ask, proactive when the learner model indicates something worth surfacing. Reads the subject map and quiz outcomes to shape responses. Writes chat history and explored topics to the learner model.

**Quiz agent** — generates and evaluates assessments. Reads the subject map to generate relevant questions. Writes outcomes (correct, wrong, skipped) to the learner model. Hands off to chat when a question needs deeper exploration.

The learner model is the connective tissue — not an agent, but shared state that all three read from and write to. Persisted to disk between sessions.

---

## Build Sequence

1. Learner model — data structure and persistence; the foundation everything else reads and writes
2. Comprehension agent — upload trigger, subject map, learning brief surfaced in chat
3. Quiz → chat handoff — wrong answers carry question context into chat naturally
4. Proactive chat — tutor surfaces unseen topics and weak areas based on learner model
5. Cross-deck comprehension — connections and dependencies across multiple decks
6. Question type expansion — true/false and fill-in-blank first, word problems and coding after

---

## Key Risks

| Risk | Mitigation |
| --- | --- |
| Comprehension brief is generic, not useful | Prompt must produce opinionated output — not a summary, a study plan |
| Learner model grows stale or contradictory | Version entries with timestamps; recency-weight when reading |
| Proactive tutor feels intrusive | Tutor initiates at natural moments (upload, post-quiz) not mid-conversation |
| Cross-deck pass hallucinates connections | Ground connections in explicit overlap of concepts, not inference |
| Quiz → chat context is lost in handoff | Pass full question, chosen answer, and correct answer as structured context |
