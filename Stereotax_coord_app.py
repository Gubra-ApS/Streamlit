# -*- coding: utf-8 -*-
"""
Created on Tue Feb 15 21:59:50 2022

@author: jpe


Multimodal mouse brain atlas - coordinate system app


"""
import os
import numpy as np
import matplotlib.pyplot as plt
import skimage.io
import skimage.transform
import scipy.ndimage
import time
from numba import jit
import pandas as pd

from skimage.morphology import disk, ball
from numpy.random import choice

import SimpleITK as sitk

import sys
sys.path.insert(0,r'C:\Users\JPE\OneDrive - Gubra ApS\ProvidedCodes\brain_statistics_29062020')
import GubraImg as gi

# %% Load data
atlas_path = r'U:\BRAIN_ATLAS_TOOLS\gubra_atlas\Multimodal_mouse_atlas'

mri_path = atlas_path + r'\MRI_space_oriented'
mri_temp = gi.io.load_nifti(os.path.join(mri_path,'mri_temp.nii.gz'))
mri_ano = gi.io.load_nifti(os.path.join(mri_path,'mri_ano_gubra.nii.gz'))
mri_coords = gi.io.load_nifti(os.path.join(mri_path,'mri_coords_all.nii.gz'))
mri_hem_mask = np.zeros(mri_temp.shape)
mri_hem_mask[:,:,:227]=1
#gi.io.save_nifti(mri_hem_mask,os.path.join(mri_path,'mri_hem_mask.nii.gz'))

aibs_path = atlas_path + r'\AIBS_CCFv3_space_oriented'
aibs_temp = gi.io.load_nifti(os.path.join(aibs_path,'ccfv3_temp.nii.gz'))
aibs_ano = gi.io.load_nifti(os.path.join(aibs_path,'ccfv3_ano_gubra.nii.gz'))
aibs_coords = gi.io.load_nifti(os.path.join(aibs_path,'ccfv3_coords_all.nii.gz'))
aibs_hem_mask = np.zeros(aibs_temp.shape)
aibs_hem_mask[:,:,:227]=1
#gi.io.save_nifti(aibs_hem_mask,os.path.join(aibs_path,'ccfv3_hem_mask.nii.gz'))

ls_path = atlas_path + r'\LSFM_space_oriented'
ls_temp = gi.io.load_nifti(os.path.join(ls_path,'lsfm_temp.nii.gz'))
ls_ano = gi.io.load_nifti(os.path.join(ls_path,'lsfm_ano_gubra.nii.gz'))
ls_coords = gi.io.load_nifti(os.path.join(ls_path,'lsfm_coords_all.nii.gz'))
ls_hem_mask = np.zeros(ls_temp.shape)
ls_hem_mask[:,:,:185]=1
#gi.io.save_nifti(ls_hem_mask,os.path.join(ls_path,'lsfm_hem_mask.nii.gz'))

# %% Find necessary substack size for adapting the get_coord_atlas for substacks

# get non-zero coordinate values for x,y,z in mri space
mri_xcoords = list(mri_coords[int(mri_temp.shape[0]/2),int(mri_temp.shape[1]/2),:,2])
mri_xcoords = [np.round(i,2) for i in mri_xcoords if i !=0]
mri_xcoords = [ii for n,ii in enumerate(mri_xcoords) if ii not in mri_xcoords[:n]]
mri_ycoords = list(mri_coords[int(mri_temp.shape[0]/2), : ,int(mri_temp.shape[2]/2),1])
mri_ycoords = [np.round(i,2) for i in mri_ycoords if i !=0]
mri_ycoords = [ii for n,ii in enumerate(mri_ycoords) if ii not in mri_ycoords[:n]]
mri_zcoords = list(mri_coords[:,int(mri_temp.shape[1]/2),int(mri_temp.shape[2]/2),0])
mri_zcoords = [np.round(i,2) for i in mri_zcoords if i !=0]
mri_zcoords = [ii for n,ii in enumerate(mri_zcoords) if ii not in mri_zcoords[:n]]



# NUMBER OF SLICES NEEDED FOR LSFM ATLAS                
#y_stacks,y_stack_max = get_substack_sizes(mri_ycoords,ls_coords[:,:,:,1],axis='y') # max nr slices needed 31          
#x_stacks,x_stack_max = get_substack_sizes(mri_xcoords,ls_coords[:,:,:,2],axis='x') # max nr slices needed 16         
#z_stacks,z_stack_max = get_substack_sizes(mri_zcoords,ls_coords[:,:,:,0],axis='z') # max nr slices needed 35  

