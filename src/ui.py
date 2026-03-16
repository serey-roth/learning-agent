"""ui.py — NiceGUI chat demo (no agents)."""

from nicegui import ui


QUESTION_TYPE_LABEL = {
    'mcq': 'Multiple choice',
    'true_false': 'True / False',
    'fill_blank': 'Fill in the blank',
}


# ── message bubble helpers ─────────────────────────────────────────────────────

def user_bubble(container, text: str):
    with container:
        with ui.row().classes('w-full justify-end items-end gap-2'):
            ui.label(text).classes(
                'max-w-sm text-sm px-4 py-2.5 rounded-2xl rounded-br-sm '
                'bg-indigo-600 text-white leading-relaxed'
            )
            ui.icon('person').classes(
                'text-base text-white bg-indigo-400 rounded-full p-1 flex-shrink-0'
            )


def assistant_bubble(container, text: str, sources: str = ''):
    with container:
        with ui.row().classes('w-full justify-start items-end gap-2'):
            ui.icon('auto_awesome').classes(
                'text-base text-indigo-500 bg-indigo-50 rounded-full p-1 flex-shrink-0'
            )
            with ui.column().classes(
                'max-w-xl text-sm px-4 py-3 rounded-2xl rounded-bl-sm '
                'bg-white border border-slate-200 text-slate-700 gap-1 shadow-sm'
            ):
                ui.markdown(text)
                if sources:
                    ui.label(sources).classes('text-xs text-slate-400 mt-0.5')


# ── quiz question renderers ────────────────────────────────────────────────────

def render_step_dots(container, current: int, total: int):
    with container:
        with ui.row().classes('items-center gap-1.5 w-full'):
            for i in range(total):
                ui.element('div').classes(
                    f'h-1 flex-grow rounded-full transition-all '
                    f'{"bg-indigo-500" if i < current else "bg-slate-200"}'
                )


def render_mcq(container, question: str, options: list[str], on_answer):
    selected = {'value': None}
    option_els = []

    with container:
        ui.label(question).classes('text-sm font-medium text-slate-700 leading-relaxed')

        options_col = ui.column().classes('gap-2 w-full mt-2')
        with options_col:
            for i, opt in enumerate(options):
                with ui.row().classes('option-row items-center gap-3 w-full') as row:
                    ui.label(chr(65 + i)).classes(
                        'text-xs font-bold text-slate-400 w-5 h-5 flex items-center justify-center '
                        'rounded-full border border-slate-300 flex-shrink-0'
                    )
                    ui.label(opt).classes('text-sm text-slate-600')
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
                    ui.label('Select an answer first.').classes(
                        'text-xs text-amber-700 bg-amber-50 px-3 py-2 rounded-lg w-full'
                    )
                return
            options_col.set_visibility(False)
            submit_btn.set_visibility(False)
            on_answer(selected['value'], result_area)

        submit_btn.on_click(submit)


def render_true_false(container, question: str, on_answer):
    answered = {'done': False}

    with container:
        ui.label(question).classes('text-sm font-medium text-slate-700 leading-relaxed')
        btn_row = ui.row().classes('gap-3 w-full mt-3')
        result_area = ui.column().classes('gap-2 w-full')

        with btn_row:
            def make_tf(value):
                def click():
                    if answered['done']:
                        return
                    answered['done'] = True
                    btn_row.set_visibility(False)
                    on_answer(value, result_area)
                return click

            ui.button('True', on_click=make_tf(True)).props('unelevated color=positive').classes('flex-grow')
            ui.button('False', on_click=make_tf(False)).props('unelevated color=negative').classes('flex-grow')


def render_fill_blank(container, question: str, on_answer):
    with container:
        ui.label(question).classes('text-sm font-medium text-slate-700 leading-relaxed')
        answer_input = ui.input(placeholder='Your answer...').classes('w-full mt-2').props('outlined dense')
        result_area = ui.column().classes('gap-2 w-full')
        submit_btn = ui.button('Submit answer').props('unelevated color=indigo').classes('w-full mt-1')

        def submit():
            val = answer_input.value.strip()
            if not val:
                with result_area:
                    ui.label('Enter an answer first.').classes(
                        'text-xs text-amber-700 bg-amber-50 px-3 py-2 rounded-lg w-full'
                    )
                return
            submit_btn.set_visibility(False)
            answer_input.set_visibility(False)
            on_answer(val, result_area)

        answer_input.on('keydown.enter', submit)
        submit_btn.on_click(submit)


# ── page ───────────────────────────────────────────────────────────────────────

