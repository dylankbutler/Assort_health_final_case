import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from collections import Counter

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Transfer Analysis — Assort Health",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Design System (taste-skill applied) ──────────────────────────────────────
# Vibe: Soft Structuralism — clinical warmth, airy bento, monospace data
# Variance: 8 | Motion: 4 (CSS only, Streamlit constraint) | Density: 4
#
# Palette — single accent, no neon, no pure black, warm neutral base
CANVAS       = "#FAFAF8"   # warm off-white
SURFACE      = "#FFFFFF"   # card fill
BORDER       = "rgba(0,0,0,0.07)"
INK          = "#18181B"   # Zinc-950 off-black
MUTED        = "#787774"   # secondary text
ACCENT       = "#1d4ed8"   # desaturated electric blue (single accent)
ACCENT_LIGHT = "#EEF2FF"   # tinted surface for accent elements

# Chart palette — desaturated categoricals, no neon
C_PREFER   = "#94a3b8"   # cool slate
C_REQUEST  = "#c4956a"   # warm tan
C_TRANSFER = "#4a7c9e"   # steel blue
C_HIGH     = "#4a9e6b"   # muted sage
C_MEDIUM   = "#c4956a"   # warm amber (shared)
C_LOW      = "#94a3b8"   # muted slate (shared)
C_NEUTRAL  = "#18181B"   # near-black bars
GRID_LINE  = "rgba(0,0,0,0.05)"
CHART_FONT = "#787774"

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=JetBrains+Mono:wght@400;500&display=swap');

  /* ── Entry animation ── */
  @keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
  }}

  /* ── Base ── */
  html, body, [class*="css"], .stApp {{
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: {CANVAS} !important;
    color: {INK} !important;
  }}
  .main .block-container {{
    padding: 3rem 3.5rem 4rem 3.5rem;
    max-width: 1400px;
    animation: fadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
  }}
  #MainMenu, footer, header {{ visibility: hidden; }}

  /* ── Typography ── */
  h1, h2, h3 {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: {INK} !important;
    letter-spacing: -0.025em;
  }}

  /* ── Eyebrow tag ── */
  .eyebrow {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: {MUTED};
    margin-bottom: 10px;
    display: block;
  }}

  /* ── KPI cards — single layer, consistent ── */
  .kpi-card {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 20px 22px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    min-height: 110px;
  }}
  .kpi-label {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {MUTED};
    margin-bottom: 8px;
  }}
  .kpi-value-sm {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 30px;
    font-weight: 500;
    color: {INK};
    line-height: 1;
    letter-spacing: -0.03em;
  }}
  .kpi-sub {{
    font-size: 12px;
    color: {MUTED};
    margin-top: 6px;
    font-weight: 400;
    line-height: 1.5;
  }}

  /* ── Hero KPI (wide dark card) ── */
  .kpi-hero {{
    background: {INK};
    border-radius: 14px;
    padding: 24px 28px;
    min-height: 110px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.12);
    border-top: 3px solid {ACCENT};
  }}
  .kpi-hero .eyebrow {{ color: rgba(255,255,255,0.4); margin-bottom: 10px; }}
  .kpi-hero .kpi-value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 52px;
    font-weight: 500;
    color: #fff;
    letter-spacing: -0.04em;
    line-height: 1;
  }}
  .kpi-hero .kpi-sub {{ color: rgba(255,255,255,0.45); font-size: 12px; margin-top: 8px; line-height: 1.5; }}
  .kpi-hero .kpi-tag {{
    display: inline-block;
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 5px;
    padding: 2px 9px;
    font-size: 10px;
    font-weight: 700;
    color: rgba(255,255,255,0.6);
    margin-top: 12px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }}

  /* ── Section header ── */
  .section-header-group {{
    border-left: 3px solid {ACCENT};
    padding-left: 12px;
    margin-bottom: 20px;
  }}
  .section-label {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: {MUTED};
    margin: 0 0 6px 0;
  }}
  .section-title {{
    font-size: 17px;
    font-weight: 700;
    color: {INK};
    margin: 0 0 2px 0;
    letter-spacing: -0.02em;
  }}
  .section-desc {{
    font-size: 13px;
    color: {MUTED};
    margin: 0;
    line-height: 1.5;
  }}

  /* ── Divider ── */
  .divider {{
    border: none;
    border-top: 1px solid {BORDER};
    margin: 28px 0 36px 0;
  }}

  /* ── Pastel badges ── */
  .badge-high   {{ background:#EDF3EC; color:#346538; border-radius:5px;
                  padding:2px 9px; font-size:10px; font-weight:700;
                  letter-spacing:0.05em; text-transform:uppercase; }}
  .badge-medium {{ background:#FBF3DB; color:#956400; border-radius:5px;
                  padding:2px 9px; font-size:10px; font-weight:700;
                  letter-spacing:0.05em; text-transform:uppercase; }}
  .badge-low    {{ background:#F1F5F9; color:#64748b; border-radius:5px;
                  padding:2px 9px; font-size:10px; font-weight:700;
                  letter-spacing:0.05em; text-transform:uppercase; }}
  .badge-type   {{ background:#E1F3FE; color:#1F6C9F; border-radius:5px;
                  padding:2px 9px; font-size:10px; font-weight:700;
                  letter-spacing:0.05em; text-transform:uppercase; }}

  /* ── Chart wrappers — target Streamlit's own plotly container ── */
  div[data-testid="stPlotlyChart"] {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 22px 16px 12px 16px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.03);
    overflow: visible;
  }}
  /* Avoid clipping Plotly SVG title / subtitle at the ceiling of the card */
  div[data-testid="stPlotlyChart"] .js-plotly-plot {{
    overflow: visible !important;
  }}
  .chart-label {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {MUTED};
    margin-bottom: 2px;
    margin-top: 0;
  }}
  .chart-title {{
    font-size: 14px;
    font-weight: 600;
    color: {INK};
    margin-bottom: 8px;
    margin-top: 0;
    letter-spacing: -0.01em;
  }}

  /* ── Transcript ── */
  .tx-content {{
    font-size: 12.5px;
    line-height: 1.8;
    color: {MUTED};
    padding: 4px 0 8px 0;
  }}
  .tx-assort {{ color: {ACCENT}; font-weight: 600; }}
  .tx-user   {{ color: {INK}; font-weight: 500; }}
  .tx-meta {{
    font-size: 11px;
    color: {MUTED};
    margin-bottom: 12px;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    align-items: center;
  }}

  /* ── Streamlit expander — light theme ── */
  div[data-testid="stExpander"] {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    margin-bottom: 6px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.03) !important;
  }}
  div[data-testid="stExpander"] summary {{
    font-size: 13px !important;
    font-weight: 500 !important;
    color: {INK} !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    padding: 12px 16px !important;
  }}
  div[data-testid="stExpander"] > div:last-child {{
    padding: 0 16px 14px 16px !important;
    background: {SURFACE} !important;
    border-radius: 0 0 10px 10px !important;
  }}

  /* ── Streamlit widgets — light theme override ── */

  /* Nuclear catch-all: any label or paragraph inside a widget gets ink color.
     Streamlit's dark-theme sets these to white; we override every possible
     selector it might use across versions. */
  .stMultiSelect label,
  .stMultiSelect p,
  .stMultiSelect span:not([data-baseweb="tag"] span),
  .stSlider label,
  .stSlider p,
  .stSlider span,
  [data-testid="stMultiSelect"] label,
  [data-testid="stMultiSelect"] p,
  [data-testid="stSlider"] label,
  [data-testid="stSlider"] p,
  [data-testid="stWidgetLabel"],
  [data-testid="stWidgetLabel"] *,
  label[data-baseweb="form-control-label"],
  div[data-baseweb="form-control"] label,
  div[data-baseweb="form-control"] p {{
    color: {MUTED} !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
  }}

  /* Multiselect outer box */
  div[data-baseweb="select"] > div {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    color: {INK} !important;
  }}

  /* Multiselect input text */
  div[data-baseweb="select"] input {{
    color: {INK} !important;
  }}

  /* Selected chips/tags */
  [data-baseweb="tag"] {{
    background-color: {ACCENT_LIGHT} !important;
    border: none !important;
  }}
  [data-baseweb="tag"] span,
  [data-baseweb="tag"] button span {{
    color: {ACCENT} !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
  }}

  /* Dropdown popover / menu panel */
  div[data-baseweb="popover"] > div,
  div[data-baseweb="menu"] {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08) !important;
  }}

  /* Dropdown option items */
  li[role="option"] {{
    background: {SURFACE} !important;
    color: {INK} !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    letter-spacing: normal !important;
    text-transform: none !important;
  }}
  li[role="option"]:hover {{
    background: {CANVAS} !important;
    color: {INK} !important;
  }}
  li[role="option"][aria-selected="true"] {{
    background: {ACCENT_LIGHT} !important;
    color: {ACCENT} !important;
  }}

  /* Slider range numbers */
  div[data-testid="stTickBarMin"],
  div[data-testid="stTickBarMax"],
  div[data-testid="stThumbValue"] {{
    color: {MUTED} !important;
    font-size: 11px !important;
    font-weight: 400 !important;
    letter-spacing: normal !important;
    text-transform: none !important;
  }}
