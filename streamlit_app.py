import streamlit as st
import pandas as pd
import numpy as np
import SimpleITK as sitk
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from skimage.transform import resize, downscale_local_mean
import helpers

##### CSS STYLING
def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)

local_css("style.css")


##### CREATE SESSION VARIABLES
if 'mip_control_counter' not in st.session_state:
    st.session_state['mip_control_counter'] = 0

if 'cor_control_counter' not in st.session_state:
    st.session_state['cor_control_counter'] = 0

if 'highligt_ind' not in st.session_state:
    st.session_state['highligt_ind'] = 0



# lsfm
if 'y_val' not in st.session_state:
    st.session_state['y_val'] = '200'
if 'x_val' not in st.session_state:
    st.session_state['x_val'] = '60'
if 'z_val' not in st.session_state:
    st.session_state['z_val'] = '80'

# mri
if 'y_val_mri' not in st.session_state:
    st.session_state['y_val_mri'] = '200'
if 'x_val_mri' not in st.session_state:
    st.session_state['x_val_mri'] = '60'
if 'z_val_mri' not in st.session_state:
    st.session_state['z_val_mri'] = '80'

# ccfv3
if 'y_val_ccfv3' not in st.session_state:
    st.session_state['y_val_ccfv3'] = '200'
if 'x_val_ccfv3' not in st.session_state:
    st.session_state['x_val_ccfv3'] = '60'
if 'z_val_ccfv3' not in st.session_state:
    st.session_state['z_val_ccfv3'] = '80'

def y_sess_update():
    #st.session_state.y_val = str(int((float(st.session_state.y_slider_s) / 340 * 512) - 20))
    st.session_state.y_val = str(st.session_state.y_slider_s)

def y_sess_update_select():
    temp = df_highligt[df_highligt['acronym'] == st.session_state.y_select_s]
    if temp.first_valid_index() != None:
        st.session_state['highligt_ind'] = int(temp.first_valid_index())

    #st.session_state['highligt_ind'] = st.session_state.y_select_s

def ste_coord_sess():
    st.session_state.y_val = st.session_state.ste_coord_s.split(';')[1].strip()
    st.session_state.x_val = st.session_state.ste_coord_s.split(';')[0].strip()
    st.session_state.z_val = st.session_state.ste_coord_s.split(';')[2].strip()


##### READ DATA
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

# read atlas region info
df_highligt = pd.read_csv('ARA2_annotation_info_reduced_gubraview.csv')


