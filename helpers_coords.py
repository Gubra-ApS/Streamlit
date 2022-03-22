import os
import numpy as np
import skimage.io
import skimage.transform
from numba import jit
import pandas as pd
from numpy.random import choice

## Functions
def vol2tif_hor(vol, path):
    if not os.path.exists(path): os.makedirs(path)

    for k in range(vol.shape[0]):
        print(k)
        im = vol[k, :, :].astype('float32')
        # save prediction image
        skimage.external.tifffile.imsave(path + r'/z' + str(k + 1) + '.tif', im)


def vol2tif_cor(vol, path):
    if not os.path.exists(path): os.makedirs(path)

    for k in range(vol.shape[1]):
        print(k)
        im = np.flipud(vol[:, k, :]).astype('float32')
        # save prediction image
        skimage.external.tifffile.imsave(path + r'/y' + str(k + 1) + '.tif', im)


def vol2tif_sag(vol, path):
    if not os.path.exists(path): os.makedirs(path)

    for k in range(vol.shape[2]):
        print(k)
        im = np.flipud(vol[:, :, k]).astype('float32')
        # save prediction image
        skimage.external.tifffile.imsave(path + r'/x' + str(k + 1) + '.tif', im)


def get_substack_sizes(native_coords_ax, target_coords_ax, axis='y'):
    # native coords_ax: list of possible coordinate values for one axis
    # target_coords_ax: coordinates for one axis in 3D format
    if axis == 'y':
        stack_sizes = []
        for c in native_coords_ax:
            count = 0
            for s in range(target_coords_ax.shape[1]):
                temp_slice = np.round(target_coords_ax[:, s, :], 2)
                existing_coords = np.argwhere(temp_slice == c)
                # print(existing_coords)
                if existing_coords.shape[0] > 0:
                    count += 1
            print(count)
            stack_sizes.append(count)

    elif axis == 'x':
        target_coords_ax = target_coords_ax[:, :, 0:(int(target_coords_ax.shape[2] / 2))]
        stack_sizes = []
        for c in native_coords_ax:
            count = 0
            for s in range(target_coords_ax.shape[2]):
                temp_slice = np.round(target_coords_ax[:, :, s], 2)
                existing_coords = np.argwhere(temp_slice == c)
                # print(existing_coords)
                if existing_coords.shape[0] > 0:
                    count += 1
            print(count)
            stack_sizes.append(count)

    elif axis == 'z':
        stack_sizes = []
        for c in native_coords_ax:
            count = 0
            for s in range(target_coords_ax.shape[0]):
                temp_slice = np.round(target_coords_ax[s, :, :], 2)
                existing_coords = np.argwhere(temp_slice == c)
                # print(existing_coords)
                if existing_coords.shape[0] > 0:
                    count += 1
            print(count)
            stack_sizes.append(count)

    # calculate maximum stack size
    stack_size_max = np.max(stack_sizes)
    return stack_sizes, stack_size_max


def connect_coords_substacks(possible_coords_ax, target_coords_ax, hem_mask=[], axis='y', hem_side='right'):
    # native coords_ax: list of possible coordinate values for one axis
    # target_coords_ax: coordinates for one axis in 3D format
    target_coords_ax = np.round(target_coords_ax, 2)
    if np.size(hem_mask) != 0:
        if hem_side == 'right':
            target_coords_ax[hem_mask == 0] = 1000
        elif hem_side == 'left':
            target_coords_ax[hem_mask == 1] = 1000
    mid_stack = []
    for c in possible_coords_ax:
        existing_coords = np.argwhere(target_coords_ax == c)
        if existing_coords.shape[0] > 0:
            if axis == 'x':
                mid_slice = np.floor(np.max(existing_coords[:, 2]) - (
                            (np.max(existing_coords[:, 2]) - np.min(existing_coords[:, 2])) / 2))
            elif axis == 'y':
                mid_slice = np.floor(np.max(existing_coords[:, 1]) - (
                            (np.max(existing_coords[:, 1]) - np.min(existing_coords[:, 1])) / 2))
            elif axis == 'z':
                mid_slice = np.floor(np.max(existing_coords[:, 0]) - (
                            (np.max(existing_coords[:, 0]) - np.min(existing_coords[:, 0])) / 2))
            mid_stack.append(int(mid_slice))
        else:
            print(c)
            diff = np.sqrt((target_coords_ax - c) ** 2)
            coord_NN = np.argwhere((diff == np.min(diff)))[0]
            value_NN = target_coords_ax[coord_NN[0], coord_NN[1], coord_NN[2]]
            # print(value_NN)
            existing_coords = np.argwhere(target_coords_ax == value_NN)
            if axis == 'x':
                mid_slice = np.floor(np.max(existing_coords[:, 2]) - (
                            (np.max(existing_coords[:, 2]) - np.min(existing_coords[:, 2])) / 2))
            elif axis == 'y':
                mid_slice = np.floor(np.max(existing_coords[:, 1]) - (
                            (np.max(existing_coords[:, 1]) - np.min(existing_coords[:, 1])) / 2))
            elif axis == 'z':
                mid_slice = np.floor(np.max(existing_coords[:, 0]) - (
                            (np.max(existing_coords[:, 0]) - np.min(existing_coords[:, 0])) / 2))
            print(mid_slice)
            mid_stack.append(int(mid_slice))

    return mid_stack


