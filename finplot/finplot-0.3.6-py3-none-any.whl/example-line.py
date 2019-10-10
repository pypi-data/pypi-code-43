#!/usr/bin/env python3

import finplot as fplt
import numpy as np

dates = pd.date_range('01:00', '21:30', freq='1min')
prices = pd.Series(np.random.random(len(dates))).rolling(30).mean() + 4
fplt.y_label_width = 230
ax,ax2 = fplt.create_plot('Crap stuff', rows=2, maximize=False)
fplt.plot(dates, prices, ax=ax)
fplt.plot(dates, np.random.random(len(dates))*3e5, ax=ax2)
fplt.show()
