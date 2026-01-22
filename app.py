import streamlit as st
from datetime import date, datetime

from data import build_resume_graph
from graph_utils import build_nx_graph, plot_graph_timeline, describe_node
from ui import inject_global_ui, card_open, card_close

st.set_page_config(page_title="Dheer Doshi — Resume Graph", page_icon="🧭", layout="wide")
inject_global_ui()

# --- Neutral, powerful palette (minimal gradients) + fix sidebar dropdown readability ---
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=DM+Sans:wght@400;500;700&display=swap');

      :root{
        --ink: rgba(226,232,240,0.92);
        --muted: rgba(226,232,240,0.72);
        --muted2: rgba(226,232,240,0.58);
        --stroke: rgba(148,163,184,0.22);
        --panel: rgba(15,23,42,0.58);
        --panel2: rgba(15,23,42,0.40);

        /* Neutral-yet-powerful accents (limited) */
        --accent: rgba(56,189,248,1);   /* cyan */
        --accent2: rgba(167,139,250,1); /* violet */
        --good: rgba(34,197,94,1);      /* green */
        --warn: rgba(251,191,36,1);     /* amber */
      }

      html, body, [class*="css"] {
        font-family: "DM Sans", system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif !important;
        color: var(--ink);
      }
      .block-container { padding-top: 1.2rem; }

      /* Hero: ONE subtle highlight only */
      .hero {
        border: 1px solid var(--stroke);
        background: rgba(15,23,42,0.52);
        border-radius: 20px;
        padding: 18px 18px 14px 18px;
        box-shadow: 0 10px 34px rgba(0,0,0,0.24);
        position: relative;
        overflow: hidden;
      }
      .hero::before{
        content:"";
        position:absolute;
        top:0; left:0; right:0;
        height: 3px;
        background: rgba(56,189,248,0.85); /* simple accent bar, no gradient */
        opacity: 0.9;
      }

      .name {
        font-family: "Space Grotesk", system-ui, sans-serif !important;
        font-weight: 700;
        font-size: 42px;
        line-height: 1.0;
        letter-spacing: -0.03em;
        margin: 2px 0 6px 0;
      }
      .name span{
        color: rgba(226,232,240,0.96);
      }
      .accent-dot{
        display:inline-block;
        width: 10px;
        height: 10px;
        border-radius: 999px;
        background: rgba(56,189,248,0.95);
        margin-left: 10px;
        transform: translateY(-2px);
        box-shadow: 0 0 0 4px rgba(56,189,248,0.10);
      }

      .subline{
        font-size: 14.5px;
        color: var(--muted);
        display:flex;
        flex-wrap: wrap;
        gap: 10px;
        align-items:center;
        margin-top: 6px;
      }
      .sep{ opacity: .55; }

      .edu {
        margin-top: 10px;
        font-size: 15.5px;
        color: rgba(226,232,240,0.86);
        display:flex;
        align-items:center;
        gap: 10px;
      }
      .pill{
        display:inline-flex;
        align-items:center;
        gap: 8px;
        padding: 7px 10px;
        border-radius: 999px;
        border: 1px solid rgba(148,163,184,0.18);
        background: rgba(2,6,23,0.28);
        color: rgba(226,232,240,0.88);
        font-size: 12.5px;
      }
      .pill b{ font-weight: 700; color: rgba(226,232,240,0.94); }
      .pill .icon{ color: rgba(56,189,248,0.95); }

      .section-title{
        font-family: "Space Grotesk", system-ui, sans-serif !important;
        font-size: 14px;
        letter-spacing: .06em;
        text-transform: uppercase;
        color: rgba(226,232,240,0.68);
        margin: 14px 0 8px 0;
      }

      .chips { display:flex; flex-wrap: wrap; gap: 8px; }
      .chip{
        display:inline-flex;
        align-items:center;
        padding: 8px 10px;
        border-radius: 999px;
        border: 1px solid rgba(148,163,184,0.16);
        background: rgba(15,23,42,0.38);
        color: rgba(226,232,240,0.88);
        font-size: 13px;
      }
      .chip.lang{ border-color: rgba(56,189,248,0.22); }
      .chip.lang:nth-child(2){ border-color: rgba(167,139,250,0.22); }
      .chip.lang:nth-child(3){ border-color: rgba(34,197,94,0.18); }

      .hr{
        height:1px;
        margin: 14px 0 14px 0;
        background: rgba(148,163,184,0.18);
        border: 0;
      }

      /* Sidebar dropdown readability */
      div[data-baseweb="select"] > div {
        background: rgba(2,6,23,0.55) !important;
        border: 1px solid rgba(148,163,184,0.28) !important;
        color: rgba(226,232,240,0.95) !important;
      }
      div[data-baseweb="select"] span { color: rgba(226,232,240,0.95) !important; }
      div[role="listbox"] {
        background: rgba(2,6,23,0.92) !important;
        border: 1px solid rgba(148,163,184,0.28) !important;
      }
      div[role="option"] { color: rgba(226,232,240,0.95) !important; }
      div[role="option"]:hover { background: rgba(56,189,248,0.12) !important; }
      div[data-baseweb="select"] input {
        color: rgba(226,232,240,0.95) !important;
        caret-color: rgba(226,232,240,0.95) !important;
      }

      section[data-testid="stSidebar"] h3 {
        font-family: "Space Grotesk", system-ui, sans-serif !important;
        letter-spacing: -0.01em;
      }

      .stCaption { color: var(--muted2) !important; }
      div[data-baseweb="slider"] > div { filter: saturate(1.05); }
    </style>
    """,
    unsafe_allow_html=True,
)

def chips(items, cls=""):
    html = ""
    for it in items:
        html += f"<span class='chip {cls}'>{it}</span>"
    st.markdown(f"<div class='chips'>{html}</div>", unsafe_allow_html=True)

nodes, edges = build_resume_graph()

def norm_kind(k: str) -> str:
    s = (k or "").strip().lower()
    mapping = {
        "projects": "project", "project": "project",
        "tools": "tool", "tool": "tool", "tech": "tool", "technology": "tool", "technologies": "tool",
        "outcome": "outcome", "outcomes": "outcome", "metric": "outcome", "metrics": "outcome", "result": "outcome", "results": "outcome",
        "experience": "experience", "experiences": "experience", "work": "experience", "job": "experience",
        "leadership": "leadership", "leaderships": "leadership",
        "tag": "tag", "tags": "tag", "label": "tag", "labels": "tag",
    }
    return mapping.get(s, s)

def kind_of(nid: str) -> str:
    return norm_kind(getattr(nodes[nid], "kind", ""))

project_ids = [nid for nid in nodes if kind_of(nid) == "project"]
tool_ids = [nid for nid in nodes if kind_of(nid) == "tool"]
outcome_ids = [nid for nid in nodes if kind_of(nid) == "outcome"]
experience_ids = [nid for nid in nodes if kind_of(nid) == "experience"]
leadership_ids = [nid for nid in nodes if kind_of(nid) == "leadership"]
tag_ids = [nid for nid in nodes if kind_of(nid) == "tag"]

# -------------------------
# FRONT PAGE (resume-only)
# -------------------------
NAME = "Dheer Doshi"
LOCATION = "Boston, MA 02215"
PHONE = "(857) 565-6018"
EMAIL = "dheer@bu.edu"
LINKEDIN = "linkedin.com/in/dheer-doshi/"
EDU_LINE = "Boston University — B.S. in Data Science (Graduation: May 2026)"
LANGS = ["English", "Hindi", "Spanish"]

st.markdown(
    f"""
    <div class="hero">
      <div class="name"><span>{NAME}</span><span class="accent-dot"></span></div>
      <div class="subline">
        <span>📍 {LOCATION}</span><span class="sep">•</span>
        <span>📞 {PHONE}</span><span class="sep">•</span>
        <span>✉️ {EMAIL}</span><span class="sep">•</span>
        <span>🔗 {LINKEDIN}</span>
      </div>
      <div class="edu">
        <span class="pill"><span class="icon">🎓</span><b>Education</b></span>
        <span>{EDU_LINE}</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='section-title'>Languages</div>", unsafe_allow_html=True)
