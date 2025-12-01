
import blenderproc as bproc
import numpy as np
import sys
from pathlib import Path
import os

DEBUG = True

bproc.init()

# Create visual coordinate frame axes at world origin
def create_coordinate_frame(length=1.0, radius=0.02):
    """Create X, Y, Z axes at world origin for visualization"""
    import bpy
    
    # X-axis (Red)
    x_axis = bproc.object.create_primitive('CYLINDER', scale=[radius, radius, length/2])
    x_axis.set_location([length/2, 0, 0])
    x_axis.set_rotation_euler([0, np.pi/2, 0])
    x_mat = bproc.material.create('x_axis_mat')
    x_mat.set_principled_shader_value("Base Color", [1, 0, 0, 1])  # Red
    x_mat.set_principled_shader_value("Metallic", 0.8)
    x_axis.replace_materials(x_mat)
    
    # Y-axis (Green)
    y_axis = bproc.object.create_primitive('CYLINDER', scale=[radius, radius, length/2])
    y_axis.set_location([0, length/2, 0])
    y_axis.set_rotation_euler([np.pi/2, 0, 0])
    y_mat = bproc.material.create('y_axis_mat')
    y_mat.set_principled_shader_value("Base Color", [0, 1, 0, 1])  # Green
    y_mat.set_principled_shader_value("Metallic", 0.8)
    y_axis.replace_materials(y_mat)
    
    # Z-axis (Blue)
    z_axis = bproc.object.create_primitive('CYLINDER', scale=[radius, radius, length/2])
    z_axis.set_location([0, 0, length/2])
    z_mat = bproc.material.create('z_axis_mat')
    z_mat.set_principled_shader_value("Base Color", [0, 0, 1, 1])  # Blue
    z_mat.set_principled_shader_value("Metallic", 0.8)
    z_axis.replace_materials(z_mat)
    
    return [x_axis, y_axis, z_axis]

# Create coordinate frame at origin
axes = create_coordinate_frame(length=2.0, radius=0.05)
print("Global coordinate frame created at origin")

# define directory to the blender_models folder
blender_models_dir = Path("blender_models")

# get a list of file names ending with .blend from blender_models_dir
blend_files = list(blender_models_dir.glob("table_2.blend"))

# load objects to the scene
# Note: load_blend expects a string path, not a list
# Load the first background file if available
if blend_files:
    objs = bproc.loader.load_blend(str(blend_files[0]))
    print(f"Object loaded from {blend_files[0].name}") # for debug in blender

    # define a light and set its location and energy level
    light = bproc.types.Light()
    light.set_type("POINT")
    light.set_location([1, -1, 5])
    light.set_energy(1000)

    # define the camera resolution
    bproc.camera.set_resolution(512, 512)
    
    # Set the camera to isometric view
    # For isometric view, camera should be at equal distance from each axis
    # Common isometric angle: 35.264° from horizontal
    distance = 5
    # Position: equal components on X, Y, and Z (diagonal)
    cam_location = np.array([distance, -distance, distance]) / np.sqrt(3)
    
    # Look at origin from this position
    rotation_matrix = bproc.camera.rotation_from_forward_vec(-cam_location)
    cam_pose = bproc.math.build_transformation_mat(cam_location, rotation_matrix)
    
    # Alternative: Use orthographic projection for true isometric view
    # import bpy
    # bpy.context.scene.camera.data.type = 'ORTHO'
    # bpy.context.scene.camera.data.ortho_scale = 5.0
    
    bproc.camera.add_camera_pose(cam_pose)

    if DEBUG:
                # render the whole pipeline
        data = bproc.renderer.render()
        # write the data to a .hdf5 container
        bproc.writer.write_hdf5("output/", data)
    else:
        bproc.renderer.set_max_samples(128) # production
else:
    print("No blend files found!")
    sys.exit(1)