import numpy as np
import streamlit as st
from MegaScreen import MegaScreen
import time

# Interactive Streamlit elements, like these sliders, return their value.
# This gives you an extremely simple interaction model.
iterations = st.sidebar.slider("Iterations", 10, 20_000, 1000, 100)
sleep = st.sidebar.slider("Sleep", 0.0, 1.0, 0.1, 0.01)
theta = st.sidebar.slider("Theta", 0, 360, 30, 10)

# Non-interactive elements return a placeholder to their location
# in the app. Here we're storing progress_bar to update it later.
progress_bar = st.sidebar.progress(0)

# These two elements will be filled in later, so we create a placeholder
# for them using st.empty()
frame_text = st.sidebar.empty()
image = st.empty()

m, n, s = 960, 640, 400
x = np.linspace(-m / s, m / s, num=m).reshape((1, m))
y = np.linspace(-n / s, n / s, num=n).reshape((n, 1))

frame_num = 0
for screen in MegaScreen(
    windowShape=(100, 100), theta=theta * np.pi / 180, numIter=iterations
):
    # Here were setting value for these two elements.
    frame_num += 1
    progress_bar.progress(frame_num / iterations)
    frame_text.text("Frame %i/100" % (frame_num + 1))
    smax = np.amax(screen)
    smin = np.amin(screen)
    scaled_screen = (screen - smin) / (smax - smin)
    # Update the image placeholder by calling the image() function on it.
    image.image(scaled_screen, use_column_width=True)
    time.sleep(sleep)

# We clear elements by calling empty on them.
progress_bar.empty()
frame_text.empty()

# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")
