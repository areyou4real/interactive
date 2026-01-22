from __future__ import annotations
from typing import Dict, List, Optional, Set, Tuple
import networkx as nx
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data import Node, Edge


KIND_STYLES = {
    "project":   {"symbol": "circle", "size": 18},
    "tool":      {"symbol": "square", "size": 13},
    "experience":{"symbol": "diamond", "size": 16},
    "leadership":{"symbol": "triangle-up", "size": 15},
    "outcome":   {"symbol": "hexagon", "size": 14},
    "tag":       {"symbol": "star", "size": 12},
    "skill":     {"symbol": "square-open", "size": 12},
}

KIND_COLORS = {
    "project": "#2563eb",
    "tool": "#06b6d4",
    "experience": "#7c3aed",
    "leadership": "#f59e0b",
    "outcome": "#22c55e",
    "tag": "#94a3b8",
    "skill": "#94a3b8",
}

EDGE_COLOR = "rgba(148,163,184,0.78)"
EDGE_WIDTH = 2.2


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


def build_nx_graph(nodes: Dict[str, Node], edges: List[Edge], allowed_nodes: Optional[Set[str]] = None) -> nx.Graph:
    G = nx.Graph()
    for nid, n in nodes.items():
        if allowed_nodes is not None and nid not in allowed_nodes:
            continue
        data = dict(n.__dict__)
        data["kind"] = norm_kind(data.get("kind", ""))
        G.add_node(nid, **data)

    for e in edges:
        if allowed_nodes is not None and (e.source not in allowed_nodes or e.target not in allowed_nodes):
            continue
        if e.source in G and e.target in G:
            G.add_edge(e.source, e.target, rel=e.rel, weight=e.weight)
    return G


def _layered_positions(
    G: nx.Graph,
    layer_kinds: List[str],
    layer_gap: float = 2.2,
    y_spread: float = 3.0,
) -> Dict[str, Tuple[float, float]]:
    layers: List[List[str]] = []
    for k in layer_kinds:
        layers.append([nid for nid, data in G.nodes(data=True) if data.get("kind") == k])

    pos: Dict[str, Tuple[float, float]] = {}
    L = len(layers)
    x0 = -((L - 1) * layer_gap) / 2.0

    for i, layer_nodes in enumerate(layers):
        x = x0 + i * layer_gap
        if not layer_nodes:
            continue

        layer_nodes = sorted(
            layer_nodes,
            key=lambda n: (G.degree(n), str(G.nodes[n].get("label", n)).lower()),
            reverse=True
        )

        m = len(layer_nodes)
        ys = [0.0] if m == 1 else [y_spread - (2 * y_spread) * (j / (m - 1)) for j in range(m)]

        for j, nid in enumerate(layer_nodes):
            jitter = 0.06 * (1 if j % 2 == 0 else -1)
            pos[nid] = (x + jitter, ys[j])

    return pos


def compute_positions(G: nx.Graph, layer_kinds: List[str], layer_gap: float, y_spread: float) -> Dict[str, Tuple[float, float]]:
    if G.number_of_nodes() == 0:
        return {}
    return _layered_positions(G, layer_kinds=layer_kinds, layer_gap=layer_gap, y_spread=y_spread)


# --- KPI helpers: split label/value into separate traces (prevents overlap) ---

def _kpi_label_html(text: str) -> str:
    return f"<span style='font-size:12px;opacity:.75'>{text}</span>"

def _kpi_value_html(value: int | str) -> str:
    return f"<span style='font-size:34px'><b>{value}</b></span>"


