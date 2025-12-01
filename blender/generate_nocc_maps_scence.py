
import blenderproc as bproc
import numpy as np
import sys
from pathlib import Path
import os

# import debugpy
# debugpy.listen(5678)
# debugpy.wait_for_client()

bproc.init()
# define directory to the blender_models folder
blender_models_dir = Path("blender_models")

# get a list of file names ending with .blend from blender_models_dir
blend_files = list(blender_models_dir.glob("*.blend"))

# get file names starts with "back_ground"
background_files = [f for f in blend_files if f.name.startswith("back_ground")]

# get file names starts with "table"
table_files = [f for f in blend_files if f.name.startswith("table")]

# load objects to the scene
# Note: load_blend expects a string path, not a list
# Load the first background file if available
if background_files:
    objs = bproc.loader.load_blend(str(background_files[0]))
    print(f"Object loaded from {background_files[0].name}") # for debug in blender
else:
    print("No background files found!")
    sys.exit(1)

#remove the default cube
# for obj in bproc.object.get_all_mesh_objects():
#     if obj.get_name() == "Cube":
#         bproc.object.remove(obj)
# # Calculate the center point of all loaded objects
# poi = bproc.object.compute_poi(objs)

# define a light and set its location and energy level
# light = bproc.types.Light()
# light.set_type("POINT")
# light.set_location([5, -5, 5])
# light.set_energy(1000)
# print("light setup done ") # for debug in blender
# # change floor color to white

# # Find the floor object
# floor = bproc.object.find_by_name("Floor")[0]

# # Create a new material
# mat = bproc.material.create("floor_material")
# mat.set_principled_shader_value("Base Color", [0.2, 0.7, 0.3, 1.0])   # RGBA

# # Assign material to the floor
# floor.replace_materials(mat)
# print("floor material setup done ") # for debug in blender

# # Sample five camera poses
# for i in range(5):
#     # Sample random camera location around the object
#     location = bproc.sampler.sphere([0, 0, 0], radius=1, mode="SURFACE")
#     # Compute rotation based on vector going from location towards the point of interest
#     rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - location)
#     # Add homog cam pose based on location an rotation
#     cam2world_matrix = bproc.math.build_transformation_mat(location, rotation_matrix)
#     bproc.camera.add_camera_pose(cam2world_matrix)

# print("camera poses sampling done ") # for debug in blender

# # Render RGB images
# data = bproc.renderer.render()
# # Render NOCS
# data.update(bproc.renderer.render_nocs())

# print("NOCS rendering done ") # for debug in blender

# # Write the rendering into an hdf5 file
# bproc.writer.write_hdf5("output/", data)

# print("Writing to HDF5 done ") # for debug in blender