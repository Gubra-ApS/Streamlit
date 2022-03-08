import streamlit as st
import pandas as pd
import numpy as np
import time
import SimpleITK as sitk

@st.cache  # 👈 This function will be cached
def read_atlases(read):
    # load atlas files only once
    volume = sitk.GetArrayFromImage(sitk.ReadImage('atlas_data/LSFM_space_oriented/lsfm_temp.nii.gz'))
    #volume = np.zeros((500,300,350),'uint8')
    return volume

atlas1 = read_atlases(1)

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

st.sidebar.button('Go to region centre')

# 'You selected atlas: ', option_atlas
# 'You selected orientation: ', option_orientation
# 'You selected regions: ', option_orientation

x = st.sidebar.text_input('x (medial-laterally):')
y = st.sidebar.text_input('y (anterior-posterior):')
z = st.sidebar.text_input('z (dorsal-ventral):')

#
st.header('Stereotxic coordinate')
'x: ', x
'y: ', y
'z: ', z

pos = st.slider('Atlas positions', min_value=0, max_value=atlas1.shape[0], value=int(atlas1.shape[0]/2), step=None)
st.image(atlas1[pos])






# 'Starting a long computation...'
# # Add a placeholder
# latest_iteration = st.empty()
# bar = st.progress(0)
#
# for i in range(100):
#   # Update the progress bar with each iteration.
#   latest_iteration.text(f'Iteration {i+1}')
#   bar.progress(i + 1)
#   time.sleep(0.1)
#
# '...and now we\'re done!'

# cache
# If this is the first time Streamlit has seen these four components with these exact values and in this exact
# combination and order, it runs the function and stores the result in a local cache. Then, next time the cached function is called,
# if none of these components changed, Streamlit will skip executing the function altogether and, instead,
# return the output previously stored in the cache.


