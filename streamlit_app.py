import streamlit as st
import pandas as pd
import numpy as np

df_options = pd.DataFrame({
    'atlas': ['LSFM', 'MRI', 'CCFv3'],
    'orientaion': ['Coronal', 'Sagital', 'Horizontal']
    })

option_atlas = st.selectbox(
    'Navigate in:',
     df_options['atlas'])

option_orientation = st.selectbox(
    'Navigate in:',
     df_options['orientaion'])


'You selected atlas: ', option_atlas
'You selected orientation: ', option_orientation




x = st.slider('x')  # 👈 this is a widget
st.write(x, 'squared is', x * x)

# Create widget which can be accesed by a key
st.text_input("Enter your name", key="name")

st.write(st.session_state.name)


