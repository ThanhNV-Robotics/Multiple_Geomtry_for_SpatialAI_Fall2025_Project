import blenderproc as bproc
import argparse
import os
from pathlib import Path
bproc.init()

# define a light and set its location and energy level
light = bproc.types.Light()
light.set_type("POINT")
light.set_location([5, -5, 5])
light.set_energy(1000)

background_blend_files = Path("blender_models/objects/object_2.blend")
print(f"Loading object from {background_blend_files}") # print for debug
# load the kitchen background
test_object = bproc.loader.load_blend(str(background_blend_files))

# Sample five camera poses
for i in range(2):
    # Sample random camera location around the object
    location = bproc.sampler.sphere([0, 0, 0], radius=2, mode="SURFACE")
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