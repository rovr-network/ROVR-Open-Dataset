import os
import numpy as np
from sensor_msgs_py import point_cloud2

class PointCloudHandler:
  def __init__(self, output_dir):
      self.output_dir = output_dir
      os.makedirs(os.path.join(output_dir, 'pointclouds'), exist_ok=True)

  def process_pointcloud(self, msg, timestamp):
      """Process and save point cloud"""
      try:
          has_timestamp = any(f.name == "timestamp" for f in msg.fields)
          fields = ("x", "y", "z", "intensity", "timestamp") if has_timestamp else ("x", "y", "z", "intensity")

          pc_data = np.array(list(point_cloud2.read_points(
              msg, field_names=fields, skip_nans=True
          )))

          self._save_pointcloud(pc_data, has_timestamp, timestamp)
      except Exception as e:
          print(f"Pointcloud processing error: {str(e)}")

  def _save_pointcloud(self, pc_data, has_timestamp, timestamp):
      """Save point cloud to PCD file"""
      filename = f"{timestamp.sec}.{timestamp.nanosec:09d}.pcd"
      output_path = os.path.join(self.output_dir, 'pointclouds', filename)

      with open(output_path, 'w') as f:
          if has_timestamp:
              f.write("FIELDS x y z intensity timestamp\nSIZE 4 4 4 4 8\nTYPE F F F F D\nCOUNT 1 1 1 1 1\n")
          else:
              f.write("FIELDS x y z intensity\nSIZE 4 4 4 4\nTYPE F F F F\nCOUNT 1 1 1 1\n")

          f.write(f"WIDTH {len(pc_data)}\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\nPOINTS {len(pc_data)}\nDATA ascii\n")

          for point in pc_data:
              if has_timestamp:
                  f.write(f"{point['x']:.6f} {point['y']:.6f} {point['z']:.6f} {point['intensity']:.6f} {point['timestamp']:.8f}\n")
              else:
                  f.write(f"{point['x']:.6f} {point['y']:.6f} {point['z']:.6f} {point['intensity']:.6f}\n")