# NUMBER OF SLICES NEEDED FOR AIBS ATLAS                
y_stacks,y_stack_max = get_substack_sizes(mri_ycoords,aibs_coords[:,:,:,1],axis='y') # max nr slices needed 12          
x_stacks,x_stack_max = get_substack_sizes(mri_xcoords,aibs_coords[:,:,:,2],axis='x') # max nr slices needed 10         
z_stacks,z_stack_max = get_substack_sizes(mri_zcoords,aibs_coords[:,:,:,0],axis='z') # max nr slices needed 19              

    
# %% Connect coordinates with substacks
#pos_y_coords = list(np.round(np.arange(-8.6,6.4,0.01),2))
pos_x_coords = list(np.round(np.arange(0,5.2,0.01),2))
#pos_z_coords = list(np.round(np.arange(-0.3,7.1,0.01),2))
#pos_x_coords = list(np.round(np.arange(0,5.2,0.5),2))
#pos_z_coords = list(np.round(np.arange(-0.3,7.1,0.5),2))


#y_mid_slices_ls = connect_coords_substacks(pos_y_coords,ls_coords[:,:,:,1],axis='y')
#y_mid_slices_aibs = connect_coords_substacks(pos_y_coords,aibs_coords[:,:,:,1],axis='y')
#y_mid_slices_mri = connect_coords_substacks(pos_y_coords,mri_coords[:,:,:,1],axis='y')

x_mid_slices_ls_L = connect_coords_substacks(pos_x_coords,ls_coords[:,:,:,2],hem_mask=ls_hem_mask,axis='x',hem_side = 'left')
x_mid_slices_aibs_L = connect_coords_substacks(pos_x_coords,aibs_coords[:,:,:,2],hem_mask=aibs_hem_mask,axis='x',hem_side = 'left')
x_mid_slices_mri_L = connect_coords_substacks(pos_x_coords,mri_coords[:,:,:,2],hem_mask=mri_hem_mask,axis='x',hem_side = 'left')


x_mid_slices_ls_R = connect_coords_substacks(pos_x_coords,ls_coords[:,:,:,2],hem_mask=ls_hem_mask,axis='x',hem_side = 'right')
x_mid_slices_aibs_R = connect_coords_substacks(pos_x_coords,aibs_coords[:,:,:,2],hem_mask=aibs_hem_mask,axis='x',hem_side = 'right')
x_mid_slices_mri_R = connect_coords_substacks(pos_x_coords,mri_coords[:,:,:,2],hem_mask=mri_hem_mask,axis='x',hem_side = 'right')


coord_mri, value_mri, hem_mri = get_random_coord(mri_temp, mri_coords, mri_hem_mask)

# start = time.time()
# coord_aibs, value_aibs, diff_aibs = get_coord_atlas(value_mri, hem_mri, mri_hem_mask, aibs_coords,aibs_hem_mask)
# end = time.time()
# print(end - start)

# start = time.time()
# aibs_coords_sub,aibs_hem_mask_sub,substack = get_substack(value_mri, aibs_coords,aibs_hem_mask, target_atlas='aibs', axis='y')
# coord_aibs, value_aibs, diff_aibs = get_coord_atlas(value_mri, hem_mri, mri_hem_mask, aibs_coords_sub,aibs_hem_mask_sub)
# end = time.time()
# print(end - start)

# start = time.time()
# coord_ls, value_ls, diff_ls = get_coord_atlas(value_mri, hem_mri, mri_hem_mask, ls_coords,ls_hem_mask)
# end = time.time()
# print(end - start)

start = time.time()
aibs_coords_sub,aibs_hem_mask_sub,substack = get_substack(value_mri, aibs_coords,aibs_hem_mask, target_atlas='aibs', target_hem = hem_mri)
coord_aibs, value_aibs, diff_aibs = get_coord_atlas_substack(value_mri, hem_mri, mri_hem_mask, aibs_coords_sub,aibs_hem_mask_sub,substack)
end = time.time()
print(end - start)

start = time.time()
ls_coords_sub,ls_hem_mask_sub,substack = get_substack(value_mri, ls_coords,ls_hem_mask, target_atlas='ls', target_hem = hem_mri)
coord_ls, value_ls, diff_ls = get_coord_atlas_substack(value_mri, hem_mri, mri_hem_mask, ls_coords_sub,ls_hem_mask_sub, substack)
end = time.time()
print(end - start)

