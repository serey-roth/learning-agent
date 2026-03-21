from nicegui import ui

def apply():
    ui.add_css('''
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

        @layer base {
            html, body { overflow: hidden !important; height: 100vh !important; }
            body { font-family: "Inter", sans-serif; }
        }

        @layer overrides {
            .q-page-container { overflow: hidden !important; }
            .q-page { min-height: unset !important; overflow: hidden !important; }
            .q-field__control { border-radius: 12px !important; }
        }

        @layer components {
            /* ── header ── */
            .app-header   { background: white; border-bottom: 1px solid #f1f5f9; padding: 0 1.5rem; box-shadow: none; }
            .header-row   { width: 100%; display: flex; align-items: center; justify-content: space-between; height: 3rem; }
            .header-title { font-size: 0.875rem; font-weight: 600; color: #1e293b; letter-spacing: -0.025em; }

            /* ── layout ── */
            .layout        { display: flex; flex-direction: row; width: 100%; overflow: hidden; background: #f8fafc; }
            .chat-col      { display: flex; flex-direction: column; flex-grow: 1; overflow: hidden; }
            .chat-messages { max-width: 42rem; margin: 0 auto; width: 100%; gap: 1rem; padding: 2rem 1.5rem; }

            /* ── deck panel ── */
            .deck-panel       { display: flex; flex-direction: column; width: 13rem; flex-shrink: 0; border-right: 1px solid #e2e8f0; background: white; overflow-y: auto; }
            .deck-panel-body  { padding: 1.25rem 1rem 0.75rem; gap: 0.75rem; width: 100%; }
            .deck-heading     { font-size: 0.6875rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.1em; }
            .deck-empty       { font-size: 0.75rem; color: #94a3b8; font-style: italic; }
            .deck-chip        { display: block; font-size: 0.75rem; padding: 0.4rem 0.75rem; border-radius: 0.5rem; border: 1px solid #e2e8f0; cursor: pointer; width: 100%; color: #475569; transition: all 0.15s; }
            .deck-chip:hover  { background: #f8fafc; border-color: #c7d2fe; }
            .deck-chip-active { background-color: #eef2ff !important; color: #4f46e5 !important; border-color: #c7d2fe !important; }

            /* ── bubbles ── */
            .bubble-row       { width: 100%; display: flex; align-items: flex-end; gap: 0.5rem; }
            .bubble-row-user  { justify-content: flex-end; }
            .bubble-row-asst  { justify-content: flex-start; }
            .bubble-user {
                max-width: 24rem; font-size: 0.875rem; padding: 0.625rem 1rem;
                border-radius: 1rem; border-bottom-right-radius: 0.125rem;
                background-color: #4f46e5; color: white; line-height: 1.625;
            }
            .bubble-assistant {
                max-width: 36rem; font-size: 0.875rem; padding: 0.75rem 1rem;
                border-radius: 1rem; border-bottom-left-radius: 0.125rem;
                background: white; border: 1px solid #e2e8f0;
                color: #334155; gap: 0.375rem; box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            }
            .bubble-icon      { font-size: 1.125rem; border-radius: 9999px; padding: 0.25rem; flex-shrink: 0; }
            .bubble-icon-user { color: white;   background-color: #818cf8; }
            .bubble-icon-asst { color: #6366f1; background-color: #eef2ff; }
            .bubble-sources   { font-size: 0.75rem; color: #94a3b8; }
            .generating-label { font-size: 0.875rem; color: #94a3b8; font-style: italic; background: white; border: 1px solid #e2e8f0; border-radius: 1rem; border-bottom-left-radius: 0.125rem; padding: 0.625rem 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }

            /* ── slide strip ── */
            .slide-strip      { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; }
            .slide-thumb      { display: flex; flex-direction: column; align-items: center; gap: 0.25rem; cursor: pointer; }
            .slide-thumb-img  { width: 7rem; border-radius: 0.375rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); transition: opacity 0.15s; }
            .slide-thumb:hover .slide-thumb-img { opacity: 0.75; }
            .slide-thumb-label { font-size: 0.6875rem; color: #94a3b8; }

            /* ── input bar ── */
            .input-bar       { padding: 0.75rem 1.5rem 2rem; background: #f8fafc; flex-shrink: 0; }
            .input-bar-inner { max-width: 42rem; margin: 0 auto; }
            .input-row       { display: flex; align-items: center; gap: 0.5rem; background: white; border: 1px solid #e2e8f0; border-radius: 1rem; padding: 0.5rem 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
            .input-text      { flex-grow: 1; font-size: 0.875rem; color: #334155; }
            .input-divider   { width: 1px; height: 1.25rem; background: #e2e8f0; margin: 0 0.25rem; flex-shrink: 0; }
            .send-btn        { width: 2.25rem; height: 2.25rem; flex-shrink: 0; }

            /* ── quiz overlay ── */
            .quiz-overlay        { display: flex; flex-direction: column; width: 100%; height: 100%; background: white; }
            .quiz-overlay-header { display: flex; align-items: flex-start; justify-content: space-between; padding: 1rem 1.25rem; border-bottom: 1px solid #f1f5f9; flex-shrink: 0; }
            .quiz-overlay-content { display: flex; flex-direction: column; flex-grow: 1; overflow: hidden; }

            /* ── quiz ── */
            .quiz-label     { font-size: 0.6875rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600; }
            .quiz-topic     { font-size: 0.875rem; font-weight: 600; color: #1e293b; }
            .quiz-complete  { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1rem; padding: 2.5rem; text-align: center; flex-grow: 1; }
            .quiz-complete-icon      { font-size: 4.5rem; }
            .quiz-complete-icon-pass { color: #818cf8; }
            .quiz-complete-icon-fail { color: #f87171; }
            .quiz-complete-actions   { display: flex; gap: 0.5rem; margin-top: 1rem; justify-content: center; }
            .quiz-score     { font-size: 2.25rem; font-weight: 700; color: #1e293b; }
            .quiz-progress  { padding: 1.25rem 1.25rem 0.75rem; gap: 0.5rem; flex-shrink: 0; }
            .quiz-body      { padding: 1.25rem 1.25rem 2rem; gap: 1rem; width: 100%; }

            /* ── step dots ── */
            .step-dots       { display: flex; align-items: center; gap: 0.375rem; width: 100%; }
            .step-dot        { height: 0.25rem; flex-grow: 1; border-radius: 9999px; transition: all 0.15s; background: #e2e8f0; }
            .step-dot-active { background: #6366f1; }

            /* ── question ── */
            .question-type-label { font-size: 0.6875rem; font-weight: 600; color: #6366f1; text-transform: uppercase; letter-spacing: 0.1em; }
            .question-text       { font-size: 0.875rem; font-weight: 500; color: #334155; line-height: 1.625; }
            .option-row          { border: 1.5px solid #e2e8f0; border-radius: 0.625rem; padding: 0.625rem 0.875rem; cursor: pointer; transition: all 0.15s; }
            .option-row:hover    { background: #f8fafc; border-color: #c7d2fe; }
            .option-selected     { border-color: #6366f1 !important; background: #eef2ff !important; }
            .option-letter       { font-size: 0.75rem; font-weight: 700; color: #94a3b8; width: 1.25rem; height: 1.25rem; display: flex; align-items: center; justify-content: center; border-radius: 9999px; border: 1px solid #cbd5e1; flex-shrink: 0; }
            .option-text         { font-size: 0.875rem; color: #475569; }
            .validation-msg      { font-size: 0.75rem; color: #92400e; background: #fffbeb; padding: 0.5rem 0.75rem; border-radius: 0.5rem; width: 100%; }

            /* ── answer results ── */
            .result-row          { display: flex; align-items: center; gap: 0.5rem; border-radius: 0.75rem; padding: 0.625rem 0.75rem; width: 100%; }
            .result-correct      { background: #f0fdf4; border: 1px solid #bbf7d0; }
            .result-wrong        { background: #fef2f2; border: 1px solid #fecaca; }
            .result-icon-correct { color: #22c55e; font-size: 1rem; }
            .result-icon-wrong   { color: #f87171; font-size: 1rem; }
            .result-text-correct { font-size: 0.875rem; color: #15803d; font-weight: 500; }
            .result-text-wrong   { font-size: 0.875rem; color: #dc2626; }

            /* ── explanation ── */
            .expl-label      { font-size: 0.6875rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
            .expl-text       { font-size: 0.875rem; color: #475569; line-height: 1.625; }
            .expl-prompt     { font-size: 0.75rem; color: #64748b; }
            .expl-prompt-row { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
            .show-more-btn   { align-self: flex-start; margin-left: -0.25rem; }

            /* ── shared prose ── */
            .prose h1 { font-size: 1.25rem; font-weight: 700; color: #1e293b; margin: 1rem 0 0.5rem; }
            .prose h2 { font-size: 1.1rem;  font-weight: 600; color: #1e293b; margin: 0.75rem 0 0.375rem; }
            .prose h3 { font-size: 1rem;    font-weight: 600; color: #334155; margin: 0.5rem 0 0.25rem; }
            .prose p  { margin-bottom: 0.75rem; line-height: 1.7; color: #334155; }
            .prose p:last-child { margin-bottom: 0; }
            .prose ul, .prose ol { padding-left: 1.25rem; margin-bottom: 0.75rem; }
            .prose li { margin-bottom: 0.25rem; line-height: 1.6; color: #334155; }
            .prose blockquote { border-left: 3px solid #c7d2fe; padding-left: 1rem; color: #64748b; font-style: italic; margin: 0.75rem 0; }
            .prose strong { color: #1e293b; }
            .prose code { background: #f1f5f9; padding: 0.125rem 0.375rem; border-radius: 0.25rem; font-size: 0.8125rem; }

            /* ── misc ── */
            .score-subtitle { font-size: 0.875rem; color: #64748b; font-weight: 500; }
            .score-pct      { font-size: 0.875rem; color: #94a3b8; }
            .progress-count { font-size: 0.75rem; color: #94a3b8; }
        }
    ''', shared=True)
