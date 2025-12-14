
import blenderproc as bproc
import numpy as np
import sys
from pathlib import Path
from scipy.spatial.transform import Rotation as R

import os


# import debugpy # for debugging
# debugpy.listen(5678)
# debugpy.wait_for_client()

bproc.init()

# Define a function that samples the pose of a given sphere
def sample_pose(obj: bproc.types.MeshObject):
    obj.set_location(np.random.uniform([-0.4, -0.4, 0.3], [0.4, 0.4, 0.5]))
    obj.set_rotation_euler(bproc.sampler.uniformSO3())

def generate_grid ():
    X = np.linspace(-0.3, 0.3, 5)
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

number_of_renderings = 1 # number of images to render
# #-------Set up camera and light-------#
# K = np.array([[23, 0, 0],
#               [0, 23, 0],
#               [0,   0, 1]])
# bproc.camera.set_intrinsics_from_K_matrix(K, image_width=512, image_height=512)
# Init camera pose
init_camera_pos_x = 0.307
init_camera_pos_y = -1.0
init_camera_pos_z = 1.41

camera_pos_x_range = 0.2
camera_pos_y_range = 0.2
camera_pos_z_range = 0.1

init_camera_euler_x = 71.125
init_camera_euler_y = 0.68952
init_camera_euler_z = 1.1758

camera_euler_x_range = 5.0
camera_euler_y_range = 5.0
camera_euler_z_range = 10.0

number_of_sampling_camera_poses = 10
camera_pos_x_samples = np.linspace(init_camera_pos_x - camera_pos_x_range, init_camera_pos_x + camera_pos_x_range, number_of_sampling_camera_poses)
camera_pos_y_samples = np.linspace(init_camera_pos_y - camera_pos_y_range, init_camera_pos_y + camera_pos_y_range, number_of_sampling_camera_poses)
camera_pos_z_samples = np.linspace(init_camera_pos_z - camera_pos_z_range, init_camera_pos_z + camera_pos_z_range, number_of_sampling_camera_poses)

camera_euler_x_samples = np.linspace(init_camera_euler_x - camera_euler_x_range, init_camera_euler_x + camera_euler_x_range, number_of_sampling_camera_poses)
camera_euler_y_samples = np.linspace(init_camera_euler_y - camera_euler_y_range, init_camera_euler_y + camera_euler_y_range, number_of_sampling_camera_poses)
camera_euler_z_samples = np.linspace(init_camera_euler_z - camera_euler_z_range, init_camera_euler_z + camera_euler_z_range, number_of_sampling_camera_poses)

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
background_blend_files = Path("blender_models/background/background_woodfloor.blend")
print(f"Loading object from {background_blend_files}") # print for debug
# load the kitchen background
ground = bproc.loader.load_blend(str(background_blend_files))
ground[0].enable_rigidbody(active=False, collision_shape="MESH")

# Setting for object loading
object_dir = Path("blender_models/objects/")
# Find all blend files in the object directory
object_blend_files = list(object_dir.glob("*.blend"))
print(f"Found {len(object_blend_files)} object blend files.") # print for debug
# randomly select 3 objects to load

object_idx_list = range(len(object_blend_files))
# randomly select 3 objects
number_of_objects_to_load = 6
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
    for mesh_obj in target_mesh_obj:
        mesh_obj.enable_rigidbody(active=True)

# arrange the selected objects on the table
bproc.object.sample_poses(
target_mesh_obj,
sample_pose_func=sample_pose)


render_cam_location =[]
render_cam_euler =[]
render_light_energy =[]

#location = bproc.sampler.sphere([0, 0, 0], radius=5, mode="SURFACE")
location = np.array([1.0, 1.0, 1.0])
print(f"Camera location: {location}")
# Compute rotation based on vector going from location towards the location of the ShapeNet object
rotation_matrix = bproc.camera.rotation_from_forward_vec(ground[0].get_location() - location)        
# Add homog cam pose based on location an rotation
cam2world_matrix = bproc.math.build_transformation_mat(location, rotation_matrix)
bproc.camera.add_camera_pose(cam2world_matrix)
bproc.object.simulate_physics_and_fix_final_poses(min_simulation_time=5, max_simulation_time=20, check_object_interval=1)
if DEBUG:
    
    #for _ in range(number_of_renderings):

        # # 1st: render rgb images only
        # # Sample a random camera location around the object
        # camera_location_random = np.random.choice(camera_pos_x_samples, 1)[0], np.random.choice(camera_pos_y_samples, 1)[0], np.random.choice(camera_pos_z_samples, 1)[0]
        # camera_euler_random = np.random.choice(camera_euler_x_samples, 1)[0], np.random.choice(camera_euler_y_samples, 1)[0], np.random.choice(camera_euler_z_samples, 1)[0]
        # camera_rotation_random = R.from_euler('xyz', camera_euler_random, degrees=True).as_matrix()
        # cam2world_matrix = bproc.math.build_transformation_mat(camera_location_random, camera_rotation_random)
        
    # set a randome light energy level
    light.set_energy(np.random.choice(light_energy_samples, 1)[0])


    data_rgb = bproc.renderer.render()
    # Run the simulation and fix the poses of the spheres at the end
    
    bproc.writer.write_hdf5("output/rgb", data_rgb)   
         
    # # render depth maps
    # # activate depth rendering
    # # delete kitchen background    
    # bproc.object.delete_multiple(bg_objs, remove_all_offspring=False)
    # # load wall background only for depth rendering
    # # background_blend_files = Path("blender_models/background/background_wall.blend")
    # # bg_objs = bproc.loader.load_blend(str(background_blend_files))
    # # print(f"Loading object from {background_blend_files}") # print for debug
    # bproc.renderer.enable_depth_output(activate_antialiasing=False, antialiasing_distance_max=0.5)
    # bproc.renderer.set_noise_threshold(0.01)  # this is the default value
    # for i in range(number_of_renderings):
    #     # set camera pose
    #     camera_location_random = render_cam_location[i]
    #     camera_euler_random = render_cam_euler[i]
    #     camera_rotation_random = R.from_euler('xyz', camera_euler_random, degrees=True).as_matrix()
    #     cam2world_matrix = bproc.math.build_transformation_mat(camera_location_random, camera_rotation_random)
    #     bproc.camera.add_camera_pose(cam2world_matrix)

    #     # set light energy
    #     light.set_energy(render_light_energy[i])

    #     data_depth = bproc.renderer.render()
    #     bproc.writer.write_hdf5("output/", data_depth, append_to_existing_output=False)


    # delete background to render nocs and segmentation only for the target objects
    bproc.object.delete_multiple(ground, remove_all_offspring=False) # delete kitchen background    
    bproc.renderer.enable_depth_output(activate_antialiasing=False, antialiasing_distance_max=0.5)
    bproc.renderer.enable_segmentation_output(map_by=["name","instance"])

    data_nocs_seg = bproc.renderer.render()
    data_nocs_seg.update(bproc.renderer.render_nocs())
    bproc.writer.write_hdf5("output/nocs", data_nocs_seg, append_to_existing_output=True)        

else:
    bproc.renderer.set_max_samples(128) # production