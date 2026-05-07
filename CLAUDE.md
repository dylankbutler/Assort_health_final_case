# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the dashboard

```bash
python3 -m streamlit run dashboard.py --server.port 8501
```

The app auto-reloads on file save. Verify it's up with `curl -s -o /dev/null -w "%{http_code}" http://localhost:8501`.

## Project overview

Single-file Streamlit analytics dashboard (`dashboard.py`) analyzing 45 call transfer records for an Assort Health case study. The data lives in one CSV file. There are no tests, no build step, and no package.json.

**Data file:** `Ops Interview_ Customer Transfer _ Opportunity Case Study - Transcripts.csv`
- 8 columns: Task Result, Task Type, Length (s), Last state, Redirect?, Redirect to, Internal task reason, Transcript
- All 45 rows are transfers to a human representative
- Task Type values: `TRANSFER`, `PREFERS HUMAN`, `REQUESTED TRANSFER`

## Dashboard architecture

`dashboard.py` is structured as one sequential script:

1. **Design tokens** (top of file) — all colors (`CANVAS`, `SURFACE`, `INK`, `MUTED`, `ACCENT`, chart palette constants) are defined as Python strings at the top. Edit here to change the palette globally.
2. **Global CSS block** — injected via `st.markdown(..., unsafe_allow_html=True)`. Uses f-strings referencing the design tokens. Contains all widget overrides, card styles, and typography. Widget label selectors must use both `.stMultiSelect label` / `.stSlider label` class-based selectors AND `[data-testid]` attribute selectors to survive Streamlit version changes.
3. **`load_data()`** — cached with `@st.cache_data`. Computes derived columns: `user_turns`, `assort_turns`, `Opportunity` tier, and `State Label` (human-readable last state). Changes here affect all downstream charts and filters.
4. **`apply_theme(fig, height)`** — applies consistent Plotly layout to every figure. Always call this before `st.plotly_chart()`.
5. **`hex_to_rgba(hex, alpha)`** — converts hex colors to rgba strings for Plotly fill colors (Plotly rejects 8-digit hex).
6. **Layout sections** — rendered top to bottom: Header → KPI bento → Row 1 charts → Row 2 charts → Recommendations → Transcript explorer.

## Key design constraints (taste-skill)

Design is governed by the installed taste skills in `.agents/skills/`. The most relevant are `high-end-visual-design` and `design-taste-frontend`. Core rules in effect:

- **Font:** Plus Jakarta Sans (body) + JetBrains Mono (all numeric values). Inter is banned.
- **Palette:** Single accent `#1d4ed8`. No neon, no pure black. Background `#FAFAF8`, surface `#FFFFFF`.
- **Charts:** All use `apply_theme()`. `paper_bgcolor` and `plot_bgcolor` match `SURFACE`. Bar chart count labels use `textposition="outside"` with `textangle=-90` on the dropout point chart.
- **Cards:** Charts are styled via CSS on `div[data-testid="stPlotlyChart"]` — do NOT wrap `st.plotly_chart()` calls in HTML `<div>` tags, as Streamlit renders them as separate DOM nodes outside any wrapper.
- **KPI cards:** Single-layer `.kpi-card` class (white bg, border, shadow). Hero card uses `.kpi-hero` (dark `#18181B` background).

## Streamlit-specific gotchas

- `st.plotly_chart()` always renders outside any surrounding `st.markdown()` HTML — never try to wrap it in a custom div.
- Widget labels (multiselect, slider) require both class-based (`.stMultiSelect label`) and `data-testid` selectors to reliably override Streamlit's dark-theme white text.
- Plotly `fillcolor` does not accept 8-digit hex (`#rrggbbaa`) — use `hex_to_rgba()`.
- `go.Box` and `go.Violin` `fillcolor` must be rgba strings, not hex with alpha.
