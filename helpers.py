import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import plotly.express as px
import plotly.graph_objects as go


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

    # rect = patches.Rectangle((0, line_coord), 200, 2, linewidth=1, edgecolor='r', facecolor='r')
    # ax.add_patch(rect)

    ax.axis('off')
    fig.tight_layout()

    pil_im = fig2img(fig)

    # st.pyplot(fig)

    return pil_im

def im_plot_pos(width, pos):
    # px = 1 / plt.rcParams['figure.dpi']
    # fig = plt.figure(figsize=(int(455*px), int(297*px)))
    #fig = plt.figure(figsize=(13.9, 10))
    pos_arr = np.ones((20,width),'uint8')
    pos = int((float(pos)-20) / 512 * 300)
    pos_arr[:,pos] = 0
    fig, ax = plt.subplots()
    ax.imshow(pos_arr, cmap='gray')

    # rect = patches.Rectangle((0, line_coord), 200, 2, linewidth=1, edgecolor='r', facecolor='r')
    # ax.add_patch(rect)

    ax.axis('off')
    fig.tight_layout()

    pil_im = fig2img(fig)

    # st.pyplot(fig)

    return pil_im

def im_plot_coord(im, x, y):
    # px = 1 / plt.rcParams['figure.dpi']
    # fig = plt.figure(figsize=(int(455*px), int(297*px)))
    #fig = plt.figure(figsize=(13.9, 10))
    fig, ax = plt.subplots()
    ax.imshow(im, cmap='gray')

    rect = patches.Rectangle((int(float(x)), int(float(y))), 5, 5, linewidth=1, edgecolor='r', facecolor='r')
    ax.add_patch(rect)

    ax.axis('off')
    fig.tight_layout()

    pil_im = fig2img(fig)

    # st.pyplot(fig)

    return pil_im