from .._colormaps import _linear3color
from .colors import *
import plotly.graph_objects as go
import plotly.io as pio

import plotly.graph_objects as go

sequential = _linear3color(navRod, navLysBla, navBla)
diverging = _linear3color(navRod, navLysBla, navBla)

sequentialminus = _linear3color(navRod, navLysBla, navBla)

colorscale = [[i/10,color] for i, color in enumerate(sequential)]
colorscale_diverging = [[i/10,color] for i, color in enumerate(sequential)]
colorscale_sequential = [[i/10,color] for i, color in enumerate(sequential)]
colorscale_sequentialminus = [[i/10,color] for i, color in enumerate(sequential)]


discrete = [navRod, navOransje, navLimeGronn, navGronn, navLilla, navDypBla,
            navBla, navLysBla, navMorkGra, navGra40]


plotly_template = pio.templates["plotly_white"]


plotly_template.layout.colorscale = go.layout.Colorscale(
    diverging=diverging,
    sequential=sequential,
    sequentialminus=sequentialminus
)

plotly_template.layout.font = go.layout.Font(
    color = 'black',
    family = "'Open Sans', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'"
)

plotly_template.layout.colorway = (navRod, navOransje, navLimeGronn, navGronn, navLilla, navDypBla, navBla, navLysBla, navMorkGra, navGra40)