@ui.page('/')
def index():
    ui.add_css('''
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        body { font-family: "Inter", sans-serif; }

        .option-row {
            border: 1.5px solid #e2e8f0; border-radius: 10px;
            padding: 10px 14px; cursor: pointer;
            transition: all 0.15s;
        }
        .option-row:hover { background: #f8fafc; border-color: #c7d2fe; }
        .option-selected { border-color: #6366f1 !important; background: #eef2ff !important; }

        html, body { overflow: hidden !important; height: 100vh !important; }
        .q-page-container { overflow: hidden !important; }
        .q-page { min-height: unset !important; overflow: hidden !important; }

        .q-field__control { border-radius: 12px !important; }
    ''')

    with ui.header().classes('bg-white border-b border-slate-100 px-6 py-0 items-center shadow-none'):
        with ui.row().classes('w-full items-center justify-between h-12'):
            ui.label('Lecture Assistant').classes('text-sm font-semibold text-slate-800 tracking-tight')

    PANEL_HEIGHT = 'height: calc(100vh - 48px)'
    CHAT_SCROLL_HEIGHT = 'height: calc(100vh - 136px)'

    with ui.element('div').classes('flex flex-row w-full overflow-hidden bg-slate-50').style(PANEL_HEIGHT):

        # ── chat side ───────────────────────────────────────────────────────────
        with ui.element('div').classes('flex flex-col flex-grow overflow-hidden'):
            with ui.scroll_area().style(CHAT_SCROLL_HEIGHT).classes('w-full'):
                chat_panel = ui.column().classes('max-w-2xl mx-auto w-full gap-4 px-6 py-8')

            # input bar
            with ui.element('div').classes('px-6 pt-3 pb-8 bg-slate-50 flex-shrink-0'):
                with ui.element('div').classes('max-w-2xl mx-auto'):
                    with ui.row().classes(
                        'items-center gap-2 bg-white border border-slate-200 '
                        'rounded-2xl px-4 py-2 shadow-sm'
                    ):
                        input_box = (
                            ui.input(placeholder='Ask a question or type "quiz" to start one...')
                            .classes('flex-grow text-sm text-slate-700')
                            .props('borderless dense')
                        )
                        ui.element('div').classes('w-px h-5 bg-slate-200 mx-1')
                        ui.button(icon='arrow_upward', on_click=lambda: send()).props(
                            'unelevated round color=indigo'
                        ).classes('w-9 h-9 flex-shrink-0')

        # ── quiz side (hidden until quiz mode) ──────────────────────────────────
        quiz_panel = (
            ui.element('div')
            .classes('hidden w-96 border-l border-slate-200 bg-white flex-shrink-0 flex flex-col')
            .style(PANEL_HEIGHT)
        )

    # ── quiz data ──────────────────────────────────────────────────────────────

    DEMO_QUESTIONS = [
        {
            'type': 'mcq',
            'question': 'What does a bond coupon represent?',
            'options': [
                'The face value of the bond',
                'A periodic interest payment to the bondholder',
                'The credit rating of the issuer',
                'The maturity date of the bond',
            ],
            'answer': 1,
            'explanation': (
                'A coupon is the periodic interest payment made to the bondholder, '
                'typically expressed as a percentage of the face value. '
                'For example, a $1,000 bond with a 5% coupon pays $50 per year.'
            ),
        },
        {
            'type': 'true_false',
            'question': 'A zero-coupon bond pays interest annually.',
            'answer': False,
            'explanation': (
                'Zero-coupon bonds pay no periodic interest. They are issued at a discount '
                'to face value and mature at par — the return comes entirely from price appreciation.'
            ),
        },
        {
            'type': 'fill_blank',
            'question': "The rate used to discount a bond's cash flows to find its present value is called the ______.",
            'answer': 'discount rate',
            'explanation': (
                'The discount rate (yield to maturity) reflects the market\'s required return '
                'given the bond\'s price, coupon, and time to maturity.'
            ),
        },
    ]

    quiz_state = {'idx': 0, 'score': 0}

    def load_question():
        quiz_panel.clear()
        idx = quiz_state['idx']
        total = len(DEMO_QUESTIONS)

        with quiz_panel:
            # title bar
            with ui.row().classes(
                'items-center justify-between w-full px-5 py-4 '
                'border-b border-slate-100 flex-shrink-0'
            ):
                with ui.column().classes('gap-0'):
                    ui.label('Quiz').classes('text-xs text-slate-400 uppercase tracking-widest font-medium')
                    ui.label('Bonds').classes('text-sm font-semibold text-slate-800 mt-0.5')
                ui.button(icon='close', on_click=close_quiz).props('flat round dense color=grey')

            # completion screen
            if idx >= total:
                score = quiz_state['score']
                pct = round(score / total * 100)
                with ui.column().classes('items-center justify-center gap-4 p-10 text-center flex-grow'):
                    ui.icon('check_circle' if pct >= 60 else 'cancel').classes(
                        f'text-7xl {"text-indigo-400" if pct >= 60 else "text-red-400"}'
                    )
                    ui.label('Quiz complete').classes('text-sm text-slate-500 font-medium')
                    ui.label(f'{score} / {total}').classes('text-4xl font-bold text-slate-800')
                    ui.label(f'{pct}% correct').classes('text-sm text-slate-400')
                    with ui.row().classes('gap-2 mt-4'):
                        ui.button('Try again', on_click=restart_quiz).props('unelevated color=indigo')
                        ui.button('Close', on_click=close_quiz).props('flat color=grey')
                assistant_bubble(
                    chat_panel,
                    f'Quiz done — **{score}/{total}** correct ({pct}%). '
                    f'{"Nice work!" if pct >= 60 else "Keep reviewing and try again."}',
                )
                return

            q = DEMO_QUESTIONS[idx]

            # progress
            with ui.column().classes('px-5 pt-5 pb-3 gap-2 flex-shrink-0'):
                render_step_dots(ui.row().classes('w-full'), idx + 1, total)
                ui.label(f'{idx + 1} of {total}').classes('text-xs text-slate-400')

            ui.separator().classes('flex-shrink-0')

            # question body
            with ui.scroll_area().classes('flex-grow w-full'):
                with ui.column().classes('px-5 pt-5 pb-8 gap-5 w-full'):
                    ui.label(QUESTION_TYPE_LABEL[q['type']]).classes(
                        'text-xs font-semibold text-indigo-500 uppercase tracking-widest'
                    )

                    def on_answer(value, result_area):
                        if q['type'] == 'fill_blank':
                            correct = value.lower().strip() == q['answer'].lower().strip()
                            selected_str, correct_str = value, q['answer']
                        elif q['type'] == 'true_false':
                            correct = value == q['answer']
                            selected_str = 'True' if value else 'False'
                            correct_str = 'True' if q['answer'] else 'False'
                        else:
                            correct = value == q['answer']
                            selected_str = q['options'][value]
                            correct_str = q['options'][q['answer']]

                        if correct:
                            quiz_state['score'] += 1

                        with result_area:
                            if correct:
                                with ui.row().classes('items-center gap-2 bg-green-50 border border-green-200 rounded-xl px-3 py-2.5 w-full'):
                                    ui.icon('check_circle').classes('text-green-500 text-base')
                                    ui.label(selected_str).classes('text-sm text-green-700 font-medium')
                            else:
                                with ui.column().classes('gap-2 w-full'):
                                    with ui.row().classes('items-center gap-2 bg-red-50 border border-red-200 rounded-xl px-3 py-2.5 w-full'):
                                        ui.icon('cancel').classes('text-red-400 text-base')
                                        ui.label(selected_str).classes('text-sm text-red-600')
                                    with ui.row().classes('items-center gap-2 bg-green-50 border border-green-200 rounded-xl px-3 py-2.5 w-full'):
                                        ui.icon('check_circle').classes('text-green-500 text-base')
                                        ui.label(correct_str).classes('text-sm text-green-700 font-medium')

                                prompt_area = ui.column().classes('gap-2 w-full')
                                with prompt_area:
                                    with ui.row().classes('items-center gap-2'):
                                        ui.label('Want an explanation?').classes('text-xs text-slate-500')

                                        def show_explanation(pa=prompt_area, ex=q['explanation']):
                                            pa.clear()
                                            with pa:
                                                ui.label('Explanation').classes(
                                                    'text-xs font-semibold text-slate-400 uppercase tracking-wide'
                                                )
                                                ui.label(ex).classes('text-sm text-slate-600 leading-relaxed')

                                        ui.button('Yes', on_click=show_explanation).props('flat dense color=indigo size=xs')
                                        ui.button('No', on_click=lambda pa=prompt_area: pa.clear()).props('flat dense color=grey size=xs')

                            next_label = 'Finish' if idx + 1 >= total else 'Next →'
                            def advance():
                                quiz_state['idx'] += 1
                                load_question()
                            ui.button(next_label, on_click=advance).props('unelevated color=indigo').classes('w-full mt-1')

                    col = ui.column().classes('gap-3 w-full')
                    if q['type'] == 'mcq':
                        render_mcq(col, q['question'], q['options'], on_answer)
                    elif q['type'] == 'true_false':
                        render_true_false(col, q['question'], on_answer)
                    elif q['type'] == 'fill_blank':
                        render_fill_blank(col, q['question'], on_answer)

    def close_quiz():
        quiz_panel.classes(add='hidden')

    def restart_quiz():
        quiz_state['idx'] = 0
        quiz_state['score'] = 0
        load_question()

    def open_quiz():
        quiz_state['idx'] = 0
        quiz_state['score'] = 0
        quiz_panel.classes(remove='hidden')
        load_question()

    # ── seed content ───────────────────────────────────────────────────────────

    user_bubble(chat_panel, 'What is a bond?')
    assistant_bubble(
        chat_panel,
        'A **bond** is a fixed-income instrument representing a loan made by an '
        'investor to a borrower. It pays periodic **coupon** payments and returns '
        'the principal at maturity.',
        'Sources: [week1, Slide 4]',
    )

    # ── input handler ──────────────────────────────────────────────────────────

    def send():
        text = input_box.value.strip()
        if not text:
            return
        input_box.value = ''
        user_bubble(chat_panel, text)
        if 'quiz' in text.lower():
            open_quiz()
        else:
            assistant_bubble(chat_panel, f'Echo: **{text}**')

    input_box.on('keydown.enter', send)


ui.run(title='Lecture Assistant', port=8080, reload=False)