</style>
""", unsafe_allow_html=True)


# ── Load & enrich data ────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv(
        "Ops Interview_ Customer Transfer _ Opportunity Case Study - Transcripts.csv"
    )
    df.columns = df.columns.str.strip()
    df["Length (s)"] = pd.to_numeric(df["Length (s)"], errors="coerce")

    df["user_turns"]   = df["Transcript"].apply(
        lambda t: len(re.findall(r"USER:", str(t))))
    df["assort_turns"] = df["Transcript"].apply(
        lambda t: len(re.findall(r"ASSORT:", str(t))))

    def opp_tier(row):
        if row["Task Type"] == "PREFERS HUMAN":
            return "Low"
        if row["Task Type"] == "REQUESTED TRANSFER":
            return "Medium"
        ls = row["Last state"]
        if ls in ("Redirect Patient Search Error", "Collecting Last Name", "ASK REASON"):
            return "High — STT / NLP"
        return "High — System Gap"

    df["Opportunity"] = df.apply(opp_tier, axis=1)

    state_map = {
        "REDIRECT":                      "Generic redirect",
        "Redirect Escape":               "User requested human",
        "REDIRECT CC AND VT":            "Specialty procedure (IUD etc.)",
        "REDIRECT SLOT MACHINE":         "No availability found",
        "Redirect Patient Search Error": "Patient search failed",
        "Collecting Last Name":          "Dropped during name capture",
        "COLLECT PROVIDER":              "Dropped: provider capture",
        "ASK REASON":                    "Dropped: asking visit reason",
        "ASKING PROVIDER AND LOCATION":  "Dropped: provider / location",
        "Private Insurance Numbers":     "Dropped: insurance capture",
    }
    df["State Label"] = df["Last state"].map(state_map).fillna(df["Last state"])
    return df


df = load_data()
total        = len(df)
pref_human   = (df["Task Type"] == "PREFERS HUMAN").sum()
requested    = (df["Task Type"] == "REQUESTED TRANSFER").sum()
sys_transfer = (df["Task Type"] == "TRANSFER").sum()
avg_len      = df["Length (s)"].mean()
high_opp     = df["Opportunity"].str.startswith("High").sum()


# ── Plotly chart defaults ──────────────────────────────────────────────────────
def apply_theme(fig, height=300):
    # Top margin reserves space for two-line HTML titles (eyebrow + headline).
    # t=52 was too tight and clipped the uppercase label on dense charts.
    fig.update_layout(
        paper_bgcolor=SURFACE,
        plot_bgcolor=CANVAS,
        font=dict(family="Plus Jakarta Sans", color=CHART_FONT, size=11),
        margin=dict(l=8, r=8, t=74, b=12),
        height=height,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=MUTED, size=11),
        ),
        showlegend=False,
    )
    fig.update_xaxes(
        gridcolor=GRID_LINE, showgrid=True, zeroline=False,
        tickfont=dict(color=MUTED, size=10), linecolor=GRID_LINE,
    )
    fig.update_yaxes(
        gridcolor=GRID_LINE, showgrid=False, zeroline=False,
        tickfont=dict(color=MUTED, size=10), linecolor="rgba(0,0,0,0)",
    )
    return fig

CHART_CFG = {"displayModeBar": False}

def hex_to_rgba(hex_color, alpha=0.13):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

TYPE_COLORS = {
    "PREFERS HUMAN":      C_PREFER,
    "REQUESTED TRANSFER": C_REQUEST,
    "TRANSFER":           C_TRANSFER,
}
OPP_COLORS = {
    "High — System Gap":  C_HIGH,
    "High — STT / NLP":  "#6abeaa",
    "Medium":             C_MEDIUM,
    "Low":                C_LOW,
}


# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<span class="eyebrow">Assort Health &nbsp;·&nbsp; Agent Deployment Case Study</span>
<h1 style="font-size:36px; font-weight:800; letter-spacing:-0.035em;
           color:#18181B; margin:0 0 6px 0; line-height:1.1;">
  45 calls transferred.<br>Here's why and how to fix it.
</h1>
<p style="font-size:15px; color:#787774; margin:0 0 0 0; max-width:600px; line-height:1.6;">
  Every call in this dataset was redirected to a human representative.
  This analysis segments the root causes and surfaces the highest-leverage
  opportunities to increase automation and improve caller experience.
</p>
<hr class="divider">
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# KPI BENTO — asymmetric layout (taste: no equal N-column grids)
# ═══════════════════════════════════════════════════════════════════════════════
hero_col, right_cols = st.columns([1.4, 2.6])

with hero_col:
    st.markdown(f"""
    <div class="kpi-hero">
      <span class="eyebrow">Automation opportunity</span>
      <div class="kpi-value">{high_opp}<span style="font-size:28px;opacity:0.4">/45</span></div>
      <div class="kpi-sub">calls could be kept in the automated flow with targeted improvements</div>
      <div class="kpi-tag">{high_opp/total*100:.0f}% recoverable</div>
    </div>
    """, unsafe_allow_html=True)

with right_cols:
    m1, m2, m3, m4 = st.columns(4)

    def mini_kpi(col, label, value, sub):
        col.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value-sm">{value}</div>
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    mini_kpi(m1, "Prefer Human",    f"{pref_human}",   f"{pref_human/total*100:.0f}% of calls")
    mini_kpi(m2, "System Transfer", f"{sys_transfer}",  f"{sys_transfer/total*100:.0f}% of calls")
    mini_kpi(m3, "Requested XFR",   f"{requested}",    f"{requested/total*100:.0f}% of calls")
    mini_kpi(m4, "Avg Handle Time", f"{avg_len:.0f}s",  f"{df['Length (s)'].min():.0f}s – {df['Length (s)'].max():.0f}s range")

st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ROW 1 — Transfer type + Drop-off state (asymmetric 1:2 split)
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header-group">
  <div class="section-label">Root cause breakdown</div>
  <div class="section-title">Where and why calls leave the automated flow</div>
  <div class="section-desc">Left: transfer type. Right: the exact system state at the moment of transfer.</div>
</div>
""", unsafe_allow_html=True)