# Coronal figure
fig, (ax1, ax2,ax3) = plt.subplots(1, 3, figsize=(15,4))
ax1.imshow(np.flipud(mri_temp[:,coord_mri[1],:]),cmap = 'gray', vmin = 50, vmax = 250)
ax1.plot(coord_mri[2],mri_temp.shape[0]-coord_mri[0],'o',color = '#c708b0',markersize =2)
ax1.plot([coord_mri[2],coord_mri[2]],[0,mri_temp.shape[0]],'-',color = '#c708b0',linewidth =1.5)
ax1.plot([0,mri_temp.shape[2]],[mri_temp.shape[0]-coord_mri[0],mri_temp.shape[0]-coord_mri[0]],'-',color = '#c708b0',linewidth =1.5)
ax1.axis('off')

ax2.imshow(np.flipud(aibs_temp[:,coord_aibs[1],:]),cmap = 'gray', vmin = 10, vmax = 300)
ax2.plot(coord_aibs[2],aibs_temp.shape[0]-coord_aibs[0],'o',color = '#c708b0',markersize =2)
ax2.plot([coord_aibs[2],coord_aibs[2]],[0,aibs_temp.shape[0]],'-',color = '#c708b0',linewidth =1.5)
ax2.plot([0,aibs_temp.shape[2]],[aibs_temp.shape[0]-coord_aibs[0],aibs_temp.shape[0]-coord_aibs[0]],'-',color = '#c708b0',linewidth =1.5)
ax2.axis('off')

ax3.imshow(np.flipud(ls_temp[:,coord_ls[1],:]),cmap = 'gray', vmin = 10, vmax = 220)
ax3.plot(coord_ls[2],ls_temp.shape[0]-coord_ls[0],'o',color = '#c708b0',markersize =2)
ax3.plot([coord_ls[2],coord_ls[2]],[0,ls_temp.shape[0]],'-',color = '#c708b0',linewidth =1.5)
ax3.plot([0,ls_temp.shape[2]],[ls_temp.shape[0]-coord_ls[0],ls_temp.shape[0]-coord_ls[0]],'-',color = '#c708b0',linewidth =1.5)
ax3.axis('off')

plt.suptitle('Stereotaxic coordinate ' + str(np.round(value_mri,3)))

plt.tight_layout()


# %% Save atlas files in three orientations - coronal, sagittal and horizontal for the app


## Save atlas templates and annotations as TIF
#vol2tif_hor(mri_temp,atlas_path + r'/TIF_stacks/MRI_temp_oriented_horiz')
#vol2tif_hor(mri_ano,atlas_path + r'/TIF_stacks/MRI_ano_oriented_horiz')
#vol2tif_cor(mri_temp,atlas_path + r'/TIF_stacks/MRI_temp_oriented_coron')
#vol2tif_cor(mri_ano,atlas_path + r'/TIF_stacks/MRI_ano_oriented_coron')
# vol2tif_sag(mri_temp,atlas_path + r'/TIF_stacks/MRI_temp_oriented_sagit')
# vol2tif_sag(mri_ano,atlas_path + r'/TIF_stacks/MRI_ano_oriented_sagit')

# vol2tif_hor(aibs_temp,atlas_path + r'/TIF_stacks/AIBS_temp_oriented_horiz')
# vol2tif_hor(aibs_ano,atlas_path + r'/TIF_stacks/AIBS_ano_oriented_horiz')
# vol2tif_cor(aibs_temp,atlas_path + r'/TIF_stacks/AIBS_temp_oriented_coron')
# vol2tif_cor(aibs_ano,atlas_path + r'/TIF_stacks/AIBS_ano_oriented_coron')
# vol2tif_sag(aibs_temp,atlas_path + r'/TIF_stacks/AIBS_temp_oriented_sagit')
# vol2tif_sag(aibs_ano,atlas_path + r'/TIF_stacks/AIBS_ano_oriented_sagit')

