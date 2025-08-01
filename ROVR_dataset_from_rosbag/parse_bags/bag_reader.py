import os
import queue
import numpy as np
import cv2
from rosbag2_py import SequentialReader, StorageOptions, ConverterOptions
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
from sensor_msgs.msg import PointCloud2, CompressedImage, Imu
from sensor_msgs_py import point_cloud2
from .image_handler import ImageHandler
from .pointcloud_handler import PointCloudHandler
from .gnss_handler import GNSSHandler
from .imu_handler import IMUHandler

class Ros2BagProcessor:
  def __init__(self, bag_path, output_dir, sn_base_dir):
      self.bag_path = bag_path
      self.output_dir = output_dir
      self.image_queue = queue.Queue()
      self.pc_queue = queue.Queue()

      self.time_sync = False
      self.time_diff = 0.09
      self.capture_diff_thresh = 0.048
      self.valid_count = 0
      self.total_count = 0
      self.capture_diff = 0

      # Initialize handlers
      self.image_handler = ImageHandler(output_dir, sn_base_dir, bag_path)
      self.pc_handler = PointCloudHandler(output_dir)
      self.gnss_handler = GNSSHandler()
      self.imu_handler = IMUHandler(output_dir)

  def process_bag(self):
      """Main method to process the ROS2 bag"""
      reader = SequentialReader()
      storage_options = StorageOptions(uri=self.bag_path, storage_id='sqlite3')
      converter_options = ConverterOptions('', '')
      reader.open(storage_options, converter_options)

      topic_types = reader.get_all_topics_and_types()
      type_map = {topic.name: topic.type for topic in topic_types}

      while reader.has_next():
          topic, data, timestamp = reader.read_next()
          msg_type = get_message(type_map[topic])
          msg = deserialize_message(data, msg_type)

          if 'compressed' in topic.lower():
              self.image_queue.put(msg)
          elif 'pointcloud' in topic.lower():
              self.pc_queue.put(msg)
          elif 'nmea_sentence' in topic.lower():
              self.gnss_handler.process_gprmc(msg)
          elif 'imu' in topic.lower():
              self.imu_handler.process_imu(msg)

          self._process_msgs()

      self.gnss_handler.calculate_image_poses(self.image_handler.image_timestamps)
      self.gnss_handler.save_ego_poses(self.output_dir)
      self.imu_handler.save_imu_data()

  def _process_msgs(self):
      """Process synchronized messages"""
      if not self.image_queue.empty() and not self.pc_queue.empty():
          image_msg = self.image_queue.get()
          pc_msg = self.pc_queue.get()

          t_image = image_msg.header.stamp.sec + image_msg.header.stamp.nanosec / 1e9
          t_pc = pc_msg.header.stamp.sec + pc_msg.header.stamp.nanosec / 1e9 + self.time_diff
          dt = abs(t_image - t_pc)

          if dt < 0.1:
              self.capture_diff += dt
              self.total_count += 1
              if dt < self.capture_diff_thresh:
                  self.valid_count += 1
                  self.image_handler.process_image(image_msg, image_msg.header.stamp)
                  self.pc_handler.process_pointcloud(pc_msg, image_msg.header.stamp)
                  self.image_handler.generate_proj_image(image_msg, pc_msg)
                  self.image_handler.image_timestamps.append(image_msg.header.stamp)
          elif t_image > t_pc:
              self.image_queue.put(image_msg)
          else:
              self.pc_queue.put(pc_msg)