chips([f"🌐 {l}" for l in LANGS], cls="lang")
st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

# -------------------------
# Sidebar controls
# -------------------------
with st.sidebar:
    st.subheader("Show layers")
    show_experiences = st.toggle("Experiences", value=True)
    show_projects = st.toggle("Projects", value=True)
    show_tools = st.toggle("Tools", value=True)
    show_outcomes = st.toggle("Outcomes (metrics)", value=True)
    show_leadership = st.toggle("Leadership", value=False)
    show_tags = st.toggle("Tags", value=False)

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    st.subheader("Focus")
    tool_filter = st.selectbox(
        "Filter projects by tool",
        ["All tools"] + [nodes[nid].label for nid in tool_ids],
        index=0,
    )

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    st.subheader("Labels")
    label_mode = st.selectbox("Labels", ["Smart", "All", "None"], index=0)

enabled_kinds = set()
if show_experiences: enabled_kinds.add("experience")
if show_projects: enabled_kinds.add("project")
if show_tools: enabled_kinds.add("tool")
if show_outcomes: enabled_kinds.add("outcome")
if show_leadership: enabled_kinds.add("leadership")
if show_tags: enabled_kinds.add("tag")

G = build_nx_graph(nodes, edges, allowed_nodes=set(nodes.keys()))

