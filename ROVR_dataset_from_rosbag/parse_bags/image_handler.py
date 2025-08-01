import os
import cv2
import numpy as np
import yaml
import glob
from sensor_msgs_py import point_cloud2

class ImageHandler:
  def __init__(self, output_dir, sn_base_dir, bag_path):
      self.output_dir = output_dir
      self.image_timestamps = []
      os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)
      os.makedirs(os.path.join(output_dir, 'project'), exist_ok=True)
      os.makedirs(os.path.join(output_dir, 'depth'), exist_ok=True)

      # Initialize camera parameters
      self.camera_matrix = np.array([
          [1190.9380383925, 0.0, 955.6705012175],
          [0.0, 1190.8862851737, 540.1090098440],
          [0.0, 0.0, 1.0]
      ])
      self.dist_coeffs = np.array([
          -0.0586809591, -0.4292077180, -0.0000209962, 
          0.0000513478, -0.0282192110, 0.3687679523,
          -0.5661097302, -0.1486583365
      ])
      
      # Default extrinsic matrix
      self.extrinsic_matrix = np.eye(4)
      self.extrinsic_matrix[:3, :3] = cv2.Rodrigues(np.array([1.765*np.pi/180.0, 1.008*np.pi/180.0, 0.2521*np.pi/180.0]))[0]
      self.extrinsic_matrix[:3, 3] = np.array([-0.01681, 0, 0.01680])
      
      self.rvec = np.array([1.765*np.pi/180.0, 1.008*np.pi/180.0, 0.2521*np.pi/180.0])
      self.tvec = np.array([-0.01681, 0, 0.01680])
      # Try to load parameters from SN folder
      self._try_load_params_from_sn(sn_base_dir, bag_path)

  def process_image(self, msg, timestamp):
      """Process and save image"""
      try:
          np_arr = np.frombuffer(msg.data, np.uint8)
          img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
          filename = f"{timestamp.sec}.{timestamp.nanosec:09d}.png"
          output_path = os.path.join(self.output_dir, 'images', filename)
          cv2.imwrite(output_path, img, [cv2.IMWRITE_PNG_COMPRESSION, 3])
      except Exception as e:
          print(f"Image processing error: {str(e)}")

  def generate_proj_image(self, img_msg, pc_msg):
      """Project point cloud to image and save depth map"""
      try:
          np_arr = np.frombuffer(img_msg.data, np.uint8)
          img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

          # Process point cloud and project to image
          points_3d = self._process_pointcloud_for_projection(pc_msg)

          # Project points
          image_points, _ = cv2.projectPoints(
              points_3d,
              self.rvec,
              self.tvec,
              self.camera_matrix,
              self.dist_coeffs
          )

          image_points = image_points.squeeze()
          depth_map = np.zeros((1080, 1920), dtype=np.float32)

          for (u, v), (x, y, z) in zip(image_points, points_3d):
              u, v = int(round(u)), int(round(v))
              if 0 <= u < 1920 and 0 <= v < 1080:
                  depth = np.sqrt(x**2 + y**2 + z**2)
                  color_value = max(0, min(255, depth*5))
                  color = (0, 255 - color_value, color_value)
                  cv2.circle(img, (u,v), 2, color, -1)

                  if depth_map[v, u] == 0 or depth < depth_map[v, u]:
                      depth_map[v, u] = depth

          # Save outputs
          self._save_projection(img_msg.header.stamp, img, depth_map)

      except Exception as e:
          print(f"Projection error: {str(e)}")

  def _process_pointcloud_for_projection(self, pc_msg):
      """Convert point cloud to 3D points for projection"""
      has_timestamp = any(f.name == "timestamp" for f in pc_msg.fields)
      fields = ("x", "y", "z", "intensity", "timestamp") if has_timestamp else ("x", "y", "z", "intensity")

      pc_data = np.array(list(point_cloud2.read_points(
          pc_msg, field_names=fields, skip_nans=True
      )))

      return np.column_stack([-pc_data['y'], -pc_data['z'], pc_data['x']]).astype(np.float32)

  def _save_projection(self, stamp, img, depth_map):
      """Save projection image and depth map"""
      proj_filename = f"{stamp.sec}.{stamp.nanosec:09d}.png"
      proj_path = os.path.join(self.output_dir, 'project', proj_filename)
      cv2.imwrite(proj_path, img, [cv2.IMWRITE_PNG_COMPRESSION, 3])

      depth_filename = f"{stamp.sec}.{stamp.nanosec:09d}.png"
      depth_path = os.path.join(self.output_dir, 'depth', depth_filename)
      depth_normalized = (depth_map * 1000).astype(np.uint16)
      cv2.imwrite(depth_path, depth_normalized, [cv2.IMWRITE_PNG_COMPRESSION, 3])

  def _try_load_params_from_sn(self, sn_base_dir, bag_path):
      """Try to load camera parameters from SN folder"""
      try:
          basename = os.path.basename(bag_path)
          
          # Split filename by -
          parts = basename.split('-')
          if len(parts) < 2:
              print(f"Warning: Filename {basename} format invalid, using default parameters")
              return

          # Get device code part (second part)
          device_code = parts[1]
          
          # Check if it's numeric and has sufficient length
          if not device_code.isdigit() or len(device_code) < 4:
              print(f"Warning: Device code {device_code} invalid, using default parameters")
              return

          # Take last 4 digits and convert to int
          sn_num = int(device_code[-4:])
          print(f"Parsed device index from filename {basename}: {device_code}")

          # Build SN folder path
          sn_dir = os.path.join(sn_base_dir, str(device_code))

          if os.path.exists(sn_dir):
              # Find intrinsic files
              intrin_file = os.path.join(sn_dir, 'int.yaml')
              print(intrin_file)
              if intrin_file:
                  self.camera_matrix, self.dist_coeffs = self._load_intrinsic_params(intrin_file)
              
              # Find extrinsic files
              extrin_files = os.path.join(sn_dir, 'ext.yaml')
              if os.path.exists(extrin_files):
                  self.extrinsic_matrix, self.rvec, self.tvec = self._load_extrinsic_params(extrin_files)
                      
      except Exception as e:
          print(f"Warning: Failed to load params from SN folder, using defaults: {str(e)}")
  
  def _load_intrinsic_params(self, file_path):
      """Load camera intrinsic and distortion parameters from text file"""
      with open(file_path, 'r') as f:
          lines = f.readlines()
      
      params = {}
      for line in lines:
          if ':' in line:
              key, value = line.split(':', 1)
              params[key.strip()] = value.strip()
      
      # Build camera matrix
      camera_matrix = np.array([
          [float(params['FX']), 0.0, float(params['CX'])],
          [0.0, float(params['FY']), float(params['CY'])],
          [0.0, 0.0, 1.0]
      ])
      print(camera_matrix)
      # Build distortion coefficients (k1, k2, p1, p2, k3, k4, k5, k6)
      dist_coeffs = np.array([
          float(params['K1']), float(params['K2']),
          float(params['P1']), float(params['P2']),
          float(params['K3']), float(params['K4']),
          float(params['K5']), float(params['K6'])
      ])
      print(dist_coeffs)
      return camera_matrix, dist_coeffs

  def _load_extrinsic_params(self, file_path):
      """Load extrinsic matrix from YAML file"""
      with open(file_path, 'r') as f:
          extrinsic_data = yaml.safe_load(f)
      
      # Get rotation vector and translation vector
      rvec = np.array(extrinsic_data['lidar_to_camera']['rvec']) *np.pi/180.0
      tvec = np.array(extrinsic_data['lidar_to_camera']['tvec'])
      
      print(rvec)
      print(tvec)
      # Convert rotation vector to rotation matrix
      rotation_matrix, _ = cv2.Rodrigues(rvec)
      
      # Build 4x4 transformation matrix
      extrinsic_matrix = np.eye(4)
      extrinsic_matrix[:3, :3] = rotation_matrix
      extrinsic_matrix[:3, 3] = tvec
      
      return extrinsic_matrix, rvec, tvec
