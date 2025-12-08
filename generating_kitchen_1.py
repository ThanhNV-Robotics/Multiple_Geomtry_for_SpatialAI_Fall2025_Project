
import blenderproc as bproc
import numpy as np
import sys
from pathlib import Path
from scipy.spatial.transform import Rotation as R

import os
import bpy

bproc.init()

# Define a function that samples the pose of a given sphere
def sample_pose(obj: bproc.types.MeshObject):
    obj.set_location(np.random.uniform([0, 0, 1], [0, 0, 1.01]))
    obj.set_rotation_euler(bproc.sampler.uniformSO3())

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent.resolve()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))


DEBUG = True # turn to False to render

# Uncomment this to show the global coordinate frame
# if DEBUG: # show the coordinate frame for debugging
#     # Create coordinate frame at origin
#     axes = helper.create_coordinate_frame(length=2.0, radius=0.05)
#     print("Global coordinate frame created at origin")

# Init camera pose
# calibrate this in blender to get the right view first
camera_pos = np.array([0.22012, -2.0731, 1.8627])
camera_euler = np.array([71.125, 0.68952, 1.1758]) # in degree
camera_rotation = R.from_euler('xyz', camera_euler, degrees=True).as_matrix()

# define a light and set its location and energy level
light = bproc.types.Light()
light.set_type("POINT")
light.set_location([1, -1, 3])
light.set_energy(500)

# kitchen blender file
# background_blend_files = Path("blender_models/objects/table_3.blend")
# print(f"Looking for blend files in: {background_blend_files}")
# define directory to the blender_models folder
background_blend_files = Path("blender_models/background/background_kitchen_1.blend")

# Setting for object loading
object_dir = Path("blender_models/objects/")
# Find all blend files in the object directory
#object_blend_files = list(object_dir.glob("*.blend"))
object_blend_files = Path("blender_models/objects/object_1.blend")
# Setting default object pose
object_pos = np.array([0.0, 0.0, 0.905])
object_euler = np.array(np.deg2rad([90, 0.0, 90])) # in degree


print(f"Loading object from {background_blend_files}") # for debug in blender
bg_objs = bproc.loader.load_blend(str(background_blend_files))

target_obj = bproc.loader.load_blend(str(object_blend_files)) # load the first object as target    

# # Filter to only get mesh objects (exclude cameras, lights, etc.)
# target_obj = [obj for obj in target_obj if isinstance(obj, bproc.types.MeshObject)]



# define the camera resolution
bproc.camera.set_resolution(512, 512)

# Set the camera to isometric view
# For isometric view, camera should be at equal distance from each axis
# distance = 2.5
# # Position: equal components on X, Y, and Z (diagonal)
# cam_location = np.array([0.0*distance, -1.0*distance, 1.5*distance]) / np.sqrt(3)    
# # Look at origin from this position
# rotation_matrix = bproc.camera.rotation_from_forward_vec(-cam_location)
# cam_pose = bproc.math.build_transformation_mat(cam_location, rotation_matrix)

#Sample pose the target object
# bproc.object.sample_poses(
# target_obj,
# sample_pose_func=sample_pose)

cam_pose = bproc.math.build_transformation_mat(camera_pos, camera_rotation)

# for obj in target_obj:
#     obj.enable_rigidbody(active = True)

# # set background object to passive - filter to only mesh objects
# for obj in bg_objs:
#     if isinstance(obj, bproc.types.MeshObject):
#         obj.enable_rigidbody(active = False, collision_shape="MESH")

target_obj[0].set_location(object_pos)
target_obj[0].set_rotation_euler(object_euler)
# Alternative: Use orthographic projection for true isometric view
# import bpy
# bpy.context.scene.camera.data.type = 'ORTHO'
# bpy.context.scene.camera.data.ortho_scale = 5.0

bproc.camera.add_camera_pose(cam_pose)

if DEBUG:
    #bproc.object.simulate_physics_and_fix_final_poses(min_simulation_time=0.2, max_simulation_time=0.5, check_object_interval=0.3)
    # render the whole pipeline
    data = bproc.renderer.render()
    # write the data to a .hdf5 container
    bproc.writer.write_hdf5("output/", data)
else:
    bproc.renderer.set_max_samples(128) # production