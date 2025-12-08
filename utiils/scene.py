
import blenderproc as bproc
import numpy as np
import sys
from pathlib import Path
from scipy.spatial.transform import Rotation as R

class scene:
    def __init__(self):
        #-------Set up camera and light-------#
        # Init camera pose
        self.camera_pos = np.array([0.22012, -2.0731, 1.8627])
        self.camera_euler = np.array([71.125, 0.68952, 1.1758]) # in degree
        self.camera_rotation = R.from_euler('xyz', self.camera_euler, degrees=True).as_matrix()
        self.cam_pose = bproc.math.build_transformation_mat(self.camera_pos, self.camera_rotation)
        bproc.camera.add_camera_pose(self.cam_pose)
        # define the camera resolution
        bproc.camera.set_resolution(512, 512)