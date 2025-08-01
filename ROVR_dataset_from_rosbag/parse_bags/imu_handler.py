import os
import csv

class IMUHandler:
  def __init__(self, output_dir):
      self.output_dir = output_dir
      self.imu_data = []
      # os.makedirs(os.path.join(output_dir, 'imu'), exist_ok=True)

  def process_imu(self, msg):
      """Process IMU message"""
      try:
          self.imu_data.append({
              'timestamp': f"{msg.header.stamp.sec}.{msg.header.stamp.nanosec:09d}",
              'acc_x': msg.linear_acceleration.x,
              'acc_y': msg.linear_acceleration.y,
              'acc_z': msg.linear_acceleration.z,
              'gyro_x': msg.angular_velocity.x,
              'gyro_y': msg.angular_velocity.y,
              'gyro_z': msg.angular_velocity.z
          })
      except Exception as e:
          print(f"IMU processing error: {str(e)}")

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