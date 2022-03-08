import streamlit as st
import pandas as pd
import numpy as np
import time

df_options = pd.DataFrame({
    'atlas': ['LSFM', 'MRI', 'CCFv3'],
    'orientaion': ['Coronal', 'Sagital', 'Horizontal']
    })

df_highligt = pd.DataFrame({
    'regions': ['hippo', 'cortex', 'ap', 'osv'],
    })

option_atlas = st.sidebar.selectbox(
    'Slice orientation:',
     df_options['atlas'])

option_orientation = st.sidebar.selectbox(
    'Navigate in:',
     df_options['orientaion'])

option_highligt = st.sidebar.selectbox(
    'Current highlight region:',
     df_highligt['regions'])


'You selected atlas: ', option_atlas
'You selected orientation: ', option_orientation
'You selected regions: ', option_orientation


'Starting a long computation...'
# Add a placeholder
latest_iteration = st.empty()
bar = st.progress(0)

for i in range(100):
  # Update the progress bar with each iteration.
  latest_iteration.text(f'Iteration {i+1}')
  bar.progress(i + 1)
  time.sleep(0.1)

'...and now we\'re done!'




x = st.slider('x')  # 👈 this is a widget
st.write(x, 'squared is', x * x)

# Create widget which can be accesed by a key
st.text_input("Enter your name", key="name")

st.write(st.session_state.name)