def month_floor(d: date) -> date:
    return date(d.year, d.month, 1)

def parse_start(value) -> date | None:
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return date.fromisoformat(value.strip())
        except Exception:
            return None
    return None

def start_of(nid: str) -> date | None:
    return parse_start(getattr(nodes[nid], "start", None))

event_dates = set()
for nid in set(project_ids) | set(experience_ids) | set(leadership_ids):
    s = start_of(nid)
    if s:
        event_dates.add(month_floor(s))
event_dates.add(month_floor(date.today()))
dates = sorted(event_dates)

def visible_by_date(d: date) -> set[str]:
    visible = set()

    if show_projects:
        for nid in project_ids:
            s = start_of(nid)
            if s and s <= d:
                visible.add(nid)

    if show_experiences:
        for nid in experience_ids:
            s = start_of(nid)
            if s and s <= d:
                visible.add(nid)

    if show_leadership:
        visible.update(leadership_ids)

    if show_tags:
        visible.update(tag_ids)

    if tool_filter != "(all tools)":
        tool_id = next((tid for tid in tool_ids if nodes[tid].label == tool_filter), None)
        if tool_id:
            connected_projects = set()
            for nb in G.neighbors(tool_id):
                if nb in project_ids and nb in visible:
                    connected_projects.add(nb)
            visible = (visible - set(project_ids)) | connected_projects | {tool_id}

    expanded = set(visible)
    for nid in list(visible):
        for nb in G.neighbors(nid):
            k = kind_of(nb)
            if k == "tool" and show_tools:
                expanded.add(nb)
            if k == "outcome" and show_outcomes:
                expanded.add(nb)

    return expanded

visible_nodes_by_date = [visible_by_date(d) for d in dates]
latest_visible = visible_nodes_by_date[-1] if visible_nodes_by_date else set()

def display_label(nid: str) -> str:
    k = kind_of(nid)
    prefix = {"experience": "🏢 ", "project": "📁 ", "tool": "🧰 ", "outcome": "📊 ", "leadership": "🎯 ", "tag": "🏷️ "}.get(k, "")
    return prefix + nodes[nid].label

spot_ids = sorted(list(latest_visible), key=lambda x: (kind_of(x), nodes[x].label.lower()))
spot_options = ["None"] + [display_label(nid) for nid in spot_ids]
display_to_id = {display_label(nid): nid for nid in spot_ids}

selected_display = st.sidebar.selectbox("Spotlight", spot_options, index=0)
selected = None if selected_display == "(none)" else display_to_id.get(selected_display)

with st.sidebar:
    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    st.subheader("Spacing")
    layer_gap = st.slider("Column spacing", 1.2, 3.6, 2.2, 0.1)
    y_spread = st.slider("Vertical spacing", 1.6, 6.0, 3.2, 0.1)

left, right = st.columns([0.72, 0.28], gap="large")

with left:
    card_open()

    layer_kinds = ["experience", "project", "tool", "outcome", "leadership", "tag"]

    fig = plot_graph_timeline(
        G=G,
        nodes=nodes,
        dates=dates,
        visible_nodes_by_date=visible_nodes_by_date,
        enabled_kinds=enabled_kinds,
        selected=selected,
        title="",
        layer_kinds=layer_kinds,
        layer_gap=layer_gap,
        y_spread=y_spread,
        label_mode=label_mode,
        frame_ms=560,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})

    card_close()

with right:
    card_open()
    st.subheader("Details")

    if selected is None or selected not in G:
        st.write("Select a node to see its description and connections.")
    else:
        info = describe_node(G, selected)
        st.markdown(f"### {info.get('label','')}")
        if info.get("subtitle"):
            st.caption(info["subtitle"])
        if info.get("metric"):
            st.markdown(f"**Evidence / metrics:** {info['metric']}")

        st.markdown("**Connected to:**")
        for nb_id, nb_label, rel, nb_kind in info.get("neighbors", []):
            nk = norm_kind(nb_kind)
            if nk in enabled_kinds:
                st.write(f"- **{nb_label}** ({nk}) — _{rel}_")

    card_close()
