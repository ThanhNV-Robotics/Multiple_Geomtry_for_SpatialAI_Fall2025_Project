import blenderproc as bproc
import numpy as np
from pathlib import Path
bproc.init()

# define a light and set its location and energy level
light = bproc.types.Light()
light.set_type("POINT")
light.set_location([5, -5, 5])
light.set_energy(1000)

background_blend_files = Path("blender_models/objects/normalized_cube.blend")
print(f"Loading object from {background_blend_files}") # print for debug
# axes = helper.create_coordinate_frame(length=2.0, radius=0.05)
# print("Global coordinate frame created at origin")
# load the kitchen background
#test_object = bproc.loader.load_blend(str(background_blend_files))
test_object = bproc.loader.load_blend(str(background_blend_files))
# mesh_objects = [obj for obj in test_object if isinstance(obj, bproc.types.MeshObject)] 
bproc.renderer.enable_depth_output(activate_antialiasing=False)
# Sample five camera poses
for i in range(1):
    # Sample random camera location around the object
    #location = bproc.sampler.sphere([0, 0, 0], radius=5, mode="SURFACE")
    location = np.array([3.0, 3.0, 3.0])
    print(f"Camera location: {location}")
    # Compute rotation based on vector going from location towards the location of the ShapeNet object
    rotation_matrix = bproc.camera.rotation_from_forward_vec(test_object[0].get_location() - location)

    # Add homog cam pose based on location an rotation
    cam2world_matrix = bproc.math.build_transformation_mat(location, rotation_matrix)
    bproc.camera.add_camera_pose(cam2world_matrix)

# Render RGB images
data = bproc.renderer.render()
# Render NOCS
data.update(bproc.renderer.render_nocs(output_key="nocs"))

# write the data to a .hdf5 container
bproc.writer.write_hdf5("output/", data)