chart_l, chart_r = st.columns([1, 2])

with chart_l:
    type_counts = df["Task Type"].value_counts().reset_index()
    type_counts.columns = ["Task Type", "Count"]
    fig = go.Figure(go.Pie(
        labels=type_counts["Task Type"],
        values=type_counts["Count"],
        hole=0.65,
        marker=dict(
            colors=[TYPE_COLORS.get(t, "#ccc") for t in type_counts["Task Type"]],
            line=dict(color=SURFACE, width=3),
        ),
        textinfo="percent",
        textfont=dict(size=11, color=INK),
        hovertemplate="<b>%{label}</b><br>%{value} calls (%{percent})<extra></extra>",
    ))
    fig.add_annotation(
        text=f"<b>45</b>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=22, color=INK, family="JetBrains Mono"),
    )
    apply_theme(fig, height=300)
    fig.update_layout(
        title=dict(
            text="<span style='font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:#787774'>TRANSFER TYPE</span><br><b style='font-size:14px;color:#18181B'>What triggered the transfer</b>",
            x=0, xanchor="left", y=1, yanchor="top",
            pad=dict(t=14, l=8),
            font=dict(family="Plus Jakarta Sans"),
        ),
        showlegend=True,
        legend=dict(
            orientation="v", x=1.0, y=0.5, xanchor="left",
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=MUTED, size=10),
        ),
    )
    st.plotly_chart(fig, use_container_width=True, config=CHART_CFG)

