# ROS2 Bag Processor 

## Overview
This is a toolkit for processing ROS2 bag files, capable of extracting images, point clouds, GNSS, and IMU data from bag files, and performing time alignment and coordinate transformation.

## Features
- Extract and save .png images named by image timestamps
- Extract point cloud data and save in .pcd format, named by the nearest image timestamp for easy alignment
- Parse GNSS data and calculate vehicle poses
- Record IMU sensor data
- Project point clouds onto image planes to generate depth maps
- Support multi-process parallel processing of multiple bag files
- Automatically load camera calibration parameters

## Environment Setup

### System Requirements
- Ubuntu: Recommended 18.04 or higher
- Python: 3.8+
- ROS2: Version corresponding to the Ubuntu system

### Dependency Installation
```bash
# Install ROS2 (take Humble as example) Refer to ROS official documentation
https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html

# Install Python dependencies
pip3 install numpy opencv-python pyproj pyyaml
```

## Directory Structure
```
├── bag_reader.py          # Read ros2bag
├── gnss_handler.py        # GNSS data processing
├── image_handler.py       # Image processing
├── imu_handler.py         # IMU data processing
├── pointcloud_handler.py  # Point cloud processing
└── main.py                # Batch processing script
```

## Usage

### Batch Processing Script
```bash
python3 -m parse_bags.main \
    --input /path/to/bags_directory \
    --output /output/directory \
    --sn-dir /path/to/sn_folders \
    --sample /optional/sample/output
```

### Single Bag File Processing
```python
from bag_reader import Ros2BagProcessor

processor = Ros2BagProcessor(
    bag_path="/path/to/bag.data",
    output_dir="/output/directory",
    sn_base_dir="/path/to/sn_folders"
)
processor.process_bag()
```

Parameter Description:
- `--input`: Input directory containing ROS2 bag files
- `--output`: Root output directory for processed results
- `--sn-dir`: Directory containing SN folders with camera calibration parameters
- `--sample`: (Optional) Directory for storing sample images

## Output Structure
Each processed bag generates a directory containing:
```
├── images/            # Original images
├── pointclouds/       # Point cloud data
├── project/           # Point cloud projection images
├── depth/             # Depth maps
├── ego_poses.json     # Poses corresponding to image timestamps
├── ego_poses_raw.json # Raw GNSS data
└── imu_data.csv       # IMU sensor data
```

## SN Folder Description
SN folders should contain camera calibration parameters, named by camera SN codes, with the following structure:
```
SN
├──1025040008/
    ├── int.yaml      # Camera intrinsic parameters
    └── ext.yaml      # Camera-LiDAR extrinsic parameters
├──1025040009/
    ├── int.yaml      # Camera intrinsic parameters
    └── ext.yaml      # Camera-LiDAR extrinsic parameters
```

## Notes
- If there are fewer than 130 valid image-point cloud pairs, it indicates potential issues with the clips, and the output directory will be automatically deleted
- Automatic parallel processing on multi-core CPUs (default 4 threads)
- The number of threads can be adjusted by modifying `num_processes` in `main.py`