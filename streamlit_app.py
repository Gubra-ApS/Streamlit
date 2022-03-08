import streamlit as st
import pandas as pd
import numpy as np

st.write('Hello world')

st.write('Perens atlas')

st.write('Git ny test')

st.write(pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
}))

x = st.slider('x')  # 👈 this is a widget
st.write(x, 'squared is', x * x)