with chart_r:
    state_counts = df["State Label"].value_counts().reset_index()
    state_counts.columns = ["State", "Count"]
    state_counts = state_counts.sort_values("Count", ascending=True)

    max_state = state_counts["Count"].max()
    fig = go.Figure(go.Bar(
        x=state_counts["Count"],
        y=state_counts["State"],
        orientation="h",
        marker=dict(
            color=[ACCENT if c == max_state else C_NEUTRAL
                   for c in state_counts["Count"]],
            line=dict(width=0),
        ),
        text=state_counts["Count"],
        textposition="outside",
        textfont=dict(family="JetBrains Mono", size=12, color=INK),
        textangle=-90,
        hovertemplate="<b>%{y}</b><br>%{x} calls<extra></extra>",
    ))
    fig.update_xaxes(title=None, showgrid=False, showticklabels=False,
                     range=[0, max_state * 1.28])
    fig.update_yaxes(title=None)
    apply_theme(fig, height=300)
    fig.update_layout(margin=dict(l=8, r=32, t=74, b=12))
    fig.update_layout(title=dict(
        text="<span style='font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:#787774'>DROPOUT POINT</span><br><b style='font-size:14px;color:#18181B'>Last system state before transfer</b>",
        x=0, xanchor="left", y=1, yanchor="top",
        pad=dict(t=14, l=8),
        font=dict(family="Plus Jakarta Sans"),
    ))
    st.plotly_chart(fig, use_container_width=True, config=CHART_CFG)

