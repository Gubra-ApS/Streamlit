import streamlit as st
import pandas as pd
import numpy as np
import time
import SimpleITK as sitk

@st.cache  # 👈 This function will be cached
def read_atlases(read):
    # load atlas files only once
    lsfm = sitk.GetArrayFromImage(sitk.ReadImage('atlas_data/LSFM_space_oriented/lsfm_temp.nii.gz'))
    lsfm = np.flip(lsfm, axis=1)
    mri = sitk.GetArrayFromImage(sitk.ReadImage('atlas_data/MRI_space_oriented/mri_temp.nii.gz'))
    mri = np.flip(mri, axis=1)
    ccfv3 = sitk.GetArrayFromImage(sitk.ReadImage('atlas_data/AIBS_CCFv3_space_oriented/ccfv3_temp.nii.gz'))
    ccfv3[ccfv3>255] = 255
    ccfv3 = np.flip(ccfv3, axis=1)

    return lsfm, mri, ccfv3

# read atlas volume (only at first app load)
lsfm, mri, ccfv3 = read_atlases(1)

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

col1, col2 = st.columns(2)
with col1:
    pos = st.slider('Atlas positions', min_value=0, max_value=lsfm.shape[1], value=int(lsfm.shape[1]/2), step=None)
    st.image(lsfm[:,pos,:])
with col2:
    st.image(mri[:,pos,:])
    st.image(ccfv3[:,pos,:])






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


