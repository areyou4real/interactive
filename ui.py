# ui.py
from __future__ import annotations
import streamlit as st


def inject_global_ui() -> None:
    st.markdown(
        """
<style>
/* ---------- Base ---------- */
:root{
  --bg0:#070A12;
  --bg1:#0B1220;
  --card: rgba(255,255,255,.06);
  --card2: rgba(255,255,255,.085);
  --stroke: rgba(255,255,255,.10);
  --text: rgba(255,255,255,.92);
  --muted: rgba(255,255,255,.68);
  --muted2: rgba(255,255,255,.55);
  --shadow: 0 16px 60px rgba(0,0,0,.35);
  --shadow2: 0 10px 30px rgba(0,0,0,.25);
  --r: 18px;
  --r2: 14px;
  --accentA: #7C3AED; /* purple */
  --accentB: #06B6D4; /* cyan */
  --accentC: #22C55E; /* green */
  --accentD: #F59E0B; /* amber */
}

/* Hide default Streamlit chrome (keep sidebar) */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* App background */
.stApp{
  background: radial-gradient(1200px 800px at 15% 10%, rgba(124,58,237,.35), transparent 55%),
              radial-gradient(1000px 700px at 85% 20%, rgba(6,182,212,.28), transparent 55%),
              radial-gradient(900px 650px at 65% 85%, rgba(34,197,94,.18), transparent 50%),
              linear-gradient(180deg, var(--bg0), var(--bg1));
  color: var(--text);
}

/* subtle animated noise overlay */
.stApp:before{
  content:"";
  position: fixed;
  inset: 0;
  pointer-events:none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='160' height='160' filter='url(%23n)' opacity='.15'/%3E%3C/svg%3E");
  opacity: .14;
  mix-blend-mode: overlay;
  animation: floatNoise 10s ease-in-out infinite;
}
@keyframes floatNoise{
  0%,100%{transform: translateY(0px);}
  50%{transform: translateY(10px);}
}

/* Typography */
html, body, [class*="css"]  { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Inter, Roboto, Arial; }
h1,h2,h3{ letter-spacing: -0.02em; }
p,li{ color: var(--muted); }

/* ---------- Components ---------- */
.hero{
  border: 1px solid var(--stroke);
  background: linear-gradient(135deg, rgba(124,58,237,.22), rgba(6,182,212,.14));
  border-radius: calc(var(--r) + 6px);
  box-shadow: var(--shadow);
  padding: 22px 22px;
  position: relative;
  overflow:hidden;
  animation: popIn .55s ease-out both;
}
.hero:after{
  content:"";
  position:absolute;
  width: 380px;
  height: 380px;
  right:-120px;
  top:-160px;
  border-radius: 999px;
  background: radial-gradient(circle at 30% 30%, rgba(255,255,255,.18), transparent 55%);
  filter: blur(0px);
  animation: orb 7s ease-in-out infinite;
}
@keyframes orb{
  0%,100%{ transform: translate(0,0) scale(1); opacity:.9;}
  50%{ transform: translate(-30px, 25px) scale(1.07); opacity:.75;}
}
@keyframes popIn{
  from{ transform: translateY(10px); opacity: 0;}
  to{ transform: translateY(0); opacity: 1;}
}

.card{
  border: 1px solid var(--stroke);
  background: var(--card);
  border-radius: var(--r);
  box-shadow: var(--shadow2);
  padding: 16px 16px;
  animation: fadeUp .45s ease-out both;
}
.card:hover{ background: var(--card2); transform: translateY(-2px); transition: .18s ease; }

@keyframes fadeUp{
  from{ transform: translateY(8px); opacity: 0;}
  to{ transform: translateY(0); opacity: 1;}
}

.badge{
  display:inline-flex;
  gap:8px;
  align-items:center;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid var(--stroke);
  background: rgba(255,255,255,.06);
  color: rgba(255,255,255,.86);
  font-size: 12px;
  line-height: 1;
}
.chip{
  display:inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,.12);
  background: rgba(0,0,0,.10);
  color: rgba(255,255,255,.78);
  font-size: 12px;
  margin: 2px 6px 2px 0;
}

.kpi{
  display:flex;
  flex-direction:column;
  border: 1px solid var(--stroke);
  background: rgba(255,255,255,.05);
  border-radius: var(--r2);
  padding: 12px 12px;
}
.kpi .label{ font-size: 12px; color: var(--muted2); }
.kpi .value{ font-size: 18px; color: rgba(255,255,255,.92); font-weight: 650; letter-spacing:-.02em; }

.hr{
  height:1px;
  background: rgba(255,255,255,.10);
  margin: 12px 0;
}

/* Sidebar polish */
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.03));
  border-right: 1px solid rgba(255,255,255,.10);
}
section[data-testid="stSidebar"] *{
  color: rgba(255,255,255,.88) !important;
}

/* Buttons */
.stButton>button{
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,.14);
  background: linear-gradient(135deg, rgba(124,58,237,.55), rgba(6,182,212,.35));
  color: white;
  box-shadow: 0 12px 30px rgba(0,0,0,.25);
}
.stButton>button:hover{
  transform: translateY(-1px);
  transition: .16s ease;
}

/* Reduce Plotly modebar clutter feel */
.js-plotly-plot .plotly .modebar{
  background: rgba(0,0,0,.15) !important;
  border-radius: 12px !important;
  padding: 4px 6px !important;
}

/* Make inputs feel consistent */
div[data-baseweb="input"] input,
div[data-baseweb="select"] > div{
  border-radius: 14px !important;
}

/* ---------- Responsive ---------- */
@media(max-width: 900px){
  .hero{ padding: 18px; }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, badges: list[str]) -> None:
    badge_html = "".join([f"<span class='badge'>⚡ {b}</span>" for b in badges])
    st.markdown(
        f"""
<div class="hero">
  <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center; margin-bottom:10px;">
    {badge_html}
  </div>
  <div style="font-size:34px; font-weight:800; line-height:1.05; color: rgba(255,255,255,.95);">
    {title}
  </div>
  <div style="margin-top:10px; font-size:14px; color: rgba(255,255,255,.72); max-width: 70ch;">
    {subtitle}
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def card_open() -> None:
    st.markdown("<div class='card'>", unsafe_allow_html=True)


def card_close() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def kpi_row(items: list[tuple[str, str]]) -> None:
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        with col:
            st.markdown(
                f"""
<div class="kpi">
  <div class="label">{label}</div>
  <div class="value">{value}</div>
</div>
                """,
                unsafe_allow_html=True,
            )


def chips(labels: list[str]) -> None:
    st.markdown("".join([f"<span class='chip'>{x}</span>" for x in labels]), unsafe_allow_html=True)
