import asyncio
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from nicegui import app, ui

app.add_static_files('/data', str(Path('data').resolve()))
from src.agents.orchestrator import classify
from src.agents.qa import ask_question
from src.agents.quiz import generate_quiz, Quiz, Question
from src.state import SessionState
from src import styles

styles.apply()

DECKS_DIR = Path('data/decks')


# ── helpers ────────────────────────────────────────────────────────────────────

def list_decks() -> list[str]:
    return sorted(p.stem for p in DECKS_DIR.glob('*.pdf'))


def user_bubble(container, text: str):
    with container:
        with ui.row().classes('bubble-row bubble-row-user'):
            ui.label(text).classes('bubble-user')
            ui.icon('person').classes('bubble-icon bubble-icon-user')


def asst_bubble(container, text: str):
    with container:
        with ui.row().classes('bubble-row bubble-row-asst'):
            ui.icon('auto_awesome').classes('bubble-icon bubble-icon-asst')
            ui.label(text).classes('generating-label')


def _render_slide_strip(container, slides: list):
    with container:
        with ui.row().classes('slide-strip'):
            for slide in slides:
                url = '/' + slide['image_path']
                label = f"{slide['deck']} · Slide {slide['slide_num']}"

                def make_open(path, lbl):
                    def open_fullscreen():
                        with ui.dialog().props('maximized') as dlg:
                            with ui.column().classes('items-center justify-center w-full h-full bg-black'):
                                ui.button(icon='close', on_click=dlg.close).props('flat round color=white').classes('self-end m-2')
                                ui.image(path).classes('max-h-screen max-w-screen object-contain')
                                ui.label(lbl).classes('text-white text-sm mt-2')
                        dlg.open()
                    return open_fullscreen

                with ui.element('div').classes('slide-thumb').on('click', make_open(url, label)):
                    ui.image(url).classes('slide-thumb-img')
                    ui.label(label).classes('slide-thumb-label')


async def stream_ask(
    prompt: str,
    history: list,
    deck_filter,
    on_token,
) -> tuple[str, list[dict]]:
    token_queue: asyncio.Queue[str | None] = asyncio.Queue()
    loop = asyncio.get_running_loop()

    async def _run():
        try:
            return await asyncio.to_thread(
                ask_question, prompt, history, deck_filter,
                lambda tok: loop.call_soon_threadsafe(token_queue.put_nowait, tok),
            )
        finally:
            loop.call_soon_threadsafe(token_queue.put_nowait, None)

    task = asyncio.create_task(_run())
    accumulated = ''
    while True:
        tok = await token_queue.get()
        if tok is None:
            break
        accumulated += tok
        on_token(accumulated)
    response, _, slides = await task
    return response, slides


# ── quiz overlay ───────────────────────────────────────────────────────────────

def _render_step_dots(current: int, total: int):
    with ui.row().classes('step-dots'):
        for i in range(total):
            ui.element('div').classes('step-dot' + (' step-dot-active' if i < current else ''))


def _render_mcq(question: str, options: list[str], on_answer):
    selected = {'value': None}
    option_els = []

    ui.label(question).classes('question-text')

    options_col = ui.column().classes('gap-2 w-full mt-2')
    with options_col:
        for i, opt in enumerate(options):
            with ui.row().classes('option-row items-center gap-3 w-full') as row:
                ui.label(chr(65 + i)).classes('option-letter')
                ui.label(opt).classes('option-text')
            option_els.append(row)

            def make_select(idx):
                def select():
                    selected['value'] = idx
                    for j, el in enumerate(option_els):
                        if j == idx:
                            el.classes('option-selected')
                        else:
                            el.classes(remove='option-selected')
                return select

            row.on('click', make_select(i))

    result_area = ui.column().classes('gap-2 w-full')
    submit_btn = ui.button('Submit answer').props('unelevated color=indigo').classes('w-full mt-2')

    def submit():
        if selected['value'] is None:
            with result_area:
                ui.label('Select an answer first.').classes('validation-msg')
            return
        options_col.set_visibility(False)
        submit_btn.set_visibility(False)
        on_answer(selected['value'], result_area)

    submit_btn.on_click(submit)


