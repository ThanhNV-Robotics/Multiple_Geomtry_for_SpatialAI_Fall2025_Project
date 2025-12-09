
import blenderproc as bproc
import numpy as np
import sys
from pathlib import Path
from scipy.spatial.transform import Rotation as R

import os
import bpy

# import debugpy # for debugging
# debugpy.listen(5678)
# debugpy.wait_for_client()

bproc.init()

# Define a function that samples the pose of a given sphere
def sample_pose(obj: bproc.types.MeshObject):
    obj.set_location(np.random.uniform([-0.4, -0.3, 0.905], [0.4, 0.3, 0.905]))
    obj.set_rotation_euler(bproc.sampler.uniformSO3())

def generate_grid ():
    X = np.linspace(-0.4, 0.4, 5)
    Y = np.linspace(-0.22, 0.22, 5)
    x,y = np.meshgrid(X, Y)
    return x,y

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

number_of_renderings = 3 # number of images to render
#-------Set up camera and light-------#
# Init camera pose
init_camera_pos_x = 0.22012
init_camera_pos_y = -2.0731
init_camera_pos_z = 1.8627

camera_pos_x_range = 0.2
camera_pos_y_range = 0.2
camera_pos_z_range = 0.2

init_camera_euler_x = 71.125
init_camera_euler_y = 0.68952
init_camera_euler_z = 1.1758

camera_euler_x_range = 10.0
camera_euler_y_range = 10.0
camera_euler_z_range = 10.0

camera_pos_x_samples = np.linspace(init_camera_pos_x - camera_pos_x_range, init_camera_pos_x + camera_pos_x_range, number_of_renderings)
camera_pos_y_samples = np.linspace(init_camera_pos_y - camera_pos_y_range, init_camera_pos_y + camera_pos_y_range, number_of_renderings)
camera_pos_z_samples = np.linspace(init_camera_pos_z - camera_pos_z_range, init_camera_pos_z + camera_pos_z_range, number_of_renderings)

camera_euler_x_samples = np.linspace(init_camera_euler_x - camera_euler_x_range, init_camera_euler_x + camera_euler_x_range, number_of_renderings)
camera_euler_y_samples = np.linspace(init_camera_euler_y - camera_euler_y_range, init_camera_euler_y + camera_euler_y_range, number_of_renderings)
camera_euler_z_samples = np.linspace(init_camera_euler_z - camera_euler_z_range, init_camera_euler_z + camera_euler_z_range, number_of_renderings)

camera_pos_init = np.array([init_camera_pos_x, init_camera_pos_y, init_camera_pos_z])
camera_euler = np.array([init_camera_euler_x, init_camera_euler_y, init_camera_euler_z]) # in degree

# define the camera resolution
bproc.camera.set_resolution(512, 512)

# define a light and set its location and energy level
light = bproc.types.Light()
light.set_type("POINT")
light.set_location([1, -1, 3])
light.set_energy(500)

light_energy_samples = np.linspace(200, 800, number_of_renderings)

# kitchen blender file
# define directory to the blender_models folder
background_blend_files = Path("blender_models/background/background_kitchen_1.blend")
print(f"Loading object from {background_blend_files}") # print for debug
# load the kitchen background
bg_objs = bproc.loader.load_blend(str(background_blend_files))


# Setting for object loading
object_dir = Path("blender_models/objects/")
# Find all blend files in the object directory
object_blend_files = list(object_dir.glob("*.blend"))
print(f"Found {len(object_blend_files)} object blend files.") # print for debug
# randomly select 3 objects to load

object_idx_list = range(len(object_blend_files))
# randomly select 3 objects
number_of_objects_to_load = 3
selected_idx = np.random.choice(object_idx_list, size=number_of_objects_to_load, replace=False)

print(f"Total selected mesh objects: {len(object_idx_list)}") # print for debug

x_pos_gen, y_pos_gen = generate_grid()
x_pos = np.random.choice(x_pos_gen.flatten(), number_of_objects_to_load, replace=False)
y_pos = np.random.choice(y_pos_gen.flatten(), number_of_objects_to_load, replace=False)

target_mesh_obj = []

for idx in range(len(selected_idx)):
    obj_blend_file = object_blend_files[selected_idx[idx]]
    print(f"Loading object from {obj_blend_file}") # print for debug in blender
    target_blend_obj = bproc.loader.load_blend(str(obj_blend_file)) # load the object
    
    # Filter to only get mesh objects (exclude cameras, lights, etc.)
    mesh_objects = [obj for obj in target_blend_obj if isinstance(obj, bproc.types.MeshObject)]    
    # Add mesh objects to target list
    for mesh_obj in mesh_objects:
        target_mesh_obj.append(mesh_obj)
    
    # Set object location from the generated grid
    for mesh_obj in mesh_objects:
        mesh_obj.set_location([x_pos[idx], y_pos[idx], 0.905]) # set on the table height

# # arrange the selected objects on the table
# bproc.object.sample_poses(
# target_mesh_obj,
# sample_pose_func=sample_pose)



if DEBUG:
    # bproc.object.delete_multiple(bg_objs, remove_all_offspring=False) # delete kitchen background
    # Only load rgb image
    for _ in range(number_of_renderings):
        # Sample a random camera location around the object
        camera_location_random = np.random.choice(camera_pos_x_samples, 1)[0], np.random.choice(camera_pos_y_samples, 1)[0], np.random.choice(camera_pos_z_samples, 1)[0]
        camera_euler_random = np.random.choice(camera_euler_x_samples, 1)[0], np.random.choice(camera_euler_y_samples, 1)[0], np.random.choice(camera_euler_z_samples, 1)[0]
        camera_rotation_random = R.from_euler('xyz', camera_euler_random, degrees=True).as_matrix()
        cam2world_matrix = bproc.math.build_transformation_mat(camera_location_random, camera_rotation_random)

        # set a randome light energy level
        light.set_energy(np.random.choice(light_energy_samples, 1)[0])

        bproc.camera.add_camera_pose(cam2world_matrix)
        data = bproc.renderer.render()
        #data.update(bproc.renderer.render_nocs())
        # write the data to a .hdf5 container
        bproc.writer.write_hdf5("output/", data)
    

else:
    bproc.renderer.set_max_samples(128) # production