st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ROW 2 — Opportunity tiers + Engagement depth (1.2 : 1 : 1)
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header-group">
  <div class="section-label">Recoverability</div>
  <div class="section-title">Automation opportunity and engagement depth</div>
  <div class="section-desc">How fixable each transfer type is, and how far callers got before leaving.</div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns([1.2, 1, 1])

with c1:
    opp_counts = df["Opportunity"].value_counts().reset_index()
    opp_counts.columns = ["Opportunity", "Count"]
    opp_counts = opp_counts.sort_values("Count", ascending=True)
    max_opp = opp_counts["Count"].max()
    fig = go.Figure(go.Bar(
        x=opp_counts["Count"],
        y=opp_counts["Opportunity"],
        orientation="h",
        marker=dict(
            color=[OPP_COLORS.get(o, "#ccc") for o in opp_counts["Opportunity"]],
            line=dict(width=0),
        ),
        text=opp_counts["Count"],
        textposition="inside",
        textfont=dict(family="JetBrains Mono", size=11, color="#FFFFFF"),
        insidetextanchor="end",
        hovertemplate="<b>%{y}</b><br>%{x} calls<extra></extra>",
    ))
    fig.update_xaxes(title=None, showgrid=False, showticklabels=False,
                     range=[0, max_opp * 1.08])
    fig.update_yaxes(title=None)
    apply_theme(fig, height=280)
    fig.update_layout(title=dict(
        text="<span style='font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:#787774'>OPPORTUNITY TIER</span><br><b style='font-size:14px;color:#18181B'>Calls by recoverability</b>",
        x=0, xanchor="left", y=1, yanchor="top",
        pad=dict(t=14, l=8),
        font=dict(family="Plus Jakarta Sans"),
    ))
    st.plotly_chart(fig, use_container_width=True, config=CHART_CFG)

SHORT = {"PREFERS HUMAN": "Prefers Human", "REQUESTED TRANSFER": "Requested", "TRANSFER": "System"}

with c2:
    fig = go.Figure()
    for tt, color in TYPE_COLORS.items():
        subset = df[df["Task Type"] == tt]["user_turns"]
        fig.add_trace(go.Box(
            y=subset, name=SHORT.get(tt, tt),
            marker=dict(color=color, size=4),
            line=dict(color=color, width=1.5),
            fillcolor=hex_to_rgba(color, 0.13),
            boxpoints="all",
            jitter=0.4,
            pointpos=0,
            hovertemplate=f"<b>{tt}</b><br>%{{y}} turns<extra></extra>",
        ))
    apply_theme(fig, height=280)
    fig.update_yaxes(title="Turns", showgrid=True)
    fig.update_layout(
        showlegend=False,
        title=dict(
            text="<span style='font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:#787774'>DIALOGUE TURNS</span><br><b style='font-size:14px;color:#18181B'>User turns by transfer type</b>",
            x=0, xanchor="left", y=1, yanchor="top",
            pad=dict(t=14, l=8),
            font=dict(family="Plus Jakarta Sans"),
        ),
    )
    st.plotly_chart(fig, use_container_width=True, config=CHART_CFG)

