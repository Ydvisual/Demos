# Scipy gaussian filter visual demo by Ken York for Enthought
#
#
# imageio 2.5.0, pillow 6.1.0, numpy 1.17.0, scipy 1.3.1
# Virtual python 3.7.0 environment for Blender 2.80 (using Anaconda3)
# i.e. pip install pandas
#

import bpy
import math
import os
import imageio # Uses numpy, pillow
import numpy as np
import scipy.ndimage


# Gaussian filter setup
filter_levels = 150
sigma_min = 0.300
sigma_max = 2.000


# Render setup
final_frame = filter_levels * 2
exec((bpy.data.texts["render_setup"]).as_string())

# Material
def make_mat(name, color, metal, rough):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    matnodes = mat.node_tree.nodes
    bsdf = matnodes["Principled BSDF"]
    bsdf.inputs[0].default_value = color
    bsdf.inputs[4].default_value = metal
    bsdf.inputs[7].default_value = rough    
    return mat

def cube_at(r, c, color_val):
    sep = 1.02
    cube_id = "cube_R" + str(r) + "C" + str(c)
    px = r * sep
    py = c * sep
    pz = 0.0
    pos=(px, py, pz)
    #
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos)    
    mat_id = "mat_" + cube_id
    mat = make_mat(mat_id, (color_val, color_val, color_val, 1.0), 0.0, 1.0)
    ob = bpy.context.active_object
    ob.name = cube_id
    ob.data.materials.append(mat)
    return ob
        

# Clear objects and materials
for obj in bpy.context.scene.objects:
    bpy.data.objects.remove(obj)    
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat)

# Read in image file
str_localfile = "img\\test.png"
img_filename = os.path.join(os.path.dirname(bpy.data.filepath), str_localfile)
img_raw = imageio.imread(img_filename)
img_h = img_raw.shape[0]
img_w = img_raw.shape[1]
img_src = img_raw[:,:,0] # Grayscale, red channel only needed

# Filter output data storage
img_filtered = np.zeros((filter_levels, img_h, img_w))
sigma_vals = np.zeros(filter_levels)

# Filter levels: calculate & store
for idx in range(0, filter_levels):
    sigma = sigma_min + ((sigma_max - sigma_min) * (idx / filter_levels))
    img_filtered[idx] = scipy.ndimage.gaussian_filter(img_src, sigma) / 255.0
    sigma_vals[idx] = sigma

        
# Track which 3d pixels will be active
active_pixels = np.zeros((img_h, img_w))
row_idx = 0
col_idx = 0
for filter_idx in range(0, filter_levels):
    for row in img_filtered[filter_idx]:
        for pixel_val in row:
            if pixel_val > 0.0:
                active_pixels[row_idx, col_idx] = 1.0
            col_idx += 1                
        row_idx += 1
        col_idx = 0
    row_idx = 0


# Create 3d pixels (and keys)
c = 0
r = 0
min_scale_z = 0.002
max_scale_z = 5.0
for row in active_pixels:
    print("Row:",r)
    for pixel_val in row:
        if pixel_val > 0.0:
            color_val = 1.0
            ob = cube_at(r, c, color_val)                 
            # color animation init                                  
            mat_color = ob.data.materials[0].node_tree.nodes['Principled BSDF'].inputs[0]
            mat_color.default_value = (0.0, 0.0, 0.0, 1.0)
            mat_color.keyframe_insert(data_path='default_value', frame=0)
            # scale animation init
            ob.scale = (1.0, 1.0, 0.1)
            ob.keyframe_insert(data_path='scale',frame=0)
            frame_num = 0
            # Simga up
            for fr in range(0, filter_levels):
                # Animate color
                cval = img_filtered[fr, r, c]
                mat_color.default_value = (cval, cval, cval, 1.0)
                mat_color.keyframe_insert(data_path='default_value', frame=frame_num)
                # Animate scale
                ob.scale = (1.0, 1.0, min_scale_z + (cval * max_scale_z))
                ob.keyframe_insert(data_path='scale', frame=frame_num)
                frame_num += 1
            # Simga down
            for fr in range(0, filter_levels):
                # Animate color
                reversed_idx = (filter_levels-1)-fr
                cval = img_filtered[reversed_idx, r, c]                
                mat_color.default_value = (cval, cval, cval, 1.0)
                mat_color.keyframe_insert(data_path='default_value', frame=frame_num)
                # Animate scale
                ob.scale = (1.0, 1.0, min_scale_z + (cval * max_scale_z))
                ob.keyframe_insert(data_path='scale', frame=frame_num)
                frame_num += 1
        c += 1
    r += 1
    c = 0

# --------------------------------------- Text/extrude
rot_txt = (math.radians(0),0,0)
loc = (10, -10, 0)
bpy.ops.object.text_add(location=loc, rotation=rot_txt)
ob = bpy.context.object
ob.name = "Text_info"
ob.data.body = "Sigma: N"
bpy.context.object.data.extrude = 0.030
bpy.context.object.data.size = 2.0
bpy.context.object.data.space_character = 1.0
mat_txt = make_mat("mat_txt", (0.5, 0.5, 0.5, 1.0), 0.0, 0.500)
ob.data.materials.append(mat_txt)

# Floor plane
bpy.ops.mesh.primitive_plane_add(size=200, location=(50, 50, 0.005))
ob = bpy.context.object
ob.name = "Floor"
mat = make_mat("mat_floor", (0.0, 0.001, 0.006, 1.0), 0.0, 1.0)
ob = bpy.context.active_object
ob.data.materials.append(mat)


# Text showing sigma values
def recalculate_text(scene):
    obj = bpy.data.objects["Text_info"]
    idx = scene.frame_current
    if idx >= filter_levels:
        idx = (filter_levels-1) - scene.frame_current        
    str_val = ("Sigma: %5.2f" %(sigma_vals[idx]))
    obj.data.body = str_val

bpy.app.handlers.frame_change_pre.append(recalculate_text)

# Camera
bpy.ops.object.camera_add(location=(-1.6, -52, 17.0), \
rotation = (math.radians(77),math.radians(0),math.radians(-13)))
ob = bpy.context.active_object
ob.name = "Cam1"




