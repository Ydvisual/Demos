# Intro screen for Enthought by Ken York 13 Aug 2019

import bpy
import math
import random

# Const
DO_BEVEL = True

# Renderer setup
exec((bpy.data.texts["setup_render"]).as_string())


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

# ------------------------------------------------------------- Select and delete all
# Delete all objects (whether hidden or not)
for obj in bpy.context.scene.objects:
    bpy.data.objects.remove(obj)



# ---------------------------------------------------------------- Materials
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat)

mat_metal1 = make_mat("m_metal1", color=(0.5, 0.5, 0.5, 1.0), metal=1.0, rough=0.250)
mat_table = make_mat("m_TABLE", color=(0.0, 0.04, 0.22, 1.0), metal=0.0, rough=0.120)
mat_ec1  = make_mat("m_EC1", color=(0.0, 0.048, 0.176, 1.0), metal=0.0, rough=0.320)
mat_ec2  = make_mat("m_EC2", color=(1.0, 1.0, 1.0, 1.0), metal=0.0, rough=0.320)
mat_ec3  = make_mat("m_EC3", color=(0.156, 0.348, 0.89, 1.0), metal=0.0, rough=0.320)
mat_ec4  = make_mat("m_EC4", color=(0.0, 0.038, 0.126, 1.0), metal=0.0, rough=0.320)
mat_tile  = make_mat("m_TILE", color=(0.0, 0.1, 1.0, 1.0), metal=1.0, rough=0.320)
mat_txt  = make_mat("m_TXT", color=(1.0, 1.0, 1.0, 1.0), metal=0.0, rough=0.500)


# ------------------------------------------------------------------ Table
table_sz = 8.0
pz = -table_sz * 0.5
bpy.ops.mesh.primitive_cube_add(size=table_sz, location=(0, 0, pz))
ob = bpy.context.active_object
ob.name = "table"
ob.data.materials.append(mat_table)



# ------------------------------------------------------------ Enthought cube(s)
cube_sz = 1.0
epx = -2.3
epy = 0
epz = (cube_sz * 0.5) + 0.5
rot_cube = (math.radians(-16.5),math.radians(15.9),math.radians(-137))
bpy.ops.mesh.primitive_cube_add(size=1, location=(epx, 0, epz),rotation=rot_cube)
ob = bpy.context.active_object
ob.name = "ecube"
ob.data.materials.append(mat_ec1)
ob.data.materials.append(mat_ec2)
ob.data.materials.append(mat_ec3)
ob.data.materials.append(mat_ec4)

# Cube to 3x3 segs
bpy.ops.object.modifier_add(type='REMESH')
bpy.context.object.modifiers["Remesh"].mode = 'BLOCKS'
bpy.context.object.modifiers["Remesh"].octree_depth = 2
bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Remesh") #convertToPoly()


# ------------------------------------- Enthought cube color
idx = 0
for p in ob.data.polygons:
    m_idx = p.material_index
    if idx in (10, 21, 22, 30, 38, 39, 43, 46, 47, 49, 51, 52, 53):
        p.material_index = 1
    elif idx in (12, 15, 18, 34, 44):
        p.material_index = 2
    else:
        p.material_index = 0
    idx += 1

if DO_BEVEL:
    bpy.ops.object.modifier_add(type='BEVEL')
    bpy.context.object.modifiers["Bevel"].width = 0.002
    bpy.context.object.modifiers["Bevel"].material = 4 # Liner
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Bevel")
    
    
# --------------------------------------- ENGHOUGHT Text/extrude
rot_txt = (math.radians(90),0,0)
loc = (epx+0.7, epy, epz)
bpy.ops.object.text_add(location=loc, rotation=rot_txt)
ob = bpy.context.object
ob.name = "txt_enthought"
ob.data.body = "ENTHOUGHT"
bpy.context.object.data.extrude = 0.030
bpy.context.object.data.size = 0.50
bpy.context.object.data.space_character = 1.4
#bpy.context.object.data.bevel_depth = 0.015
#bpy.context.object.data.bevel_resolution = 1
ob.data.materials.append(mat_txt)


