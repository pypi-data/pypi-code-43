import numpy as np
import plotly.graph_objects as go


class Canvas3D:
    def __init__(self):
        self._fig = go.Figure()
        self._min = np.array([float('inf')] * 3, float)
        self._max = np.array([float('-inf')] * 3, float)

    def line(self, a, b, color='black', text=None):
        x, y, z = np.asarray([a, b], float).T

        self._fig.add_scatter3d(
            x=x,
            y=y,
            z=z,
            mode='lines',
            name=text,
            line=dict(
                width=2,
                color=color,
            ),
        )

        box_min = np.minimum(a, b)
        box_max = np.maximum(a, b)

        self._min = np.minimum(box_min, self._min)
        self._max = np.maximum(box_max, self._max)

    def show(self):
        mid = (self._max + self._min) * 0.5
        size = max(self._max - self._min)

        box_min = mid - size / 2
        box_max = mid + size / 2

        self._fig.update_layout(
            scene=dict(
                xaxis=dict(range=[box_min[0], box_max[0]]),
                yaxis=dict(range=[box_min[1], box_max[1]]),
                zaxis=dict(range=[box_min[2], box_max[2]]),
            ),
        )

        self._fig.show()
