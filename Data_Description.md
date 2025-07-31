# ROVR Open Dataset - Data Directory Structure and Field Specifications

## Overview

The ROVR Open Dataset provides **processed data saved only in ROS 2 bag format**, suitable for autonomous driving, robotics, and 4D perception tasks. This document outlines the directory structure and field specifications of the dataset.

## Data Directory Structure

```
ROVR-Open-Dataset/
├── Samples/                     # Sample data clips
│   ├── ${bag_name}/             # Folder name matches ROS bag name
│   │   ├── images/              # Image data (.png)
│   │   ├── pointclouds/         # Point cloud data (.pcd)
│   │   ├── annotation/          # Point cloud detection and segmentation results
│   │   │   ├── detection_result/    # Detection results (.txt)
│   │   │   └── segmentation_result/ # Segmentation results (.txt)
│   │   ├── ego_poses.json       # Interpolated GNSS positioning data
│   │   ├── ego_poses_raw.json   # Raw GNSS positioning data
│   │   └── imu_data.csv         # IMU data (CSV format)
├── ROVR_intrinsics_extrinsics/  # Camera and LiDAR parameter files
│   ├── ${device_serial}/        # Subfolder named by device serial number (e.g., 1025040009)
│   │   ├── ext.yaml             # LiDAR-to-camera extrinsic parameters
│   │   └── int.yaml             # Camera intrinsic parameters
```

### Detailed Structure Description

1. **Samples/${bag_name}/**  
   - **Description**: Contains processed data clips with folder names matching the ROS bag names (e.g., `20250517173254-1025040009-34-lUNe`).
   - **Subfolders and files**:
     - `images/`: PNG images (1920 x 1080 px).
     - `pointclouds/`: Point cloud data in PCD format.
     - `annotation/`: Point cloud detection and segmentation results, containing:
       - `detection_result/`: Detection results in `.txt` format.
       - `segmentation_result/`: Segmentation results in `.txt` format.
     - `ego_poses.json`: Interpolated GNSS positioning data.
     - `ego_poses_raw.json`: Raw GNSS positioning data.
     - `imu_data.csv`: IMU data in CSV format.

2. **ROVR_intrinsics_extrinsics/${device_serial}/**  
   - **Description**: Camera and LiDAR parameters corresponding to the device serial number.
   - **Files**:
     - `ext.yaml`: LiDAR-to-camera extrinsic parameters (rotation matrix and translation vector).  
       - **Note**: Apply coordinate transform before use: `x = -y`, `y = -z`, `z = x`.
     - `int.yaml`: Camera intrinsic parameters (focal length, principal point, distortion coefficients).

## Naming Conventions

### Folder Naming Format

- **Format**: `<CollectionTime>-<DeviceSerialNumber>-<CollectionSequenceNumber>-<IdentifierCode>`
- **Example**: `20250517173254-1025040009-34-lUNe`
- **Field Explanation**:
  - **Collection Time**: `YYYYMMDDhhmmss` (e.g., May 17, 2025, 17:32:54), in Greenwich Mean Time (UTC).
  - **Device Serial Number**: Unique device identifier (e.g., 1025040009).
  - **Collection Sequence Number**: Sequence number within the collection (e.g., 34).
  - **Identifier Code**: Data verification identifier (e.g., lUNe).

### Sensor Data in Samples/${bag_name}/

| File/Folder         | Description                       | Format      |
|---------------------|-----------------------------------|-------------|
| images/             | PNG images                        | .png        |
| pointclouds/        | Point cloud data                  | .pcd        |
| annotation/         | detection & segmentation results  | .txt        |
| ego_poses.json      | Interpolated GNSS positioning data| .json       |
| ego_poses_raw.json  | Raw GNSS positioning data         | .json       |
| imu_data.csv        | IMU data                          | .csv        |

## Usage

- **Data Access**: Find processed data in the `Samples/${bag_name}/` folder and corresponding camera and LiDAR parameters under `ROVR_intrinsics_extrinsics/${device_serial}/`.
- **Repository**: [https://github.com/rovr-network/ROVR-Open-Dataset](https://github.com/rovr-network/ROVR-Open-Dataset)  
  > This repository currently contains only one sample ROS bag. The full dataset will be open-sourced by the end of August, with download links provided.

## Contact

For inquiries or commercial licensing, please contact: [support@rovr.network](mailto:support@rovr.network).