def open_quiz_overlay(quiz: Quiz, session: SessionState, on_done=None):
    quiz_state = {'idx': 0, 'score': 0}

    with ui.dialog().props('maximized persistent') as dlg:
        with ui.element('div').classes('quiz-overlay'):

            with ui.element('div').classes('quiz-overlay-header'):
                with ui.column().classes('gap-0'):
                    ui.label('Quiz').classes('quiz-label')
                    ui.label(quiz.topic.title()).classes('quiz-topic')
                ui.button(icon='close', on_click=dlg.close).props('flat round dense color=grey')

            content = ui.element('div').classes('quiz-overlay-content')

    def load_question():
        content.clear()
        idx, total = quiz_state['idx'], len(quiz.questions)

        with content:
            if idx >= total:
                _render_complete()
                return

            q = quiz.questions[idx]
            with ui.column().classes('quiz-progress'):
                _render_step_dots(idx + 1, total)
                ui.label(f'{idx + 1} of {total}').classes('progress-count')
            ui.separator().classes('flex-shrink-0')

            with ui.scroll_area().classes('flex-grow w-full'):
                with ui.column().classes('quiz-body'):
                    ui.label('Multiple choice').classes('question-type-label')
                    with ui.column().classes('gap-3 w-full'):
                        _render_mcq(q.prompt, q.options, lambda val, area: on_answer(val, area, q, idx, total))

    def on_answer(value: int, result_area, q: Question, idx: int, total: int):
        correct = value == q.answer
        if correct:
            quiz_state['score'] += 1

        with result_area:
            if correct:
                with ui.row().classes('result-row result-correct'):
                    ui.icon('check_circle').classes('result-icon-correct')
                    ui.label(q.options[value]).classes('result-text-correct')
            else:
                with ui.column().classes('gap-2 w-full'):
                    with ui.row().classes('result-row result-wrong'):
                        ui.icon('cancel').classes('result-icon-wrong')
                        ui.label(q.options[value]).classes('result-text-wrong')
                    with ui.row().classes('result-row result-correct'):
                        ui.icon('check_circle').classes('result-icon-correct')
                        ui.label(q.options[q.answer]).classes('result-text-correct')
                    _render_explanation_prompt(q.prompt)

            next_label = 'Finish' if idx + 1 >= total else 'Next →'
            def advance():
                quiz_state['idx'] += 1
                load_question()
            ui.button(next_label, on_click=advance).props('unelevated color=indigo').classes('w-full mt-2')

    def _render_explanation_prompt(prompt: str):
        prompt_area = ui.column().classes('gap-2 w-full')
        with prompt_area:
            with ui.row().classes('expl-prompt-row'):
                ui.label('Want an explanation?').classes('expl-prompt')

                async def show_explanation(pa=prompt_area, p=prompt):
                    pa.clear()
                    with pa:
                        ui.label('Explanation').classes('expl-label')
                        expl_md = ui.markdown('▍').classes('expl-text prose')
                    response, _ = await stream_ask(p, session.history, session.deck_filter, lambda acc: expl_md.set_content(acc + '▍'))
                    expl_md.set_content(response)
                    session.add('user', p)
                    session.add('assistant', response)

                ui.button('Yes', on_click=show_explanation).props('flat dense color=indigo size=xs')
                ui.button('No', on_click=lambda pa=prompt_area: pa.clear()).props('flat dense color=grey size=xs')

    def _render_complete():
        score, total = quiz_state['score'], len(quiz.questions)
        pct = round(score / total * 100)
        passed = pct >= 60
        with ui.column().classes('quiz-complete w-full'):
            ui.icon('check_circle' if passed else 'cancel').classes(
                'quiz-complete-icon ' + ('quiz-complete-icon-pass' if passed else 'quiz-complete-icon-fail')
            )
            ui.label('Quiz complete').classes('score-subtitle')
            ui.label(f'{score} / {total}').classes('quiz-score')
            ui.label(f'{pct}% correct').classes('score-pct')
            with ui.row().classes('quiz-complete-actions'):
                def restart():
                    quiz_state.update({'idx': 0, 'score': 0})
                    load_question()
                ui.button('Try again', on_click=restart).props('unelevated color=indigo')
                ui.button('Close', on_click=dlg.close).props('flat color=grey')
        if on_done:
            on_done(score, total, pct)

    load_question()
    dlg.open()


# ── page ───────────────────────────────────────────────────────────────────────

