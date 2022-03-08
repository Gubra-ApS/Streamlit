import streamlit as st
import pandas as pd
import numpy as np
import time
import SimpleITK as sitk
from PIL import Image

# create session variables
if 'y_val' not in st.session_state:
    st.session_state['y_val'] = '300'

@st.cache  # 👈 This function will be cached
def read_atlases(read):
    # load atlas files only once
    lsfm = sitk.GetArrayFromImage(sitk.ReadImage('atlas_data/LSFM_space_oriented/lsfm_temp.nii.gz'))
    lsfm = np.flip(lsfm, axis=0)
    mri = sitk.GetArrayFromImage(sitk.ReadImage('atlas_data/MRI_space_oriented/mri_temp.nii.gz'))
    mri = np.flip(mri, axis=0)
    ccfv3 = sitk.GetArrayFromImage(sitk.ReadImage('atlas_data/AIBS_CCFv3_space_oriented/ccfv3_temp.nii.gz'))
    ccfv3[ccfv3>255] = 255
    ccfv3 = np.flip(ccfv3, axis=0)

    return lsfm, mri, ccfv3

# read atlas volume (only at first app load)
lsfm, mri, ccfv3 = read_atlases(1)


## Setup drop down selection menus
df_options = pd.DataFrame({
    'orientaion': ['Coronal', 'Sagital']
    })

# df_highligt = pd.DataFrame({
#     'regions': ['hippo', 'cortex', 'ap', 'osv'],
#     })

df_highligt = pd.read_csv('atlas_regions_available.csv')

# option_atlas = st.sidebar.selectbox(
#     'Navigate in:',
#      df_options['atlas'])

st.sidebar.header('Select orientation')
option_orientation = st.sidebar.selectbox(
    'Slice orientation:',
     df_options['orientaion'])

st.sidebar.header('Atlas brain regions')
option_highligt = st.sidebar.selectbox(
    'Current highlight region:',
     df_highligt['acronym'])

st.sidebar.button('Go to region centre')

# 'You selected atlas: ', option_atlas
# 'You selected orientation: ', option_orientation
# 'You selected regions: ', option_orientation

st.sidebar.header('Coordinate finder')
x = st.sidebar.text_input('x (medial-laterally):', '0')
y = st.sidebar.text_input('y (anterior-posterior):', '300')
z = st.sidebar.text_input('z (dorsal-ventral):', '0')
if st.sidebar.button('Update'):
    st.session_state.y_val = y
#
st.header('Stereotxic coordinate [' + x + ', ' + st.session_state.y_val + ', ' + z + ']')

col1, col2 = st.columns(2)
with col1:
    if option_orientation=='Coronal':
        if st.button('Next'):
            st.session_state.y_val = str(int(st.session_state.y_val)+10)
        if st.button('Prev'):
            st.session_state.y_val = str(int(st.session_state.y_val)-10)
        #st.sidebar.button('Go to region centre')

        image = Image.open('horizontal_white_neuropedia/'+option_highligt+'.tif')
        st.image(image)
        st.image(mri[:,int(st.session_state.y_val),:])
    if option_orientation=='Sagital':
        image = Image.open('horizontal_white_neuropedia/'+option_highligt+'.tif')
        st.image(image)
        st.image(mri[:, :, int(x)])
with col2:
    if option_orientation == 'Coronal':
        st.image(lsfm[:,int(st.session_state.y_val),:])
        st.image(ccfv3[:,int(st.session_state.y_val),:])
    if option_orientation == 'Sagital':
        st.image(lsfm[:, :, int(x)])
        st.image(ccfv3[:, :, int(x)])






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


