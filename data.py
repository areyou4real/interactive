from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional, Dict, List


@dataclass(frozen=True)
class Node:
    id: str
    label: str
    kind: str  # "project" | "tool" | "experience" | "outcome" | "leadership" | "tag"
    subtitle: str = ""
    metric: str = ""
    start: Optional[date] = None
    end: Optional[date] = None
    url: Optional[str] = None


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    rel: str
    weight: float = 1.0


def build_resume_graph() -> tuple[Dict[str, Node], List[Edge]]:
    # Dates you specified for projects
    D_SMPBED = date(2023, 10, 1)
    D_DISEASE = date(2024, 2, 1)
    D_VISION = date(2024, 9, 1)
    D_GENOMESAGE = date(2025, 3, 1)
    D_CATERING = date(2025, 11, 1)

    # Experiences
    BARNES_START = date(2025, 11, 1)
    VENTURA_START = date(2025, 5, 1)
    VENTURA_END = date(2025, 8, 31)

    nodes: Dict[str, Node] = {}

    def add(n: Node):
        nodes[n.id] = n

    # -----------------------------
    # Projects (end=None so they persist in cumulative timeline)
    # -----------------------------
    add(Node(
        id="proj_smpbed",
        label="SMPBED",
        kind="project",
        subtitle="S&P 500 next-day direction from macro signals",
        metric="2010–2024 macro coverage • AUC vs always-up baseline",
        start=D_SMPBED,
        end=None,
    ))

    add(Node(
        id="proj_disease",
        label="Disease Simulation",
        kind="project",
        subtitle="SIR simulation on synthetic graphs + interventions",
        metric="50k nodes • 4 strategies • 22% peak infection reduction",
        start=D_DISEASE,
        end=None,
    ))

    add(Node(
        id="proj_vision",
        label="Vision",
        kind="project",
        subtitle="Low-latency Streamlit image classifier",
        metric="10 classes • 45ms latency • 6× faster GPU vs CPU",
        start=D_VISION,
        end=None,
    ))

    add(Node(
        id="proj_genomesage",
        label="GenomeSage",
        kind="project",
        subtitle="DNA sequence modeling + error-slice dashboards",
        metric="0.91 AUC • 120k sequences • 35% faster interpretation",
        start=D_GENOMESAGE,
        end=None,
    ))

    add(Node(
        id="proj_catering",
        label="Catering Leftovers App",
        kind="project",
        subtitle="Campus app to surface leftover food drops + notifications",
        metric="Product build • Firebase + web/app stack",
        start=D_CATERING,
        end=None,
    ))

    # -----------------------------
    # Experiences (end kept for display, but timeline filter will be cumulative)
    # -----------------------------
    add(Node(
        id="exp_barnes",
        label="Barnes Research Group",
        kind="experience",
        subtitle="Undergraduate Researcher",
        metric="150GB+ climate pipelines • +14% vs baseline • 8 model variants • regime-sliced error analysis",
        start=BARNES_START,
        end=None
    ))

    add(Node(
        id="exp_ventura",
        label="Ventura Securities",
        kind="experience",
        subtitle="Data Analysis Intern",
        metric="20+ briefs • $10–15M allocation discussions • DCF/comps/sensitivity • 25+ companies",
        start=VENTURA_START,
        end=VENTURA_END
    ))

    # -----------------------------
    # Leadership (optional layer)
    # -----------------------------
    add(Node(
        id="lead_oxmun",
        label="Oxford MUN",
        kind="leadership",
        subtitle="Director",
        metric="Led 2,000+ delegates"
    ))
    add(Node(
        id="lead_pitun",
        label="PIT-UN",
        kind="leadership",
        subtitle="Logistics Lead",
        metric="Cross-sector convening"
    ))
    add(Node(
        id="lead_fysop",
        label="FYSOP Mentor",
        kind="leadership",
        subtitle="Mentor",
        metric="Nonprofit team scoping + timelines"
    ))

    # -----------------------------
    # Tools
    # -----------------------------
    tools = [
        ("tool_python", "Python"),
        ("tool_pytorch", "PyTorch"),
        ("tool_tensorflow", "TensorFlow"),
        ("tool_rust", "Rust"),
        ("tool_r", "R"),
        ("tool_sql", "SQL"),
        ("tool_tableau", "Tableau"),
        ("tool_streamlit", "Streamlit"),
        ("tool_docker", "Docker"),
        ("tool_git", "Git/GitHub"),
        ("tool_aws", "AWS"),
        ("tool_firebase", "Firebase"),
        ("tool_mongo", "MongoDB"),
        ("tool_javascript", "JavaScript"),
        ("tool_rest", "REST APIs"),
        ("tool_html", "HTML5"),
    ]
    for tid, name in tools:
        add(Node(id=tid, label=name, kind="tool"))

    # -----------------------------
    # Tags
    # -----------------------------
    tags = [
        ("tag_bio", "Bio"),
        ("tag_ml", "ML"),
        ("tag_finance", "Finance"),
        ("tag_data", "Data"),
        ("tag_systems", "Systems"),
        ("tag_product", "Product"),
        ("tag_research", "Research"),
        ("tag_viz", "Viz"),
        ("tag_deploy", "Deployment"),
    ]
    for tid, name in tags:
        add(Node(id=tid, label=name, kind="tag"))

    # -----------------------------
    # Outcomes
    # -----------------------------
    outcomes = [
        ("out_auc091", "0.91 AUC"),
        ("out_35pct", "35% faster interpretation"),
        ("out_45ms", "45 ms latency"),
        ("out_6x", "6× GPU speedup"),
        ("out_22pct", "22% peak reduction"),
        ("out_14pct", "+14% vs baseline"),
        ("out_150gb", "150 GB processed"),
    ]
    for oid, label in outcomes:
        add(Node(id=oid, label=label, kind="outcome"))

    edges: List[Edge] = []

    def link(a: str, b: str, rel: str, w: float = 1.0):
        edges.append(Edge(source=a, target=b, rel=rel, weight=w))

    # Project ↔ tools
    link("proj_genomesage", "tool_pytorch", "uses")
    link("proj_genomesage", "tool_python", "uses")
    link("proj_genomesage", "tool_tableau", "uses")

    link("proj_smpbed", "tool_python", "uses")
    link("proj_smpbed", "tool_tableau", "uses")
    link("proj_smpbed", "tool_sql", "uses")

    link("proj_disease", "tool_rust", "uses")
    link("proj_disease", "tool_git", "uses")

    link("proj_vision", "tool_tensorflow", "uses")
    link("proj_vision", "tool_streamlit", "uses")
    link("proj_vision", "tool_docker", "uses")
    link("proj_vision", "tool_git", "uses")

    link("proj_catering", "tool_firebase", "uses")
    link("proj_catering", "tool_javascript", "uses")
    link("proj_catering", "tool_rest", "uses")
    link("proj_catering", "tool_git", "uses")
    link("proj_catering", "tool_html", "uses")
    link("proj_catering", "tool_mongo", "uses")

    # Tags
    link("proj_genomesage", "tag_bio", "tagged")
    link("proj_genomesage", "tag_ml", "tagged")
    link("proj_genomesage", "tag_viz", "tagged")

    link("proj_smpbed", "tag_finance", "tagged")
    link("proj_smpbed", "tag_data", "tagged")
    link("proj_smpbed", "tag_viz", "tagged")

    link("proj_disease", "tag_systems", "tagged")
    link("proj_disease", "tag_research", "tagged")

    link("proj_vision", "tag_product", "tagged")
    link("proj_vision", "tag_ml", "tagged")
    link("proj_vision", "tag_deploy", "tagged")

    link("proj_catering", "tag_product", "tagged")
    link("proj_catering", "tag_systems", "tagged")
    link("proj_catering", "tag_deploy", "tagged")

    # Outcomes
    link("proj_genomesage", "out_auc091", "achieves", 2.0)
    link("proj_genomesage", "out_35pct", "achieves", 1.5)
    link("proj_vision", "out_45ms", "achieves", 2.0)
    link("proj_vision", "out_6x", "achieves", 1.8)
    link("proj_disease", "out_22pct", "achieves", 1.8)

    # Experiences ↔ outcomes/tools
    link("exp_barnes", "out_14pct", "achieves", 1.6)
    link("exp_barnes", "out_150gb", "achieves", 1.6)
    link("exp_barnes", "tool_pytorch", "uses")
    link("exp_barnes", "tool_python", "uses")

    link("exp_ventura", "tag_finance", "focuses")
    link("exp_ventura", "tool_python", "uses")
    link("exp_ventura", "tool_sql", "uses")

    # Story links
    link("exp_barnes", "proj_genomesage", "related")
    link("exp_ventura", "proj_smpbed", "related")

    # Leadership ↔ tags
    link("lead_oxmun", "tag_research", "organizes")
    link("lead_pitun", "tag_data", "coordinates")
    link("lead_fysop", "tag_finance", "supports")

      # DEBUG: validate edges
    node_ids = set(nodes.keys())
    bad = []
    for e in edges:
        if e.source not in node_ids or e.target not in node_ids:
            bad.append((e.source, e.target, e.rel))
    print("N nodes:", len(node_ids))
    print("N edges:", len(edges))
    print("Bad edges:", len(bad))
    print("Examples:", bad[:10])

    return nodes, edges