@ui.page('/')
def index():
    PANEL_HEIGHT       = 'height: calc(100vh - 48px)'
    CHAT_SCROLL_HEIGHT = 'height: calc(100vh - 136px)'

    session = SessionState()

    with ui.header().classes('app-header items-center'):
        with ui.row().classes('header-row'):
            ui.label('Lecture Assistant').classes('header-title')

    with ui.element('div').classes('layout').style(PANEL_HEIGHT):

        # deck sidebar
        selected_decks: set[str] = set()
        with ui.element('div').classes('deck-panel'):
            with ui.column().classes('deck-panel-body'):
                ui.label('Decks').classes('deck-heading')
                decks = list_decks()
                if not decks:
                    ui.label('No decks found.').classes('deck-empty')
                else:
                    def update_filter():
                        if not selected_decks or len(selected_decks) == len(decks):
                            session.deck_filter = None
                        elif len(selected_decks) == 1:
                            session.deck_filter = next(iter(selected_decks))
                        else:
                            session.deck_filter = list(selected_decks)

                    def make_toggle(name: str, chip_el):
                        def toggle():
                            if name in selected_decks:
                                selected_decks.discard(name)
                                chip_el.classes(remove='deck-chip-active')
                            else:
                                selected_decks.add(name)
                                chip_el.classes(add='deck-chip-active')
                            update_filter()
                        return toggle

                    for deck in decks:
                        chip = ui.label(deck).classes('deck-chip')
                        chip.on('click', make_toggle(deck, chip))

        # chat column
        with ui.element('div').classes('chat-col'):
            with ui.scroll_area().style(CHAT_SCROLL_HEIGHT).classes('w-full'):
                chat_panel = ui.column().classes('chat-messages')

            with ui.element('div').classes('input-bar'):
                with ui.element('div').classes('input-bar-inner'):
                    with ui.row().classes('input-row'):
                        input_box = (
                            ui.input(placeholder='Ask a question or type "quiz" to start one...')
                            .classes('input-text')
                            .props('borderless dense')
                        )
                        ui.element('div').classes('input-divider')
                        ui.button(icon='arrow_upward', on_click=lambda: send()).props(
                            'unelevated round color=indigo'
                        ).classes('send-btn')

    # ── input handler ──────────────────────────────────────────────────────────

    async def send():
        text = input_box.value.strip()
        if not text:
            return
        input_box.value = ''
        input_box.props(add='disable')

        session.add_query(text)
        user_bubble(chat_panel, text)

        intent = await asyncio.to_thread(classify, text, session.recent_queries[:-1])

        if intent.type == 'qa':
            query = intent.query or text

            with chat_panel:
                with ui.row().classes('bubble-row bubble-row-asst'):
                    ui.icon('auto_awesome').classes('bubble-icon bubble-icon-asst')
                    with ui.column().classes('bubble-assistant gap-2'):
                        response_md = ui.markdown('▍').classes('prose')
                        slides_container = ui.element('div')

            try:
                response, slides = await stream_ask(
                    query, session.history, session.deck_filter,
                    lambda acc: response_md.set_content(acc + '▍'),
                )
            except Exception as e:
                response_md.set_content('')
                asst_bubble(chat_panel, f'Request failed: {e}')
                input_box.props(remove='disable')
                return

            response_md.set_content(response)
            if slides:
                _render_slide_strip(slides_container, slides)
            session.add('user', query)
            session.add('assistant', response)

        elif intent.type == 'quiz':
            topic = intent.topic or text

            with chat_panel:
                quiz_row = ui.row().classes('bubble-row bubble-row-asst')
            with quiz_row:
                ui.icon('quiz').classes('bubble-icon bubble-icon-asst')
                ui.label(f'Generating quiz on {topic}…').classes('generating-label')

            try:
                quiz = await asyncio.to_thread(generate_quiz, topic, session.deck_filter)
            except Exception as e:
                quiz_row.clear()
                asst_bubble(chat_panel, f'Request failed: {e}')
                input_box.props(remove='disable')
                return

            quiz_row.clear()
            with quiz_row:
                ui.icon('quiz').classes('bubble-icon bubble-icon-asst')
                if not quiz.questions:
                    ui.label('No questions could be generated for that topic.').classes('generating-label')
                else:
                    refs = {}
                    with ui.column().classes('bubble-assistant gap-1'):
                        ui.label(topic.title()).classes('quiz-topic')
                        refs['count'] = ui.label(f'{len(quiz.questions)} questions').classes('bubble-sources')

                        def on_quiz_done(score, total, pct):
                            refs['btn'].set_visibility(False)
                            refs['count'].text = f'{score}/{total} · {pct}% correct'

                        refs['btn'] = ui.button(
                            'Start quiz →',
                            on_click=lambda: open_quiz_overlay(quiz, session, on_done=on_quiz_done),
                        ).props('flat dense color=indigo size=sm').classes('show-more-btn')

        else:
            asst_bubble(chat_panel, "I can only answer questions or run quizzes about your slides.")

        input_box.props(remove='disable')

    input_box.on('keydown.enter', send)


ui.run(title='Lecture Assistant', port=8080, reload=False)
