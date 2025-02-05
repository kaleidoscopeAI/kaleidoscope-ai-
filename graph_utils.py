# graph_utils.py

from plotly.graph_objs import Pie, Heatmap, Bar
from typing import List, Dict

class GraphUtils:
    """
    Utility functions for creating visualizations with Plotly.
    """
    @staticmethod
    def create_pie_chart(labels: List[str], values: List[int], title: str) -> Pie:
        """
        Creates a pie chart visualization.
        """
        return Pie(labels=labels, values=values, hole=0.4, title=title)

    @staticmethod
    def create_heatmap(data: List[float], x_axis: List[int], y_axis: List[str], title: str) -> Heatmap:
        """
        Creates a heatmap visualization.
        """
        return Heatmap(
            z=data,
            x=x_axis,
            y=y_axis,
            colorscale="Viridis",
            name=title
        )

    @staticmethod
    def create_bar_chart(x: List[str], y: List[float], title: str) -> Bar:
        """
        Creates a bar chart visualization.
        """
        return Bar(x=x, y=y, name=title)
