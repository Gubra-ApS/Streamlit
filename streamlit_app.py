import streamlit as st
import pandas as pd
import numpy as np
import time
import SimpleITK as sitk
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import plotly.express as px
import plotly.graph_objects as go
from skimage.transform import downscale_local_mean


def fig2img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it"""
    buf = io.BytesIO()
    fig.savefig(buf, pad_inches=0)
    buf.seek(0)
    img = Image.open(buf)
    return img


# custom functions
def im_plot(im):
    px = 1 / plt.rcParams['figure.dpi']
    # fig = plt.figure(figsize=(int(455*px), int(297*px)))
    fig = plt.figure(figsize=(15.319, 10))
    plt.imshow(im, cmap='gray')
    plt.axis('off')
    plt.tight_layout()

    pil_im = fig2img(fig)

    # st.pyplot(fig)

    return pil_im

def im_plot_mip(im, line_coord):
    # px = 1 / plt.rcParams['figure.dpi']
    # fig = plt.figure(figsize=(int(455*px), int(297*px)))
    #fig = plt.figure(figsize=(13.9, 10))
    fig, ax = plt.subplots()
    ax.imshow(im)

    rect = patches.Rectangle((0, line_coord), 200, 2, linewidth=1, edgecolor='r', facecolor='r')
    ax.add_patch(rect)

    ax.axis('off')
    fig.tight_layout()

    pil_im = fig2img(fig)

    # st.pyplot(fig)

    return pil_im


# create session variables
if 'y_val' not in st.session_state:
    st.session_state['y_val'] = '150'
if 'x_val' not in st.session_state:
    st.session_state['x_val'] = '150'
if 'z_val' not in st.session_state:
    st.session_state['z_val'] = '180'


@st.cache  # 👈 This function will be cached
def read_atlases(read):
    # load atlas files only once
    lsfm = sitk.GetArrayFromImage(sitk.ReadImage('atlas_data/LSFM_space_oriented/lsfm_temp.nii.gz'))
    lsfm = np.flip(lsfm, axis=0)
    lsfm_ano = sitk.GetArrayFromImage(sitk.ReadImage('atlas_data/LSFM_space_oriented/lsfm_ano_gubra.nii.gz'))
    lsfm_ano = np.flip(lsfm_ano, axis=0)

    mri = sitk.GetArrayFromImage(sitk.ReadImage('atlas_data/MRI_space_oriented/mri_temp.nii.gz'))
    mri = np.flip(mri, axis=0)
    ccfv3 = sitk.GetArrayFromImage(sitk.ReadImage('atlas_data/AIBS_CCFv3_space_oriented/ccfv3_temp.nii.gz'))
    ccfv3[ccfv3>255] = 255
    ccfv3 = np.flip(ccfv3, axis=0)

    return lsfm, mri, ccfv3, lsfm_ano

# read atlas volume (only at first app load)
lsfm, mri, ccfv3, lsfm_ano = read_atlases(1)


# ## Setup drop down selection menus
# df_options = pd.DataFrame({
#     'orientaion': ['Coronal', 'Sagital']
#     })

# df_highligt = pd.DataFrame({
#     'regions': ['hippo', 'cortex', 'ap', 'osv'],
#     })

df_highligt = pd.read_csv('ARA2_annotation_info_reduced_gubraview.csv')

# option_atlas = st.sidebar.selectbox(
#     'Navigate in:',
#      df_options['atlas'])

# st.sidebar.header('Select orientation')
# option_orientation = st.sidebar.selectbox(
#     'Slice orientation:',
#      df_options['orientaion'])

st.sidebar.header('Atlas brain regions')
option_highligt = st.sidebar.selectbox(
    'Current highlight region:',
     df_highligt['acronym'])

# temp = df_highligt.loc[df_highligt['acronym'] == option_highligt]
# st.session_state.y_val = str(temp.iloc[0]['slice_number'])

st.sidebar.header('Stereotaxic coordinate')
ste_coord = st.sidebar.text_input('x (medial-laterally); y (anterior-posterior); z ():', '0; 0; 0')

if st.sidebar.button('Got to coordinate'):
    # parse text string and set sesseio state vars
    st.write(ste_coord)
    # st.session_state.y_val = y
    # st.session_state.x_val = x
    # st.session_state.z_val = z
#


# st.sidebar.header('Explore')

# Create a canvas component
col1, col2 = st.columns(2)
with col1:
    image = Image.open('horizontal_white_neuropedia/' + option_highligt + '.tif')
    pix = np.array(image)
    y_coord = int(int(float(st.session_state.y_val)) / 512 * 199) + 20
    im_mip = im_plot_mip(pix, y_coord)

    canvas_result_mip = st_canvas(
        stroke_width=0,
        stroke_color="black",
        background_image=im_mip,
        height=199,
        width=143,
        drawing_mode="circle",
        display_toolbar=False,
        key="mip"
    )
    if canvas_result_mip.json_data is not None:
        df = pd.json_normalize(canvas_result_mip.json_data["objects"])
        if len(df) != 0:
            df["center_x"] = df["left"] + df["radius"] * np.cos(
                df["angle"] * np.pi / 180
            )
            df["center_y"] = df["top"] + df["radius"] * np.sin(
                df["angle"] * np.pi / 180
            )

            # st.subheader("Click coordinate")
            for index, row in df.iterrows():
                if index + 1 == len(df):
                    # st.markdown(
                    #     # f'Center coords: ({row["center_x"]:.2f}, {row["center_y"]:.2f}). Radius: {row["radius"]:.2f}'
                    #     f'Center coords: ({row["center_x"]:.2f}, {row["center_y"]:.2f}). Radius: {row["radius"]:.2f}'
                    # )
                    st.session_state.y_val = str(int(row["center_y"] / 199 * 512) + 25)


    y_coord = int(int(float(st.session_state.y_val)) / 512 * 199) + 20
    im_mip = im_plot_mip(pix, y_coord)
    st.image(im_mip)
    # y_slider = st.slider('Anterior-posterios', min_value=0, max_value=199, value=y_coord, step=1)

# with col2:
#     # template
#     im_click_pre = np.copy(lsfm[:, int(float(st.session_state.y_val))+30, :])
#     im_click_pre = downscale_local_mean(im_click_pre,(2,2))
#     im_click = im_plot(im_click_pre)
#     canvas_result = st_canvas(
#         stroke_width=0,
#         stroke_color="black",
#         background_image=im_click,
#         height=im_click_pre.shape[0],
#         width=im_click_pre.shape[1],
#         drawing_mode="circle",
#         display_toolbar=False,
#         key="center_circle_app"
#     )
#     if canvas_result.json_data is not None:
#         df = pd.json_normalize(canvas_result.json_data["objects"])
#         if len(df) != 0:
#             df["center_x"] = df["left"] + df["radius"] * np.cos(
#                 df["angle"] * np.pi / 180
#             )
#             df["center_y"] = df["top"] + df["radius"] * np.sin(
#                 df["angle"] * np.pi / 180
#             )
#
#             # st.subheader("Click coordinate")
#             for index, row in df.iterrows():
#                 if index + 1 == len(df):
#                     # st.markdown(
#                     #     # f'Center coords: ({row["center_x"]:.2f}, {row["center_y"]:.2f}). Radius: {row["radius"]:.2f}'
#                     #     f'Center coords: ({row["center_x"]:.2f}, {row["center_y"]:.2f}). Radius: {row["radius"]:.2f}'
#                     # )
#                     st.session_state.x_val = str(row["center_x"])
#                     st.session_state.z_val = str(row["center_y"])


    # # ano
    # im_click_pre_ano = np.copy(lsfm_ano[:, int(st.session_state.y_val)+30, :])
    # im_click_pre_ano[im_click_pre_ano>255] = 255
    # im_click_pre_ano = downscale_local_mean(im_click_pre_ano,(2,2))
    # im_click_ano = im_plot(im_click_pre_ano)
    # canvas_result_ano = st_canvas(
    #     stroke_width=0,
    #     stroke_color="black",
    #     background_image=im_click_ano,
    #     height=im_click_pre_ano.shape[0],
    #     width=im_click_pre_ano.shape[1],
    #     drawing_mode="circle",
    #     display_toolbar=False,
    #     key="ano_click"
    # )
    # if canvas_result_ano.json_data is not None:
    #     df = pd.json_normalize(canvas_result_ano.json_data["objects"])
    #     if len(df) != 0:
    #         df["center_x"] = df["left"] + df["radius"] * np.cos(
    #             df["angle"] * np.pi / 180
    #         )
    #         df["center_y"] = df["top"] + df["radius"] * np.sin(
    #             df["angle"] * np.pi / 180
    #         )
    #
    #         # st.subheader("Click coordinate")
    #         for index, row in df.iterrows():
    #             if index + 1 == len(df):
    #                 # st.markdown(
    #                 #     # f'Center coords: ({row["center_x"]:.2f}, {row["center_y"]:.2f}). Radius: {row["radius"]:.2f}'
    #                 #     f'Center coords: ({row["center_x"]:.2f}, {row["center_y"]:.2f}). Radius: {row["radius"]:.2f}'
    #                 # )
    #                 st.session_state.x_val = str(row["center_x"])
    #                 st.session_state.z_val = str(row["center_y"])
    #

# if st.sidebar.button('Go to region centre'):
#     temp = df_highligt.loc[df_highligt['acronym'] == option_highligt]
#     st.session_state.y_val = str(temp.iloc[0]['slice_number'])

# 'You selected atlas: ', option_atlas
# 'You selected orientation: ', option_orientation
# 'You selected regions: ', option_orientation


#
st.header('Stereotxic coordinate [' + st.session_state.x_val + ', ' + st.session_state.y_val + ', ' + st.session_state.z_val + ']')

#
#

# col1, col2 = st.columns(2)
# with col1:
#     if option_orientation=='Coronal':
#         if st.button('Next'):
#             st.session_state.y_val = str(int(st.session_state.y_val)+10)
#         if st.button('Prev'):
#             st.session_state.y_val = str(int(st.session_state.y_val)-10)
#         #st.sidebar.button('Go to region centre')
#
#         image = Image.open('horizontal_white_neuropedia/'+option_highligt+'.tif')
#         st.image(image)
#
#     if option_orientation=='Sagital':
#         image = Image.open('horizontal_white_neuropedia/'+option_highligt+'.tif')
#         st.image(image)
#         st.image(mri[:, :, int(x)])
# with col2:
#     if option_orientation == 'Coronal':
#         # Create a canvas component
#         canvas_result = st_canvas(
#             stroke_width=0,
#             stroke_color="black",
#             background_image=im_plot(mri[:, int(st.session_state.y_val), :]),
#             height=297,
#             width=455,
#             drawing_mode="circle",
#             display_toolbar=False,
#             key="center_circle_app"
#         )
#         if canvas_result.json_data is not None:
#             df = pd.json_normalize(canvas_result.json_data["objects"])
#             if len(df) != 0:
#                 df["center_x"] = df["left"] + df["radius"] * np.cos(
#                     df["angle"] * np.pi / 180
#                 )
#                 df["center_y"] = df["top"] + df["radius"] * np.sin(
#                     df["angle"] * np.pi / 180
#                 )
#
#                 st.subheader("Click coordinate")
#                 for index, row in df.iterrows():
#                     if index + 1 == len(df):
#                         st.markdown(
#                             # f'Center coords: ({row["center_x"]:.2f}, {row["center_y"]:.2f}). Radius: {row["radius"]:.2f}'
#                             f'Center coords: ({row["center_x"]:.2f}, {row["center_y"]:.2f}). Radius: {row["radius"]:.2f}'
#                         )
#
#                         st.session_state.x_val = str(row["center_x"])
#                         st.session_state.z_val = str(row["center_y"])
#
#     #st.image(ccfv3[:,int(st.session_state.y_val),:])
#     if option_orientation == 'Sagital':
#         st.image(lsfm[:, :, int(x)])
#         st.image(ccfv3[:, :, int(x)])
#
#




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


