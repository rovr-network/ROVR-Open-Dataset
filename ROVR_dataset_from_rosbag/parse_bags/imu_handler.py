import os
import csv
import numpy as np
from scipy.spatial.transform import Rotation as R

class IMUHandler:
  def __init__(self, output_dir):
      self.output_dir = output_dir
      self.imu_data = []
      # os.makedirs(os.path.join(output_dir, 'imu'), exist_ok=True)
      # Complementary filter parameters
      self.alpha = 0.98  # Gyroscope weight (high frequency)
      self.beta = 0.02   # Accelerometer weight (low frequency)
      
      # Attitude state
      self.current_quaternion = np.array([1.0, 0.0, 0.0, 0.0])  # [w, x, y, z]
      self.last_imu_time = 0
      self.current_rpy = np.zeros(3)  # [roll, pitch, yaw] in radians

  def process_imu(self, msg):
      """Process IMU message with complementary filter and return roll/pitch"""
      try:
          timestamp = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
          
          # Extract IMU measurements
          gyro_data = np.array([
              -msg.angular_velocity.x,
              msg.angular_velocity.y, 
              msg.angular_velocity.z
          ])
          
          accel_data = np.array([
              -msg.linear_acceleration.x,
              msg.linear_acceleration.y,
              msg.linear_acceleration.z
          ])
          
          # Calculate time delta
          dt = timestamp - self.last_imu_time if self.last_imu_time > 0 else 0.01
          
          # Update complementary filter
          self._update_complementary_filter(gyro_data, accel_data, dt, timestamp)
          
          # Store raw IMU data with attitude
          self.imu_data.append({
              'timestamp': f"{msg.header.stamp.sec}.{msg.header.stamp.nanosec:09d}",
              'acc_x': msg.linear_acceleration.x,
              'acc_y': msg.linear_acceleration.y,
              'acc_z': msg.linear_acceleration.z,
              'gyro_x': msg.angular_velocity.x,
              'gyro_y': msg.angular_velocity.y,
              'gyro_z': msg.angular_velocity.z
          })
          
          # Update last time
          self.last_imu_time = timestamp
          
          # Return current roll and pitch in degrees
          return {
              'roll_deg': np.degrees(self.current_rpy[0]),
              'pitch_deg': np.degrees(self.current_rpy[1]),
              'quaternion': self.current_quaternion.copy(),
              'timestamp': timestamp
          }
              
      except Exception as e:
          print(f"IMU processing error: {str(e)}")
          return {
              'roll_deg': 0.0,
              'pitch_deg': 0.0,
              'quaternion': np.array([1.0, 0.0, 0.0, 0.0]),
              'timestamp': 0.0
          }

  def _update_complementary_filter(self, gyro_data, accel_data, dt, timestamp):
      """Update attitude using complementary filter"""
      # Normalize accelerometer data
      accel_norm = np.linalg.norm(accel_data)
      if accel_norm < 1e-6:
          return
          
      accel_normalized = accel_data / accel_norm
      
      # 1. Gyroscope integration (high frequency response)
      if np.linalg.norm(gyro_data) > 1e-6:
          # Convert to rotation vector and create delta quaternion
          rotation_vector = gyro_data * dt
          delta_rotation = R.from_rotvec(rotation_vector)
          delta_quat = delta_rotation.as_quat()  # [x, y, z, w]
          delta_quat = np.array([delta_quat[3], delta_quat[0], delta_quat[1], delta_quat[2]])  # [w, x, y, z]
          
          # Apply gyroscope integration
          gyro_quat = self._quaternion_multiply(self.current_quaternion, delta_quat)
      else:
          gyro_quat = self.current_quaternion.copy()
      
      # 2. Accelerometer correction (low frequency response)
      # Estimate gravity direction from current orientation
      gravity_est = self._quaternion_rotate_vector(self.current_quaternion, np.array([0, 0, 1]))
      
      # Measured gravity direction (accelerometer measures opposite of gravity)
      gravity_meas = -accel_normalized
      
      # Calculate correction vector (cross product)
      correction_vector = np.cross(gravity_est, gravity_meas)
      
      # Apply correction (complementary filter)
      correction_quat = np.array([
          1.0,  # scalar part
          correction_vector[0] * self.beta,
          correction_vector[1] * self.beta, 
          correction_vector[2] * self.beta
      ])
      
      # Normalize correction quaternion
      correction_norm = np.linalg.norm(correction_quat)
      if correction_norm > 1e-6:
          correction_quat /= correction_norm
      
      # Fuse gyroscope and accelerometer data
      fused_quat = (self.alpha * gyro_quat + self.beta * correction_quat)
      fused_quat /= np.linalg.norm(fused_quat)
      
      # Update current state
      self.current_quaternion = fused_quat
      
      # Convert to Euler angles for easy access
      rotation = R.from_quat([fused_quat[1], fused_quat[2], fused_quat[3], fused_quat[0]])
      self.current_rpy = rotation.as_euler('xyz')  # [roll, pitch, yaw] in radians

  def _quaternion_multiply(self, q1, q2):
      """Multiply two quaternions q1 * q2"""
      w1, x1, y1, z1 = q1
      w2, x2, y2, z2 = q2
      
      w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
      x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
      y = w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2
      z = w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2
      
      return np.array([w, x, y, z])

  def _quaternion_rotate_vector(self, q, v):
      """Rotate vector v by quaternion q"""
      q_vec = q[1:]
      q_scalar = q[0]
      
      # Using quaternion rotation formula
      v_rot = (q_scalar**2 - np.dot(q_vec, q_vec)) * v
      v_rot += 2 * np.dot(q_vec, v) * q_vec
      v_rot += 2 * q_scalar * np.cross(q_vec, v)
      
      return v_rot

  def save_imu_data(self):
      """Save IMU data to CSV"""
      if not self.imu_data:
          return

      imu_csv_path = os.path.join(self.output_dir, 'imu_data.csv')

      with open(imu_csv_path, 'w', newline='') as csvfile:
          writer = csv.DictWriter(csvfile, fieldnames=[
              'timestamp', 'acc_x', 'acc_y', 'acc_z', 
              'gyro_x', 'gyro_y', 'gyro_z'
          ])
          writer.writeheader()
          writer.writerows(self.imu_data)