# vol2tif_hor(ls_temp,atlas_path + r'/TIF_stacks/LSFM_temp_oriented_horiz')
# vol2tif_hor(ls_ano,atlas_path + r'/TIF_stacks/LSFM_ano_oriented_horiz')
# vol2tif_cor(ls_temp,atlas_path + r'/TIF_stacks/LSFM_temp_oriented_coron')
# vol2tif_cor(ls_ano,atlas_path + r'/TIF_stacks/LSFM_ano_oriented_coron')
# vol2tif_sag(ls_temp,atlas_path + r'/TIF_stacks/LSFM_temp_oriented_sagit')
# vol2tif_sag(ls_ano,atlas_path + r'/TIF_stacks/LSFM_ano_oriented_sagit')

## Save coordinate system as TIF
# vol2tif_hor(mri_coords[:,:,:,0],atlas_path + r'/TIF_stacks/MRI_zcoords_oriented_horiz')
vol2tif_hor(mri_coords[:,:,:,1],atlas_path + r'/TIF_stacks/MRI_ycoords_oriented_horiz')
vol2tif_hor(mri_coords[:,:,:,2],atlas_path + r'/TIF_stacks/MRI_xcoords_oriented_horiz')
vol2tif_cor(mri_coords[:,:,:,0],atlas_path + r'/TIF_stacks/MRI_zcoords_oriented_coron')
vol2tif_cor(mri_coords[:,:,:,1],atlas_path + r'/TIF_stacks/MRI_ycoords_oriented_coron')
vol2tif_cor(mri_coords[:,:,:,2],atlas_path + r'/TIF_stacks/MRI_xcoords_oriented_coron')
vol2tif_sag(mri_coords[:,:,:,0],atlas_path + r'/TIF_stacks/MRI_zcoords_oriented_sagit')
vol2tif_sag(mri_coords[:,:,:,1],atlas_path + r'/TIF_stacks/MRI_ycoords_oriented_sagit')
vol2tif_sag(mri_coords[:,:,:,2],atlas_path + r'/TIF_stacks/MRI_xcoords_oriented_sagit')

# vol2tif_hor(aibs_coords[:,:,:,0],atlas_path + r'/TIF_stacks/AIBS_zcoords_oriented_horiz')
vol2tif_hor(aibs_coords[:,:,:,1],atlas_path + r'/TIF_stacks/AIBS_ycoords_oriented_horiz')
vol2tif_hor(aibs_coords[:,:,:,2],atlas_path + r'/TIF_stacks/AIBS_xcoords_oriented_horiz')
vol2tif_cor(aibs_coords[:,:,:,0],atlas_path + r'/TIF_stacks/AIBS_zcoords_oriented_coron')
vol2tif_cor(aibs_coords[:,:,:,1],atlas_path + r'/TIF_stacks/AIBS_ycoords_oriented_coron')
vol2tif_cor(aibs_coords[:,:,:,2],atlas_path + r'/TIF_stacks/AIBS_xcoords_oriented_coron')
vol2tif_sag(aibs_coords[:,:,:,0],atlas_path + r'/TIF_stacks/AIBS_zcoords_oriented_sagit')
vol2tif_sag(aibs_coords[:,:,:,1],atlas_path + r'/TIF_stacks/AIBS_ycoords_oriented_sagit')
vol2tif_sag(aibs_coords[:,:,:,2],atlas_path + r'/TIF_stacks/AIBS_xcoords_oriented_sagit')

vol2tif_hor(ls_coords[:,:,:,0],atlas_path + r'/TIF_stacks/LSFM_zcoords_oriented_horiz')
vol2tif_hor(ls_coords[:,:,:,1],atlas_path + r'/TIF_stacks/LSFM_ycoords_oriented_horiz')
vol2tif_hor(ls_coords[:,:,:,2],atlas_path + r'/TIF_stacks/LSFM_xcoords_oriented_horiz')
vol2tif_cor(ls_coords[:,:,:,0],atlas_path + r'/TIF_stacks/LSFM_zcoords_oriented_coron')
vol2tif_cor(ls_coords[:,:,:,1],atlas_path + r'/TIF_stacks/LSFM_ycoords_oriented_coron')
vol2tif_cor(ls_coords[:,:,:,2],atlas_path + r'/TIF_stacks/LSFM_xcoords_oriented_coron')
vol2tif_sag(ls_coords[:,:,:,0],atlas_path + r'/TIF_stacks/LSFM_zcoords_oriented_sagit')
vol2tif_sag(ls_coords[:,:,:,1],atlas_path + r'/TIF_stacks/LSFM_ycoords_oriented_sagit')
vol2tif_sag(ls_coords[:,:,:,2],atlas_path + r'/TIF_stacks/LSFM_xcoords_oriented_sagit')