# ##### BUILD APP
# st.session_state
st.header('Coordinate picker')
with st.container():
    # Create a canvas component
    col1a, col2a = st.columns(2)
    with col1a:
        ### SELECT BOX WITH ATLAS REGIONS
        option_highligt = st.empty()
        option_highligt = st.selectbox(
            'Current highlight region:',
            df_highligt['acronym'],
            index=st.session_state.highligt_ind,
            key='y_select_s',
            on_change=y_sess_update_select)

        ### MIP DRAWABLE CANVAS
        # st.write('Click images to select coordinate..')
        image = Image.open('horizontal_white_neuropedia/' + option_highligt + '.tif')
        pix = np.array(image)
        pix = np.swapaxes(pix, 0, 1)
        y_coord = int(int(float(st.session_state.y_val)) / 512 * 199) + 20
        im_mip = helpers.im_plot_mip(pix, y_coord)

        canvas_result_mip = st_canvas(
            stroke_width=0,
            stroke_color="black",
            background_image=im_mip,
            height=200,
            width=340,
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
                        if len(df) > st.session_state['mip_control_counter']:
                            st.session_state.y_val = str(int(row["center_x"] / 340 * 512) - 20)
                            st.session_state['mip_control_counter'] = len(df)

        # slider_y = st.slider('Position', 0, 340, int((float(st.session_state.y_val) / 512 * 340)+12),
        #                      format='%g',
        #                      key='y_slider_s',
        #                      on_change=y_sess_update)

        slider_y = st.slider('Click image to select y coordinate..', 0, 512, int(float(st.session_state.y_val)),
                             format='%g',
                             key='y_slider_s',
                             on_change=y_sess_update)

    with col2a:
        df_cor = pd.DataFrame({
            'plates': ('Template', 'Annotations')
        })

        option_coronal = st.selectbox(
            'Coronal plate:',
            df_cor['plates'])

        # template coronal
        if option_coronal == 'Template':
            im_click_pre = np.copy(lsfm[:, int(float(st.session_state.y_val)) + 30, :])
        else:
            im_click_pre = np.copy(lsfm_ano[:, int(float(st.session_state.y_val)) + 30, :])

        im_click_pre = resize(im_click_pre, (179, 246))
        im_click = helpers.im_plot(im_click_pre)
        canvas_result = st_canvas(
            stroke_width=0,
            stroke_color="black",
            background_image=im_click,
            height=im_click_pre.shape[0],
            width=im_click_pre.shape[1],
            drawing_mode="circle",
            display_toolbar=False,
            key="center_circle_app"
        )
        if canvas_result.json_data is not None:
            df = pd.json_normalize(canvas_result.json_data["objects"])
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
                        if len(df) > st.session_state['cor_control_counter']:
                            st.session_state.x_val = str(int((float(row["center_x"]) / 246 * 369)))
                            st.session_state.z_val = str(int((float(row["center_y"]) / 179 * 268)))

                            if option_coronal == 'Annotations':
                                temp_id = lsfm_ano[int(float(st.session_state.z_val)),int(float(st.session_state.y_val)),int(float(st.session_state.x_val))]
                                temp = df_highligt[df_highligt['id']==temp_id]
                                # st.write(temp)
                                # st.write(temp.first_valid_index())
                                if temp.first_valid_index() != None:
                                    st.session_state['highligt_ind'] = int(temp.first_valid_index())

                            st.session_state['cor_control_counter'] = len(df)

        ### TEXT FIELD INPUT
        st.write('Click image to select x, z coordinates..')
        ste_coord = st.text_input('(medial-lateral); (anterior-posterior); (dorsal-caudal):',
                                  f'{st.session_state.x_val}; {st.session_state.y_val}; {st.session_state.z_val}',
                                  key="ste_coord_s",
                                  on_change=ste_coord_sess)


# Create a canvas component
st.subheader(f'Current coordinate: {st.session_state.x_val}, {st.session_state.y_val}, {st.session_state.z_val}')
# st.markdown(
#     f'<h3 style="color:#000000;font-size:22px;">{st.session_state.x_val}, {st.session_state.y_val}, {st.session_state.z_val}</h3>',
#     unsafe_allow_html=True)
# st.write('[' + st.session_state.x_val + ', ' + st.session_state.y_val + ', ' + st.session_state.z_val + ']')
#
col1, col2 = st.columns(2)
with col1:
    # plot LSFM
    im_lsfm = np.copy(lsfm[:, int(float(st.session_state.y_val))+30, :])
    im_ano = np.copy(lsfm_ano[:, int(float(st.session_state.y_val)) + 30, :])

    temp_id = df_highligt.iloc[st.session_state.highligt_ind,0]

    im_ano[im_ano!=temp_id] = 0
    im_ano[im_ano>0] = 100
    im_lsfm_pil = helpers.im_plot_coord(im_lsfm, im_ano, st.session_state.x_val, st.session_state.z_val)
    st.image(im_lsfm_pil)
#
#     if st.button('Sync to LSFM'):
#         # JPE calculations
#         st.session_state.y_val_mri = st.session_state.y_val
#         st.session_state.x_val_mri = st.session_state.x_val
#         st.session_state.z_val_mri = st.session_state.z_val
#
#         st.session_state.y_val_ccfv3 = st.session_state.y_val
#         st.session_state.x_val_ccfv3 = st.session_state.x_val
#         st.session_state.z_val_ccfv3 = st.session_state.z_val

# with col2:
    # # plot MRI
    # im_mri = np.copy(mri[:, int(float(st.session_state.y_val_mri))+30, :])
    # im_mri_pil = helpers.im_plot_coord(im_mri, st.session_state.x_val_mri, st.session_state.z_val_mri)
    # st.image(im_mri_pil)
    #
    # # plot CCFv3
    # im_ccfv3 = np.copy(ccfv3[:, int(float(st.session_state.y_val_ccfv3))+30, :])
    # im_ccfv3_pil = helpers.im_plot_coord(im_ccfv3, st.session_state.x_val_mri, st.session_state.z_val_mri)
    # st.image(im_ccfv3_pil)

    #

# Test plotly hover