def plot_graph_timeline(
    G: nx.Graph,
    nodes: Dict[str, Node],
    dates: List,
    visible_nodes_by_date: List[Set[str]],
    enabled_kinds: Optional[Set[str]] = None,
    selected: Optional[str] = None,
    title: str = "",
    layer_kinds: Optional[List[str]] = None,
    layer_gap: float = 2.2,
    y_spread: float = 3.2,
    label_mode: str = "smart",
    frame_ms: int = 560,  # SLOWER default playback
) -> go.Figure:

    if layer_kinds is None:
        layer_kinds = ["experience", "project", "tool", "outcome", "leadership", "tag"]

    layer_kinds = [norm_kind(k) for k in layer_kinds]
    if enabled_kinds is not None:
        enabled_kinds = {norm_kind(k) for k in enabled_kinds}
        layer_kinds = [k for k in layer_kinds if k in enabled_kinds]

    drawable_ids = {nid for nid in G.nodes() if (enabled_kinds is None) or (G.nodes[nid].get("kind") in enabled_kinds)}
    H = G.subgraph(drawable_ids).copy()

    pos = compute_positions(H, layer_kinds=layer_kinds, layer_gap=layer_gap, y_spread=y_spread)
    drawable = set(pos.keys())

    total_stops = len(dates)

    neigh: Set[str] = set()
    if selected and selected in H:
        neigh = set(H.neighbors(selected)) | {selected}

    kind_order = ["experience", "project", "tool", "outcome", "leadership", "tag", "skill"]
    kinds_present = []
    for k in kind_order:
        if enabled_kinds is not None and k not in enabled_kinds:
            continue
        if any(H.nodes[n].get("kind") == k for n in H.nodes()):
            kinds_present.append(k)

    kind_nodes: Dict[str, List[str]] = {}
    for k in kinds_present:
        nids = [nid for nid in H.nodes() if H.nodes[nid].get("kind") == k]
        kind_nodes[k] = sorted(nids, key=lambda n: str(H.nodes[n].get("label", n)).lower())

    fig = make_subplots(
        rows=2, cols=3,
        row_heights=[0.22, 0.78],
        vertical_spacing=0.02,
        specs=[
            [{"type": "scatter"}, {"type": "scatter"}, {"type": "scatter"}],
            [{"type": "scatter", "colspan": 3}, None, None],
        ],
    )

    # KPI traces: 6 total (label,value) x 3 tiles
    # indices:
    # 0 label stops, 1 value stops
    # 2 label nodes, 3 value nodes
    # 4 label edges, 5 value edges
    # graph edge trace becomes index 6
    fig.add_trace(go.Scatter(x=[0], y=[0.68], mode="text",
                             text=[_kpi_label_html("Timeline stops")],
                             textposition="middle center", hoverinfo="skip", showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=[0], y=[0.22], mode="text",
                             text=[_kpi_value_html(total_stops)],
                             textposition="middle center", hoverinfo="skip", showlegend=False), row=1, col=1)

    fig.add_trace(go.Scatter(x=[0], y=[0.68], mode="text",
                             text=[_kpi_label_html("Latest visible nodes")],
                             textposition="middle center", hoverinfo="skip", showlegend=False), row=1, col=2)
    fig.add_trace(go.Scatter(x=[0], y=[0.22], mode="text",
                             text=[_kpi_value_html(0)],
                             textposition="middle center", hoverinfo="skip", showlegend=False), row=1, col=2)

    fig.add_trace(go.Scatter(x=[0], y=[0.68], mode="text",
                             text=[_kpi_label_html("Total edges")],
                             textposition="middle center", hoverinfo="skip", showlegend=False), row=1, col=3)
    fig.add_trace(go.Scatter(x=[0], y=[0.22], mode="text",
                             text=[_kpi_value_html(0)],
                             textposition="middle center", hoverinfo="skip", showlegend=False), row=1, col=3)

    for c in (1, 2, 3):
        fig.update_xaxes(visible=False, row=1, col=c, range=[-1, 1])
        fig.update_yaxes(visible=False, row=1, col=c, range=[0, 1])

    # Graph edge trace (index 6) on row 2
    fig.add_trace(go.Scatter(
        x=[], y=[],
        mode="lines",
        line=dict(width=EDGE_WIDTH, color=EDGE_COLOR),
        hoverinfo="none",
        showlegend=False,
    ), row=2, col=1)

    graph_xaxis = fig.data[6].xaxis
    graph_yaxis = fig.data[6].yaxis

    # Node traces start at 7
    node_trace_start = 7
    for k in kinds_present:
        nids = kind_nodes[k]
        xs = [pos[nid][0] for nid in nids]
        ys = [pos[nid][1] for nid in nids]

        hovers = []
        for nid in nids:
            label = H.nodes[nid].get("label", nid)
            subtitle = H.nodes[nid].get("subtitle", "")
            metric = H.nodes[nid].get("metric", "")
            hover = f"<b>{label}</b>"
            if subtitle:
                hover += f"<br>{subtitle}"
            if metric:
                hover += f"<br><span style='color:#94a3b8'>{metric}</span>"
            hovers.append(hover)

        base_size = KIND_STYLES.get(k, {"size": 14})["size"]
        sizes = []
        for nid in nids:
            if selected == nid:
                sizes.append(base_size + 10)
            elif selected is None:
                sizes.append(base_size)
            else:
                sizes.append(base_size + 2 if nid in neigh else max(8, base_size - 3))

        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode="markers+text",
            text=[""] * len(nids),
            textposition="bottom center",
            hovertext=hovers,
            hoverinfo="text",
            customdata=nids,
            marker=dict(
                size=sizes,
                color=KIND_COLORS.get(k, "#2563eb"),
                opacity=[0.0] * len(nids),
                line=dict(width=1.0, color="rgba(15,23,42,0.45)"),
                symbol=KIND_STYLES.get(k, {"symbol": "circle"})["symbol"],
            ),
            name=k.capitalize(),
        ), row=2, col=1)

    def frame_state(visible_raw: Set[str]):
        visible = {nid for nid in visible_raw if nid in drawable}

        ex, ey = [], []
        edge_count = 0
        for u, v in G.edges():
            if u in visible and v in visible and u in drawable and v in drawable:
                x0, y0 = pos[u]
                x1, y1 = pos[v]
                ex += [x0, x1, None]
                ey += [y0, y1, None]
                edge_count += 1

        node_updates = []
        for k in kinds_present:
            nids = kind_nodes[k]
            opacities, labels = [], []
            for nid in nids:
                base_vis = 1.0 if nid in visible else 0.0

                if selected is None:
                    spot = 0.92
                elif selected == nid:
                    spot = 1.0
                else:
                    spot = 0.92 if nid in neigh else 0.18

                opacities.append(base_vis * spot)

                if base_vis <= 0.0 or label_mode == "none":
                    labels.append("")
                elif label_mode == "all":
                    labels.append(H.nodes[nid].get("label", nid))
                else:
                    if selected is not None:
                        labels.append(H.nodes[nid].get("label", nid) if nid in neigh else "")
                    else:
                        labels.append(H.nodes[nid].get("label", nid) if k in {"project", "experience"} else "")

            node_updates.append({"marker": {"opacity": opacities}, "text": labels})

        return visible, ex, ey, edge_count, node_updates

    frames = []
    num_node_traces = len(kinds_present)

    # traces updated per frame:
    # value nodes trace index 3
    # value edges trace index 5
    # graph edge trace index 6
    # node traces start at 7
    trace_indices = [3, 5, 6] + list(range(node_trace_start, node_trace_start + num_node_traces))

    for i, d in enumerate(dates):
        visible, ex, ey, edge_count, node_updates = frame_state(visible_nodes_by_date[i])

        kpi_nodes_val = {"text": [_kpi_value_html(len(visible))]}
        kpi_edges_val = {"text": [_kpi_value_html(edge_count)]}

        edge_update = {"x": ex, "y": ey, "xaxis": graph_xaxis, "yaxis": graph_yaxis}
        frame_data = [kpi_nodes_val, kpi_edges_val, edge_update] + node_updates

        frames.append(go.Frame(name=d.isoformat(), data=frame_data, traces=trace_indices))

    fig.frames = frames

    # Init to last frame
    if frames:
        visible, ex, ey, edge_count, node_updates = frame_state(visible_nodes_by_date[-1])
        fig.data[3].text = [_kpi_value_html(len(visible))]
        fig.data[5].text = [_kpi_value_html(edge_count)]
        fig.data[6].x, fig.data[6].y = ex, ey

        idx = node_trace_start
        for upd in node_updates:
            fig.data[idx].marker.opacity = upd["marker"]["opacity"]
            fig.data[idx].text = upd["text"]
            idx += 1

    steps = []
    for d in dates:
        steps.append(dict(
            method="animate",
            args=[[d.isoformat()],
                  {"frame": {"duration": frame_ms, "redraw": True},
                   "transition": {"duration": int(frame_ms * 0.85), "easing": "cubic-in-out"}}],
            label=d.strftime("%b %Y"),
        ))

    fig.update_layout(
        title=dict(text=title, x=0.01, xanchor="left", font=dict(size=18, color="rgba(255,255,255,.92)")),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.01,
            font=dict(color="rgba(255,255,255,.78)"),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=8, r=8, t=40, b=55),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor="rgba(15,23,42,.92)", font=dict(color="white")),
        font=dict(color="rgba(255,255,255,.85)"),
        updatemenus=[dict(
            type="buttons",
            direction="left",
            x=0.01,
            y=-0.08,
            xanchor="left",
            yanchor="top",
            showactive=False,
            buttons=[
                dict(label="▶ Play", method="animate",
                     args=[None, {"fromcurrent": True,
                                 "frame": {"duration": frame_ms, "redraw": True},
                                 "transition": {"duration": int(frame_ms * 0.85)}}]),
                dict(label="⏸ Pause", method="animate",
                     args=[[None], {"mode": "immediate",
                                   "frame": {"duration": 0, "redraw": True},
                                   "transition": {"duration": 0}}]),
            ],
        )],
        sliders=[dict(
            active=max(0, len(steps) - 1),
            x=0.01,
            y=-0.14,
            xanchor="left",
            yanchor="top",
            len=0.98,
            pad={"t": 0, "b": 0},
            currentvalue={"prefix": "Timeline: ", "font": {"color": "rgba(255,255,255,.78)"}},
            steps=steps,
        )],
    )

    fig.update_xaxes(visible=False, row=2, col=1)
    fig.update_yaxes(visible=False, row=2, col=1)

    return fig


def describe_node(G: nx.Graph, nid: str) -> dict:
    if nid not in G:
        return {}
    data = dict(G.nodes[nid])
    neighbors = []
    for nb in G.neighbors(nid):
        rel = G.edges[nid, nb].get("rel", "")
        neighbors.append((nb, G.nodes[nb].get("label", nb), rel, G.nodes[nb].get("kind", "")))
    neighbors.sort(key=lambda x: (x[3], x[1]))
    data["neighbors"] = neighbors
    return data
