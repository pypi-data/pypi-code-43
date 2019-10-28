import numpy as np
import plotly.graph_objects as go


class Canvas3D:
    def __init__(self):
        self._fig = go.Figure(
            layout=dict(
                scene=dict(
                    xaxis=dict(
                        showspikes=False,
                    ),
                    yaxis=dict(
                        showspikes=False,
                    ),
                    zaxis=dict(
                        showspikes=False,
                    ),
                ),
                hovermode=False,
            ),
        )
        self._min = np.array([float('inf')] * 3, float)
        self._max = np.array([float('-inf')] * 3, float)

    def _enlarge_bbox(self, points):
        for point in points:
            self._min = np.minimum(point, self._min)
            self._max = np.maximum(point, self._max)

    def dot(self, p, color='black', text=None):
        x, y, z = np.array([p], float).T

        self._fig.add_scatter3d(
            x=x,
            y=y,
            z=z,
            mode='markers',
            name=text,
            marker=dict(
                color=color,
            ),
        )

        self._enlarge_bbox([p])

    def line(self, a, b, color='black', text=None):
        x, y, z = np.array([a, b], float).T

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

        self._enlarge_bbox([a, b])

    def support(self, p):
        p = np.asarray(p, float)
        a = np.subtract(p, [0.6, 0.6, 1])
        b = np.subtract(p, [0.6, -0.6, 1])
        c = np.subtract(p, [-0.6, -0.6, 1])
        d = np.subtract(p, [-0.6, 0.6, 1])

        x, y, z = np.array([p, a, b, c, d]).T

        self._fig.add_mesh3d(
            x=x,
            y=y,
            z=z,
            i=[0, 0, 0, 0, 1, 3],
            j=[1, 2, 3, 4, 2, 4],
            k=[2, 3, 4, 1, 4, 2],
            color='red',
            opacity=0.50,
            hoverinfo='skip',
        )

        self._enlarge_bbox([p, a, b, c, d])

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