with c3:
    fig = go.Figure()
    for tt, color in TYPE_COLORS.items():
        subset = df[df["Task Type"] == tt]
        fig.add_trace(go.Violin(
            y=subset["Length (s)"],
            name=SHORT.get(tt, tt),
            box_visible=True,
            meanline_visible=True,
            fillcolor=hex_to_rgba(color, 0.2),
            line_color=color,
            line_width=1.5,
            hovertemplate=f"<b>{tt}</b><br>%{{y}}s<extra></extra>",
        ))
    apply_theme(fig, height=280)
    fig.update_yaxes(title="Seconds", showgrid=True)
    fig.update_layout(
        showlegend=False,
        title=dict(
            text="<span style='font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:#787774'>CALL LENGTH</span><br><b style='font-size:14px;color:#18181B'>Handle time distribution</b>",
            x=0, xanchor="left", y=1, yanchor="top",
            pad=dict(t=14, l=8),
            font=dict(family="Plus Jakarta Sans"),
        ),
    )
    st.plotly_chart(fig, use_container_width=True, config=CHART_CFG)




# ═══════════════════════════════════════════════════════════════════════════════
# ROW 3 — Transcript Explorer
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header-group">
  <div class="section-label">Evidence</div>
  <div class="section-title">Transcript explorer</div>
  <div class="section-desc">Filter calls and review raw transcripts. Useful for validating recommendations against real evidence.</div>
</div>
""", unsafe_allow_html=True)

f1, f2, f3 = st.columns([1.2, 1.2, 1])

with f1:
    type_filter = st.multiselect(
        "Transfer type",
        df["Task Type"].unique(),
        default=list(df["Task Type"].unique()),
    )
with f2:
    opp_filter = st.multiselect(
        "Opportunity tier",
        df["Opportunity"].unique(),
        default=list(df["Opportunity"].unique()),
    )
with f3:
    max_len = int(df["Length (s)"].max())
    len_range = st.slider("Max call length (s)", 0, max_len, max_len)

filtered = df[
    df["Task Type"].isin(type_filter) &
    df["Opportunity"].isin(opp_filter) &
    (df["Length (s)"] <= len_range)
].reset_index(drop=True)

st.markdown(
    f"<p style='font-size:11px; color:{MUTED}; font-family:JetBrains Mono,monospace; "
    f"margin-bottom:12px;'>Showing {len(filtered)} of {total} calls</p>",
    unsafe_allow_html=True,
)

opp_badge_map = {
    "High — System Gap":  "badge-high",
    "High — STT / NLP":  "badge-high",
    "Medium":             "badge-medium",
    "Low":                "badge-low",
}

for _, row in filtered.iterrows():
    badge_cls  = opp_badge_map.get(row["Opportunity"], "badge-low")
    type_color = TYPE_COLORS.get(row["Task Type"], "#ccc")

    raw = str(row["Transcript"])
    rendered = re.sub(r"ASSORT:", "<span class='tx-assort'>ASSORT:</span>", raw)
    rendered = re.sub(r"USER:",   "<span class='tx-user'>USER:</span>", rendered)
    rendered = rendered.replace("\n", "<br>")

    with st.expander(
        f"{row['Task Type']}  ·  {row['State Label']}  ·  "
        f"{int(row['Length (s)'])}s  ·  {row['user_turns']} user turns"
    ):
        st.markdown(f"""
        <div class="tx-meta">
          <span class="{badge_cls}">{row['Opportunity']}</span>
          <span class="badge-type">{row['Task Type']}</span>
          <span style="font-family:'JetBrains Mono',monospace; font-size:10px; color:{MUTED};">
            {row['Last state']}
          </span>
        </div>
        <div class="tx-content">{rendered}</div>
        """, unsafe_allow_html=True)
