import streamlit as st
import pandas as pd
import numpy as np

options = np.array('Coronal', 'Sagital', 'Horizontal')

option = st.selectbox(
    'Navigate in:',
     options)

'You selected: ', option




x = st.slider('x')  # 👈 this is a widget
st.write(x, 'squared is', x * x)

# Create widget which can be accesed by a key
st.text_input("Enter your name", key="name")

st.write(st.session_state.name)


