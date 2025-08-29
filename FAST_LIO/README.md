# Fast-LIO for ROVR Data

This project is a modified version of Fast-Lio(refer to README_fastlio_origin.md), specifically for processing data from the ROVR platform.

### Modifications
1.  **Adapted for ROVR LiDAR Data:** Updated the point cloud subscriber and pre-processing logic to be compatible with the ROVR sensor's data format and topics.
2.  **Removed Dependency on Livox Drivers:** Eliminated the specific reliance on Livox LiDAR drivers, making the solution more generic.
3.  **Modified IMU Frame:** Adjusted the IMU frame transformation to align with the ROVR's physical sensor configuration and ROS 2 convention (`imu_link`).
4.  **Georeferencing and Export:** Transforms the point cloud into the UTM coordinate system based on GNSS position input and saves the final map as a `.las` file for geospatial applications.

### Dependencies
Ensure you have a ROS 2 environment installed and sourced.
Install the required system and ROS packages:
```bash
sudo apt install libpdal-dev ros-${ROS_DISTRO}-nmea-msgs libproj-deb
```

### Build
Clone and build the package within your ROS 2 workspace:
```bash
cd <your_ros2_ws>/src
git clone {this_repository_url}
cd ..
rosdep install --from-paths src --ignore-src -y
colcon build
```

### Run
1.  Source the workspace and launch the mapping node:
    ```bash
    cd <your_ros2_ws>
    source install/setup.bash # Use 'setup.zsh' if you use zsh
    ros2 launch fast_lio mapping.launch.py config_file:=rs_m1p.yaml
    ```
2.  Play back your ROS 2 bag file containing the sensor data:
    ```bash
    ros2 bag play rovr_sample_bag
    ```

**Output:** The processed point cloud map will be saved in the `PCD/` directory
---
