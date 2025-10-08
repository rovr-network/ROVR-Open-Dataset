import os
import json
import math
from pyproj import Proj
import numpy as np

class GNSSHandler:
  def __init__(self):
      self.gnss_data = []
      self.image_poses = []
      self.zone_id = -1
      self.gpgga_buffer = []
      self.gprmc_buffer = []
      self.matched_data = []

      self.recent_attitudes = []
      self.max_attitude_history = 500

  def add_attitude_data(self, attitude_data):
      """Add attitude data from IMU for later use"""
      self.recent_attitudes.append(attitude_data)
      
      # Keep only recent history
      if len(self.recent_attitudes) > self.max_attitude_history:
          self.recent_attitudes.pop(0)

  def get_attitude_for_timestamp(self, target_timestamp):
      """Get attitude data for specific timestamp using nearest neighbor"""
      if not self.recent_attitudes:
          return None
          
      # Find closest attitude data
      closest = min(self.recent_attitudes, key=lambda x: abs(x['timestamp'] - target_timestamp))
      
      # Check if time difference is acceptable (100ms threshold)
      if abs(closest['timestamp'] - target_timestamp) > 0.1:
          return None
          
      return closest

  def process_gnss(self, msg, current_attitude=None):
      """Process GPRMC message"""
      try:
          timestamp = self._to_sec(msg.header.stamp)
          sentence = str(msg.sentence)
          
          if 'RMC' in sentence:
              attitude_to_use = current_attitude or self.get_attitude_for_timestamp(timestamp)
              parsed_rmc = self._parse_gprmc(sentence, timestamp, attitude_to_use)
              if parsed_rmc:
                  self.gprmc_buffer.append(parsed_rmc)
                  self._try_match_data()
                  
          elif 'GGA' in sentence:
              parsed_gga = self._parse_gpgga(sentence, timestamp)
              if parsed_gga:
                  self.gpgga_buffer.append(parsed_gga)
                  self._try_match_data()

          # for rmc_data in self.gprmc_buffer:
          #     print(f"Warning: Unmatched GPRMC data at timestamp {rmc_data['timestamp']}")
          #     rmc_data["utm_z"] = 0.0
          #     # self._update_with_roll_pitch(rmc_data)
          #     self.matched_data.append(rmc_data)
          #     self.gnss_data.append(rmc_data)

      except Exception as e:
          print(f"GNSS processing error: {str(e)}")

  def _try_match_data(self):
      if self.gprmc_buffer and self.gpgga_buffer:
          self.gprmc_buffer.sort(key=lambda x: x["timestamp"])
          self.gpgga_buffer.sort(key=lambda x: x["timestamp"])
          
          matched_indices = set()
          for i, rmc_data in enumerate(self.gprmc_buffer):
              best_match_idx = None
              min_time_diff = float('inf')
              
              for j, gga_data in enumerate(self.gpgga_buffer):
                  if j in matched_indices:
                      continue
                  
                  time_diff = abs(rmc_data["timestamp"] - gga_data["timestamp"])
                  if time_diff < min_time_diff and time_diff < 0.2:  
                      min_time_diff = time_diff
                      best_match_idx = j
              
              if best_match_idx is not None:
                  matched_data = self._combine_rmc_gga(rmc_data, self.gpgga_buffer[best_match_idx])
                  self.matched_data.append(matched_data)
                  self.gnss_data.append(matched_data)
                  matched_indices.add(best_match_idx)
                  # print("find match",len(self.gnss_data))
          
          self.gprmc_buffer = [rmc for i, rmc in enumerate(self.gprmc_buffer) 
                              if i not in [idx for idx in range(len(self.gprmc_buffer)) 
                                        if i not in matched_indices]]
          self.gpgga_buffer = [gga for j, gga in enumerate(self.gpgga_buffer) 
                              if j not in matched_indices]
          

  def _combine_rmc_gga(self, rmc_data, gga_data):
      combined = rmc_data.copy()
      combined["utm_z"] = gga_data["elevation"]
      # combined["gga_timestamp"] = gga_data["timestamp"]
      # combined["time_diff"] = abs(rmc_data["timestamp"] - gga_data["timestamp"])
      
      # self._update_with_roll_pitch(combined)
      
      return combined

  def calculate_image_poses(self, image_timestamps):
      """Calculate poses for all image timestamps"""
      if not self.gnss_data or not image_timestamps:
          return

      min_time = self.gnss_data[0]["timestamp"]
      max_time = self.gnss_data[-1]["timestamp"]

      for ts in image_timestamps:
          img_time = self._to_sec(ts)
          if min_time <= img_time <= max_time:
              pose = self._interpolate_pose(ts)
          elif img_time < min_time:
              pose = self._extrapolate_pose(ts, False)
          else:
              pose = self._extrapolate_pose(ts, True)

          if pose:
              pose["token"] = f"{ts.sec}.{ts.nanosec:09d}"
              self.image_poses.append(pose)

  def save_ego_poses(self, output_dir):
      """Save pose information"""
      full_pose_path = os.path.join(output_dir, 'ego_poses_raw.json')
      with open(full_pose_path, 'w') as f:
          json.dump(self.gnss_data, f, indent=2)

      image_pose_path = os.path.join(output_dir, 'ego_poses.json')
      with open(image_pose_path, 'w') as f:
          json.dump(self.image_poses, f, indent=2)

  def _parse_gprmc(self, gprmc_msg, timestamp, attitude_data=None):
      parts = gprmc_msg.split(',')
      if len(parts) < 10 or parts[0].find("RMC") == -1 or parts[2] != 'A':
          return None

      # Parse latitude
      lat = float(parts[3][:2]) + float(parts[3][2:]) / 60
      if parts[4] == 'S':
          lat = -lat
          
      # Parse longitude
      lon = float(parts[5][:3]) + float(parts[5][3:]) / 60
      if parts[6] == 'W':
          lon = -lon
          
      # Parse speed (knots to m/s)
      speed_knots = float(parts[7]) if parts[7] else 0.0
      speed_mps = speed_knots * 0.514444
      
      # Parse heading (degrees)
      heading = float(parts[8]) if parts[8] else 0.0
      
      # Parse date
      date_str = parts[9] if len(parts) > 9 else ""
      
      # Determine UTM zone
      if self.zone_id == -1:
          self.zone_id = int((lon + 180) // 6) + 1

      # Calculate UTM coordinates
      projector = Proj(proj='utm', zone=self.zone_id, ellps='WGS84')
      x, y = projector(lon, lat)
      z = 0.0  # Assume altitude is 0

      # Use IMU attitude if available, otherwise use GNSS-only
      if attitude_data:
          # Use IMU roll/pitch with GNSS heading
          roll_deg = attitude_data['roll_deg']
          pitch_deg = attitude_data['pitch_deg']
          yaw_rad = math.radians(heading)
          
          # Create full quaternion
          quaternion = self._create_quaternion_from_rpy(
              math.radians(roll_deg), 
              math.radians(pitch_deg), 
              yaw_rad
          )
      else:
          # Fallback to GNSS-only (yaw only)
          yaw_rad = math.radians(heading)
          quaternion = [math.cos(yaw_rad / 2), 0.0, 0.0, math.sin(yaw_rad / 2)]
          roll_deg, pitch_deg = 0.0, 0.0

      return {
          "timestamp": timestamp,
          "lat": lat,
          "lon": lon,
          "utm_x": x,
          "utm_y": y,
          "utm_z": z,
          "heading": heading,
          "speed": speed_mps,
          "date": date_str,
          "hemisphere_ns": parts[4],
          "hemisphere_ew": parts[6],
          "quaternion": quaternion
      }

  def _parse_gpgga(self, gpgga_msg, timestamp):
      parts = gpgga_msg.split(',')
      if len(parts) < 10 or parts[0].find("GGA") == -1:
          return None
      
      try:
          elevation = float(parts[9]) if parts[9] else 0.0
          if len(parts) > 10 and parts[10] == 'F':  
              elevation *= 0.3048
          
          return {
              "timestamp": timestamp,
              "elevation": elevation
          }
          
      except (ValueError, IndexError) as e:
          print(f"GPGGA parsing error: {e}")
          return None

  def _interpolate_pose(self, target_time_stamp):
      """Interpolate pose, handling heading angle correctly"""
      if not self.gnss_data:
          return None
      target_time = self._to_sec(target_time_stamp)
      # If only one pose, return it directly
      if len(self.gnss_data) == 1:
          return self.gnss_data[0]
          
      # Find nearest poses before and after
      before = None
      after = None
      for pose in self.gnss_data:
          if pose["timestamp"] <= target_time:
              before = pose
          else:
              after = pose
              break
              
      # If target time is before or after all poses, use extrapolation
      if not before:
          return self._extrapolate_pose(target_time_stamp, extrapolate_forward=False)
      if not after:
          return self._extrapolate_pose(target_time_stamp, extrapolate_forward=True)
          
      # Calculate interpolation ratio
      tsa = after["timestamp"]
      tsb = before["timestamp"]
      time_diff = tsa - tsb
      if time_diff == 0:
          return before
          
      ratio = (target_time - tsb) / time_diff
      
      # Linear interpolation for lat/lon and UTM coordinates
      lat = before["lat"] + (after["lat"] - before["lat"]) * ratio
      lon = before["lon"] + (after["lon"] - before["lon"]) * ratio
      utm_x = before["utm_x"] + (after["utm_x"] - before["utm_x"]) * ratio
      utm_y = before["utm_y"] + (after["utm_y"] - before["utm_y"]) * ratio
      utm_z = before["utm_z"] + (after["utm_z"] - before["utm_z"]) * ratio
      speed = before["speed"] + (after["speed"] - before["speed"]) * ratio
      
      # Special handling for heading angle interpolation
      heading_diff = self._angle_diff(after["heading"], before["heading"])
      heading = before["heading"] + heading_diff * ratio
      
      # Handle quaternion interpolation
      quaternion = self._slerp_quaternion(before["quaternion"], after["quaternion"], ratio)
      
      # Build interpolation result
      interpolated = {
          "timestamp": f"{target_time_stamp.sec}.{target_time_stamp.nanosec:09d}",
          "lat": lat,
          "lon": lon,
          "utm_x": utm_x,
          "utm_y": utm_y,
          "utm_z": utm_z,
          "heading": heading % 360,
          "speed": max(0, speed),
          "date": before["date"],
          "hemisphere_ns": 'N' if lat >= 0 else 'S',
          "hemisphere_ew": 'E' if lon >= 0 else 'W',
          "quaternion": quaternion
      }
      
      return interpolated

  def _angle_diff(self, a, b):
      """Calculate smallest difference between two angles (considering 360° wrap)"""
      diff = (a - b + 180) % 360 - 180
      return diff if diff != -180 else 180

  def _extrapolate_pose(self, target_time_stamp, extrapolate_forward=True):
      """Extrapolate pose, including lat/lon and UTM coordinates"""
      if not self.gnss_data:
          return None
          
      # Select reference points for extrapolation
      if extrapolate_forward:
          # Use last two points for forward extrapolation
          if len(self.gnss_data) < 2:
              return None
          p1 = self.gnss_data[-2]
          p2 = self.gnss_data[-1]
      else:
          # Use first two points for backward extrapolation
          if len(self.gnss_data) < 2:
              return None
          p1 = self.gnss_data[0]
          p2 = self.gnss_data[1]
          
      # Calculate time difference
      dt = p2["timestamp"] - p1["timestamp"]
      target_time = self._to_sec(target_time_stamp)
      if dt == 0:
          return p2.copy()
          
      # Calculate extrapolation time
      extrapolate_dt = target_time - (p2["timestamp"] if extrapolate_forward else p1["timestamp"])
      
      # Calculate lat/lon change rate (degrees/second)
      dlat_dt = (p2["lat"] - p1["lat"]) / dt
      dlon_dt = (p2["lon"] - p1["lon"]) / dt
      
      # Calculate UTM coordinate change rate (meters/second)
      dx_dt = (p2["utm_x"] - p1["utm_x"]) / dt
      dy_dt = (p2["utm_y"] - p1["utm_y"]) / dt
      dz_dt = (p2["utm_z"] - p1["utm_z"]) / dt
      
      dspeed_dt = (p2["speed"] - p1["speed"]) / dt
      
      # Calculate heading change rate (considering angle wrap)
      heading_diff = self._angle_diff(p2["heading"], p1["heading"])
      dheading_dt = heading_diff / dt

      # Calculate extrapolated values
      lat = p2["lat"] + dlat_dt * extrapolate_dt if extrapolate_forward else p1["lat"] + dlat_dt * extrapolate_dt
      lon = p2["lon"] + dlon_dt * extrapolate_dt if extrapolate_forward else p1["lon"] + dlon_dt * extrapolate_dt
      utm_x = p2["utm_x"] + dx_dt * extrapolate_dt if extrapolate_forward else p1["utm_x"] + dx_dt * extrapolate_dt
      utm_y = p2["utm_y"] + dy_dt * extrapolate_dt if extrapolate_forward else p1["utm_y"] + dy_dt * extrapolate_dt
      utm_z = p2["utm_z"] + dz_dt * extrapolate_dt if extrapolate_forward else p1["utm_z"] + dz_dt * extrapolate_dt
      heading = p2["heading"] + dheading_dt * extrapolate_dt if extrapolate_forward else p1["heading"] + dheading_dt * extrapolate_dt
      speed = p2["speed"] + dspeed_dt * extrapolate_dt if extrapolate_forward else p1["speed"] + dspeed_dt * extrapolate_dt
      
      # Normalize heading to 0-360 degrees
      heading = heading % 360
      
      # Ensure lat/lon are within valid ranges
      lat = max(-90, min(90, lat))
      lon = max(-180, min(180, lon))
      
      # Ensure speed is not negative
      speed = max(0, speed)
      
      # Calculate quaternion
      quaternion = self._heading_to_quaternion(heading)
      
      # Build extrapolation result
      extrapolated = {
          "timestamp": f"{target_time_stamp.sec}.{target_time_stamp.nanosec:09d}",
          "lat": lat,
          "lon": lon,
          "utm_x": utm_x,
          "utm_y": utm_y,
          "utm_z": utm_z,
          "heading": heading,
          "speed": speed,
          "date": p2["date"] if extrapolate_forward else p1["date"],
          "hemisphere_ns": 'N' if lat >= 0 else 'S',
          "hemisphere_ew": 'E' if lon >= 0 else 'W',
          "quaternion": quaternion
      }
      
      return extrapolated

  def _heading_to_quaternion(self, heading_deg):
      """Convert heading angle to quaternion"""
      heading_rad = math.radians(heading_deg)
      qw = math.cos(heading_rad / 2)
      qx = 0.0
      qy = 0.0
      qz = math.sin(heading_rad / 2)
      return [qw, qx, qy, qz]

  def _slerp_quaternion(self, q1, q2, ratio):
      """Spherical linear interpolation for quaternions"""
      dot = sum(a*b for a, b in zip(q1, q2))
      
      # If dot product is negative, negate to take shortest path
      if dot < 0.0:
          q2 = [-x for x in q2]
          dot = -dot
          
      # If quaternions are very close, use linear interpolation
      if dot > 0.9995:
          result = [
              q1[i] + (q2[i] - q1[i]) * ratio
              for i in range(4)
          ]
          norm = math.sqrt(sum(x*x for x in result))
          return [x/norm for x in result]
          
      # Calculate angle and interpolate
      theta_0 = math.acos(dot)
      theta = theta_0 * ratio
      sin_theta = math.sin(theta)
      sin_theta_0 = math.sin(theta_0)
      
      s0 = math.cos(theta) - dot * sin_theta / sin_theta_0
      s1 = sin_theta / sin_theta_0
      
      return [
          s0 * q1[i] + s1 * q2[i]
          for i in range(4)
      ]

  def _create_quaternion_from_rpy(self, roll, pitch, yaw):
      """Create quaternion from roll, pitch, yaw angles"""
      cy = math.cos(yaw * 0.5)
      sy = math.sin(yaw * 0.5)
      cp = math.cos(pitch * 0.5)
      sp = math.sin(pitch * 0.5)
      cr = math.cos(roll * 0.5)
      sr = math.sin(roll * 0.5)
      
      qw = cr * cp * cy + sr * sp * sy
      qx = sr * cp * cy - cr * sp * sy
      qy = cr * sp * cy + sr * cp * sy
      qz = cr * cp * sy - sr * sp * cy
      
      return [qw, qx, qy, qz]
  
  def _to_sec(self, stamp):
      return stamp.sec + stamp.nanosec / 1e9