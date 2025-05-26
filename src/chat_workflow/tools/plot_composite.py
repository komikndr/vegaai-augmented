from langchain.tools import tool
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import chainlit as cl


@tool
async def plot_composite_figure(title: str, layout: list) -> str:
    """
    Create a custom grid layout of plots.

    Args:
        title: Title of the overall figure.
        layout: List of rows, each row is a list of plot components (dicts).
                Each component must include a "type" and required data.

                Optional keys:
                - "rowspan": int, number of rows to span vertically. Based on the number of row and its max row
                - "colspan": int, number of columns to span horizontally. Based on the number of col and its max col
                This is if users want to certain subplot to occupied entire or partial width/height
                of the charts canvas. Such as "Make the table to span entire row, or span entire height"

                Example:
                [
                    [  # Row 1
                        {"type": "bar", "x": [...], "y": [...], "name": "Bar", "colspan": 2},
                        {"type": "pie", "labels": [...], "values": [...], "name": "Pie"}
                    ],
                    [  # Row 2
                        {"type": "scatter", "x": [...], "y": [...], "name": "Scatter", "rowspan": 2},
                        {"type": "table", "columns": [...], "data": [...], "name": "Table"}
                    ],
                    [  # Row 3
                        # Empty cell next to scatter (which spans 2 rows)
                    ]
                ]

    Returns:
        Confirmation message.
    """

    rows = len(layout)
    cols = max(len(r) for r in layout)

    specs = [[{} for _ in range(cols)] for _ in range(rows)]
    subplot_titles = []

    # Track occupied cells for rowspan/colspan skipping
    occupied = [[False] * cols for _ in range(rows)]

    traces = []

    for r_idx, row in enumerate(layout):
        c_idx = 0
        for comp in row:
            # Skip to next available column
            while c_idx < cols and occupied[r_idx][c_idx]:
                c_idx += 1
            if c_idx >= cols:
                break

            t = comp["type"]
            name = comp.get("name", t.capitalize())
            rs = comp.get("rowspan", 1)
            cs = comp.get("colspan", 1)

            for dr in range(rs):
                for dc in range(cs):
                    if r_idx + dr < rows and c_idx + dc < cols:
                        occupied[r_idx + dr][c_idx + dc] = True

            subplot_titles.append(name)
            specs[r_idx][c_idx] = {"type": "domain" if t in {"pie", "table"} else "xy",
                                   "rowspan": rs,
                                   "colspan": cs}
            traces.append((r_idx + 1, c_idx + 1, comp))
            c_idx += 1

    fig = make_subplots(
        rows=rows,
        cols=cols,
        specs=specs,
        subplot_titles=subplot_titles,
        vertical_spacing=0.08,
        horizontal_spacing=0.05
    )

    for r, c, comp in traces:
        t = comp["type"]
        name = comp.get("name", t.capitalize())

        if t == "bar":
            fig.add_trace(go.Bar(x=comp["x"], y=comp["y"], name=name, showlegend=False), row=r, col=c)
        elif t == "line":
            fig.add_trace(go.Scatter(x=comp["x"], y=comp["y"], mode='lines+markers', name=name, showlegend=False), row=r, col=c)
        elif t == "scatter":
            fig.add_trace(go.Scatter(x=comp["x"], y=comp["y"], mode='markers', name=name, showlegend=False), row=r, col=c)
        elif t == "bubble":
            fig.add_trace(go.Scatter(
                x=comp["x"], y=comp["y"], mode='markers',
                marker=dict(size=comp["size"], opacity=0.6),
                name=name, showlegend=False
            ), row=r, col=c)
        elif t == "pie":
            fig.add_trace(go.Pie(labels=comp["labels"], values=comp["values"], name=name, showlegend=False), row=r, col=c)
        elif t == "table":
            transposed_data = list(map(list, zip(*comp["data"])))
            fig.add_trace(go.Table(
                header=dict(values=comp["columns"]),
                cells=dict(values=transposed_data),
                name=name
            ), row=r, col=c)
        else:
            return f"Unsupported type: {t}"

    fig.update_layout(
        title_text=title,
        width=960,
        margin=dict(l=40, r=40, t=60, b=40),
        template="presentation",
        showlegend=False
    )

    elements = [cl.Plotly(name=title, figure=fig, display="side", size="large")]
    await cl.ElementSidebar.set_elements([])
    await cl.Message(content=f"Chart: **{title}**", elements=elements).send()
    await cl.ElementSidebar.set_elements(elements)
    return f"Composite layout '{title}' sent."

