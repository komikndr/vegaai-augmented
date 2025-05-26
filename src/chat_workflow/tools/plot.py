from langchain.tools import tool
import plotly.graph_objects as go
import chainlit as cl
from typing import List


@tool
async def plot_pie_chart(title: str, labels: List[str], values: List[float]) -> str:
    """
    Generates and sends a pie chart message in Chainlit given a title, labels, and values.

    Args:
        title: The title of the pie chart.
        labels: List of names for each slice of the pie chart.
        values: Corresponding values for each slice.

    Returns:
        A confirmation message that the pie chart has been sent.
    """
    if len(labels) != len(values):
        return "Error: Labels and values lists must have the same length."

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.update_layout(title_text=title)

    elements = [cl.Plotly(name="chart", figure=fig, display="inline")]

    await cl.Message(content=f"Here is your pie chart: {title}", elements=elements).send()

    return f"Pie chart '{title}' has been successfully sent."


@tool
async def plot_bar_chart(title: str, labels: List[str], values: List[float]) -> str:
    """
    Generates and sends a bar chart message in Chainlit.
    """
    if len(labels) != len(values):
        return "Error: Labels and values lists must have the same length."

    fig = go.Figure(data=[go.Bar(x=labels, y=values)])
    fig.update_layout(title_text=title)

    elements = [cl.Plotly(name="chart", figure=fig, display="inline")]
    await cl.Message(content=f"Here is your bar chart: {title}", elements=elements).send()

    return f"Bar chart '{title}' has been successfully sent."


@tool
async def plot_line_chart(title: str, labels: List[str], values: List[float]) -> str:
    """
    Generates and sends a line chart message in Chainlit.
    """
    if len(labels) != len(values):
        return "Error: Labels and values lists must have the same length."

    fig = go.Figure(data=[go.Scatter(x=labels, y=values, mode='lines+markers')])
    fig.update_layout(title_text=title)

    elements = [cl.Plotly(name="chart", figure=fig, display="inline")]
    await cl.Message(content=f"Here is your line chart: {title}", elements=elements).send()

    return f"Line chart '{title}' has been successfully sent."


@tool
async def plot_bubble_chart(title: str, labels: List[str], values: List[float], sizes: List[float]) -> str:
    """
    Generates and sends a bubble chart message in Chainlit.
    """
    if len(labels) != len(values) or len(labels) != len(sizes):
        return "Error: Labels, values, and sizes lists must have the same length."

    fig = go.Figure(data=[go.Scatter(
        x=labels, y=values, mode='markers',
        marker=dict(size=sizes, opacity=0.6)
    )])
    fig.update_layout(title_text=title)

    elements = [cl.Plotly(name="chart", figure=fig, display="inline")]
    await cl.Message(content=f"Here is your bubble chart: {title}", elements=elements).send()

    return f"Bubble chart '{title}' has been successfully sent."