# --------------------------------------- "Transform Science" Text/extrude
rot_txt = (math.radians(90),0,0)
loc = (epx+1.3, epy, epz-0.5)
bpy.ops.object.text_add(location=loc, rotation=rot_txt)
ob = bpy.context.object
ob.name = "txt_xform_science"
ob.data.body = "Transform Science"
bpy.context.object.data.extrude = 0.015
bpy.context.object.data.size = 0.35
bpy.context.object.data.space_character = 1.0
ob.data.materials.append(mat_txt)
# Animate motion (Y)
action = bpy.data.actions.new("txt motion_y")
action.fcurves.new("location", index=1)
action.fcurves[0].extrapolation = 'CONSTANT'
fr_start1 = 320
fr_end1 = 400
action.fcurves[0].keyframe_points.insert(fr_start1, -10)
action.fcurves[0].keyframe_points.insert(fr_end1, 0)
kpts = action.fcurves[0].keyframe_points
for kp in kpts:
    kp.interpolation = 'BEZIER'
#
ob.animation_data_create()
ob.animation_data.action=action



# ------------------------------------------------------------------------------------ Tiles
px0 = -3.5
py0 = -3.5
r1 = 0.250
y_spacing = (3.0/2.0) * r1
sep_fac = 1.1
tile_h = 0.350 #0.050
pz0 = 0.0
pz1 = (-tile_h * 0.500) + 0.040
rot = (0,0,math.radians(0))
#
def hex_tile_at(name, idx_x, idx_y):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=r1, depth=tile_h, \
        end_fill_type='NGON')
    bpy.ops.object.shade_flat()
    ob = bpy.context.active_object
    width = ob.dimensions.x
    if (y % 2 == 0):
        px = px0 + ((idx_x * width) * sep_fac)
    else:
        px = px0 + (((idx_x * width) + (width * 0.5)) * sep_fac)
    py = py0 + ((idx_y * y_spacing) * sep_fac)
    
            
    ob.location = (px, py, pz0)
    ob.name = name
    ob.data.materials.append(mat_tile)

    # Animate motion (X)
    action = bpy.data.actions.new("tile motion_x")
    action.fcurves.new("location", index=0)
    action.fcurves[0].extrapolation = 'CONSTANT'
    fr_start1 = 6*(13-idx_x) + random.randint(0,20)
    fr_end1 = fr_start1 + 150
    action.fcurves[0].keyframe_points.insert(fr_start1, (px-8))
    action.fcurves[0].keyframe_points.insert(fr_end1, px)
    kpts = action.fcurves[0].keyframe_points
    for kp in kpts:
        kp.interpolation = 'BEZIER'
    #
    ob.animation_data_create()
    ob.animation_data.action=action
    
    # Animate motion (Z)
    action.fcurves.new("location", index=2)
    action.fcurves[1].extrapolation = 'CONSTANT'
    fr_start2 = fr_end1 + random.randint(0,60)
    fr_end2 = fr_start2 + random.randint(20,50)
    action.fcurves[1].keyframe_points.insert(fr_start2, pz0)
    action.fcurves[1].keyframe_points.insert(fr_end2, pz1)
    kpts = action.fcurves[1].keyframe_points
    for kp in kpts:
        kp.interpolation = 'BEZIER'
    #
    ob.animation_data_create()
    ob.animation_data.action=action
    
        
# 15x18
for x in range(0,15):
    for y in range(0,18):
        r = random.randint(0,100)
        if (r < 60):
            hex_tile_at("xt.000", x, y)
            

# ------------------------------------------------------------------------ Cam
bpy.ops.object.camera_add(location=(-3.2, -9.5, 2.4), \
rotation = (math.radians(77.0),math.radians(0),math.radians(-17.0)))
ob = bpy.context.active_object
ob.name = "Cam1"
bpy.context.object.data.dof.use_dof = True
bpy.context.object.data.dof.focus_object = bpy.data.objects["txt_enthought"]
bpy.context.object.data.dof.aperture_fstop = 0.3