def get_random_coord(temp, temp_coords, hem_mask):
    tissue_coords = np.argwhere(temp)
    rand_idx = choice(tissue_coords.shape[0], 1)
    native_coord = [tissue_coords[rand_idx, 0][0], tissue_coords[rand_idx, 1][0], tissue_coords[rand_idx, 2][0]]
    native_value = temp_coords[
        tissue_coords[rand_idx, 0][0], tissue_coords[rand_idx, 1][0], tissue_coords[rand_idx, 2][0]]
    native_hem = hem_mask[tissue_coords[rand_idx, 0][0], tissue_coords[rand_idx, 1][0], tissue_coords[rand_idx, 2][0]]
    return native_coord, native_value, int(native_hem)


@jit(forceobj=True, parallel=True)
def get_substack(native_value, target_coord_sys, target_hem_mask, target_atlas='aibs', target_hem=1):
    df_y = (pd.read_csv(atlas_path + r'/y_coord_2_slices.csv', index_col=0)).to_numpy()
    df_z = (pd.read_csv(atlas_path + r'/z_coord_2_slices.csv', index_col=0)).to_numpy()
    df_xr = (pd.read_csv(atlas_path + r'/x_coord_2_slices_right.csv', index_col=0)).to_numpy()
    df_xl = (pd.read_csv(atlas_path + r'/x_coord_2_slices_left.csv', index_col=0)).to_numpy()
    mid_slice_idx_y = np.argwhere(df_y[:, 0] == np.round(native_value[1], 2))[0]
    mid_slice_idx_z = np.argwhere(df_z[:, 0] == np.round(native_value[0], 2))[0]
    if target_hem == 1:
        mid_slice_idx_x = np.argwhere(df_xr[:, 0] == np.round(native_value[2], 2))[0]
        df_x = df_xr
    elif target_hem == 0:
        mid_slice_idx_x = np.argwhere(df_xl[:, 0] == np.round(native_value[2], 2))[0]
        df_x = df_xl

    if target_atlas == 'ls':
        mid_slice_y = df_y[mid_slice_idx_y, 3][0]
        mid_slice_z = df_z[mid_slice_idx_z, 3][0]
        mid_slice_x = df_x[mid_slice_idx_x, 3][0]
    elif target_atlas == 'aibs':
        mid_slice_y = df_y[mid_slice_idx_y, 2][0]
        mid_slice_z = df_z[mid_slice_idx_z, 2][0]
        mid_slice_x = df_x[mid_slice_idx_x, 2][0]
    elif target_atlas == 'mri':
        mid_slice_y = df_y[mid_slice_idx_y, 1][0]
        mid_slice_z = df_z[mid_slice_idx_z, 1][0]
        mid_slice_x = df_x[mid_slice_idx_x, 1][0]

    substack = [[int(mid_slice_z - 17), int(mid_slice_z + 17)], [int(mid_slice_y - 17), int(mid_slice_y + 17)],
                [int(mid_slice_x - 17), int(mid_slice_x + 17)]]
    target_coord_sys_sub = target_coord_sys[int(mid_slice_z - 17):int(mid_slice_z + 17),
                           int(mid_slice_y - 17):int(mid_slice_y + 17), int(mid_slice_x - 17):int(mid_slice_x + 17)]
    target_hem_mask_sub = target_hem_mask[int(mid_slice_z - 17):int(mid_slice_z + 17),
                          int(mid_slice_y - 17):int(mid_slice_y + 17), int(mid_slice_x - 17):int(mid_slice_x + 17)]
    return target_coord_sys_sub, target_hem_mask_sub, substack


@jit(forceobj=True, parallel=True)
def get_coord_atlas(native_value, native_hem, native_hem_mask, target_coord_sys, target_hem_mask):
    target_coord_sys = np.round(target_coord_sys, 3)
    diff_z = target_coord_sys[:, :, :, 0] - native_value[0]
    diff_y = target_coord_sys[:, :, :, 1] - native_value[1]
    diff_x = target_coord_sys[:, :, :, 2] - native_value[2]
    diff = np.sqrt(diff_x[:, :, :] ** 2 + diff_y[:, :, :] ** 2 + diff_z[:, :, :] ** 2)
    diff[target_hem_mask != native_hem] = 1000
    target_coord_NN = np.argwhere((diff == np.min(diff)))[0]
    target_value_NN = [target_coord_sys[target_coord_NN[0], target_coord_NN[1], target_coord_NN[2], 0],
                       target_coord_sys[target_coord_NN[0], target_coord_NN[1], target_coord_NN[2], 1],
                       target_coord_sys[target_coord_NN[0], target_coord_NN[1], target_coord_NN[2], 2]]
    return target_coord_NN, target_value_NN, diff


@jit(forceobj=True, parallel=True)
def get_coord_atlas_substack(native_value, native_hem, native_hem_mask, target_coord_sys, target_hem_mask, substack):
    target_coord_sys = np.round(target_coord_sys, 3)
    diff_z = target_coord_sys[:, :, :, 0] - native_value[0]
    diff_y = target_coord_sys[:, :, :, 1] - native_value[1]
    diff_x = target_coord_sys[:, :, :, 2] - native_value[2]
    diff = np.sqrt(diff_x[:, :, :] ** 2 + diff_y[:, :, :] ** 2 + diff_z[:, :, :] ** 2)
    diff[target_hem_mask != native_hem] = 1000
    target_coord_NN = np.argwhere((diff == np.min(diff)))[0]
    target_coord_NN_final = [target_coord_NN[0] + substack[0][0], target_coord_NN[1] + substack[1][0],
                             target_coord_NN[2] + substack[2][0]]
    target_value_NN = [target_coord_sys[target_coord_NN[0], target_coord_NN[1], target_coord_NN[2], 0],
                       target_coord_sys[target_coord_NN[0], target_coord_NN[1], target_coord_NN[2], 1],
                       target_coord_sys[target_coord_NN[0], target_coord_NN[1], target_coord_NN[2], 2]]
    return target_coord_NN_final, target_value_NN, diff

