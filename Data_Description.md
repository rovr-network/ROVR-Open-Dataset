# Data Directory Structure and Field Specifications

## Overview

The ROVR Open Dataset provides **processed data saved only in ROS 2 bag format**, suitable for autonomous driving, robotics, and 4D perception tasks. This document outlines the directory structure and field specifications of the dataset.

## Data Directory Structure

```
ROVR-Open-Dataset/
├── Samples/                         # Sample data clips
│   ├── ${bag_name}/                 # Folder name matches ROS bag name
│   │   ├── images/                  # Image data (.png)
│   │   ├── pointclouds/             # Point cloud data (.pcd)
│   │   ├── annotation/              # Point cloud detection and segmentation results
│   │   │   ├── detection_result/    # Detection results (.txt)
│   │   │   └── segmentation_result/ # Segmentation results (.txt)
│   │   ├── ego_poses.json           # Interpolated GNSS positioning data
│   │   ├── ego_poses_raw.json       # Raw GNSS positioning data
│   │   └── imu_data.csv             # IMU data (CSV format)
├── ROVR_intrinsics_extrinsics/      # Camera and LiDAR parameter files
│   ├── ${device_serial}/            # Subfolder named by device serial number (e.g., 1025040009)
│   │   ├── ext.yaml                 # LiDAR-to-camera extrinsic parameters
│   │   └── int.yaml                 # Camera intrinsic parameters
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

### Sensor Data in `Samples/${bag_name}/`

| File/Folder         | Description                        | Format     | Frame Rate | Coordinate System Definition    |
|---------------------|------------------------------------|------------|------------|---------------------------------|
| images/             | Image data                         | .png       | 5 Hz       | X: Right,    Y: Down, Z: Forward|
| pointclouds/        | Point cloud data                   | .pcd       | 5 Hz       | X: Forward,  Y: Left, Z: Up     |
| annotation/         | Detection and segmentation results | .txt       | 5 Hz       |                                 |
| ego_poses.json      | Interpolated GNSS positioning data | .json      | 5 Hz       | According to GNSS standard      |
| ego_poses_raw.json  | Raw GNSS positioning data          | .json      | 1 Hz       | According to GNSS standard      |
| imu_data.csv        | IMU data                           | .csv       | 100 Hz     | X: Backward, Y: Left, Z: Down   |

### Camera and LiDAR Parameters in `ROVR_intrinsics_extrinsics/${device_serial}/`

| File/Folder         | Description                                                                                        | Format      |
|---------------------|----------------------------------------------------------------------------------------------------|-------------|
| ext.yaml            | LiDAR-to-camera extrinsic parameters, including rotation vector and translation vector.            | .yaml       |
| int.yaml            | Camera intrinsic parameters, including focal length, principal point, and distortion coefficients. | .yaml       |

---

## Descriptions:

### Sensor Data in `Samples/${bag_name}/`

#### **1. `images/`**

- **Description**: PNG format images with a resolution of 1920×1080 pixels.
- **File Naming Convention**:  
  The image filenames are based on UTC timestamps, precise to nanoseconds, ensuring that the file names correspond directly with other data files (point cloud, annotation).  

#### **2. `pointclouds/`**

- **Description**: PCD format point cloud data.
- **File Naming Convention**:  
  The point cloud filenames follow the same UTC timestamp convention as the image filenames, ensuring that each point cloud file corresponds to a specific image file.

#### **3. `annotation/`**

- **Description**: Detection and segmentation results for the images and point cloud.
- **File Naming Convention**:  
  The annotation filenames are also based on the same UTC timestamp as the corresponding image and point cloud files. This ensures that the annotations match the exact frame captured in the image and point cloud data.
  
##### **Object Detection Annotations (`detection_result/`)**

- **Description**: 3D and 2D object detection results in plain text format (.txt), each line representing a detected object with detailed fields. Each line contains:
```
[category_id] [tracking_id] [alpha] [x1] [y1] [x2] [y2] [height] [width] [length] [x] [y] [z] [rotation_y] [bbox_3d_points...]
```

###### **Explanation**:
- **category_id**: Object class ID:
  - 1: Motor_vehicle, 2: Pedestrian, 3: Non-motor_vehicle, 4: Traffic_light,
  - 5: Traffic_sign, 6: Lane_line, 7: Pole, 8: Traffic_cone, 9: Other, 10: Ground_marking, 11: Road.
- **tracking_id**: Unique ID for tracking the object across frames.
- **alpha**: Observation angle in radians, range [0, 2π].
- **x1, y1, x2, y2**: Top-left and bottom-right corners of the 2D bounding box (pixels). -1 for missing data.
- **height, width, length**: 3D size of the object (in meters).
- **x, y, z**: 3D location in camera coordinates (in meters).
- **rotation_y**: Rotation around Y-axis (radians), range [-π, π].
- **bbox_3d_points**: 8-point 3D bounding box, may be projected to 2D pixel space.

---

##### **Object Segmentation Annotations (`segmentation_result/`)**

- **Description**: 2D image segmentation masks with category and pixel coordinates per object. Each line contains:
```
[category_id] [object_id] [x1] [y1] [x2] [y2] ... [xn] [yn]
```

###### **Explanation**:
- **category_id**: Same ID system as detection annotations.
- **object_id**: Unique ID per segmented object.
- **[x1, y1], [x2, y2], ...**: Polygon points of the mask (in pixels).

---

##### **Notes on Annotation Data**

- **Coordinate Systems**:
  - 3D positions in detection results use camera coordinates. Apply the coordinate transformation from `ext.yaml` to align with LiDAR.
  - Some 3D bounding box fields may be 2D projected points — verify with dataset version.
  - Segmentation mask points are in pixel space, aligning with `../image/` data.

#### **4. `ego_poses_raw.json` and `ego_poses.json`**

- **Description**: 
- **`ego_poses_raw.json`**: Contains raw GNSS positioning data, which follows the GNSS standard with the following fields:
  - **Timestamp**: GNSS timestamp.
  - **lat**: Latitude.
  - **lon**: Longitude.
  - **utm_x, utm_y, utm_z**: UTM coordinates.
  - **heading**: Heading in degrees (0~360, clockwise from north).
  - **speed**: Speed in m/s.
  - **date**: Date in ddmmyy format.
  - **hemisphere_ns**: Northern or Southern hemisphere.
  - **hemisphere_ew**: Eastern or Western hemisphere.
  - **quaternion**: Quaternion representing the rotation.

- **`ego_poses.json`**: Contains interpolated GNSS positioning data based on image timestamp, following the same structure as `ego_poses_raw.json`, but with timestamps matching the image data.

| Field           | Description                                   |
|-----------------|-----------------------------------------------|
| timestamp       | GNSS timestamp                                |
| lat             | Latitude                                      |
| lon             | Longitude                                     |
| utm_x           | UTM X coordinate                              |
| utm_y           | UTM Y coordinate                              |
| utm_z           | UTM Z coordinate                              |
| heading         | Heading (0~360 degrees, clockwise from north) |
| speed           | Speed (in m/s)                                |
| date            | Date (ddmmyy format)                          |
| hemisphere_ns   | Northern or Southern Hemisphere               |
| hemisphere_ew   | Eastern or Western Hemisphere                 |
| quaternion      | Quaternion (rotation representation)          |

##### **Data Example**:
```json
{
  "timestamp": 1747503144.1424189,
  "lat": 37.77150665166667,
  "lon": -122.42305399166666,
  "utm_x": 550811.2977794447,
  "utm_y": 4180620.4009261196,
  "utm_z": 0.0,
  "heading": 332.79,
  "speed": 0.0,
  "date": "170525",
  "hemisphere_ns": "N",
  "hemisphere_ew": "W",
  "quaternion": [-0.9719404768572004, 0.0, 0.0, 0.23522693180543294]
}
```

- **Explanation**:
  - `ego_poses_raw.json` contains raw GNSS positioning data, with a frequency of 1 Hz.
  - `ego_poses.json` contains interpolated GNSS positioning data based on image timestamps, with a frequency of 5 Hz.


#### **5. `imu_data.csv`**

- **Description**: IMU raw data in CSV format with columns: [timestamp, acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z].

##### **Data Example**:
```csv
timestamp, acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z
1747503144.066422725,-0.06345245393458754,1.0756415122747423,9.818998864889146,6.807146783081999e-06,-0.0035436609232569302,0.0026104203575969863
1747503144.076391309,-0.055494749746285384,1.0912267539650202,9.795408273339271,0.0006594161759019893,-0.003767680104459781,0.0024891367766331452
1747503144.086524977,-0.07948344075120986,1.0916746506839992,9.802085208892823,0.0007679316679443117,-0.003132297461968387,0.0022016243500468475
```

- **Explanation**:
  - **Timestamp**: UTC Timestamp of the IMU data.
  - **acc_x, acc_y, acc_z**: Acceleration data in the X, Y, Z axes (in m/s²).
  - **gyro_x, gyro_y, gyro_z**: Gyroscope data in the X, Y, Z axes (in rad/s).
  - **Frequency**: 100 Hz.

### Camera and LiDAR Parameters in `ROVR_intrinsics_extrinsics/${device_serial}/`

#### 1. `ext.yaml` - LiDAR-Camera Extrinsic Parameters

- **Description**: Contains the extrinsic parameters that define the transformation from the LiDAR coordinate system to the camera coordinate system, using a rotation vector and a translation vector. The filename `ext.yaml` is fixed, with parameters specific to the device serial number.

##### **Data Example**:
```yaml
# x = -y  # y = -z  # z = x
lidar_to_camera:
  rvec: [1.7649999999999999, 1.008, 0.25209999999999999]  # Rotation vector. Rodrigues. [deg, deg, deg]
  tvec: [-0.016810000000000002, 0, 0.016810000000000002]  # Translation vector. [m, m, m]
```

- **Explanation**:
  - **rvec (Rotation Vector):** A 3D rotation vector using Rodrigues' rotation formula, given in degrees, describing the rotation between the LiDAR and camera coordinate systems. 
  - **tvec (Translation Vector):** A 3D vector describing the translation (offset) between the LiDAR and camera coordinate systems in meters.
  - **Transformation Matrix:** The full extrinsic transformation is represented as a 4x4 homogeneous matrix.

**Note:** Before applying extrinsic parameters, the LiDAR coordinate system must be transformed using the following rule:

```
x = -y
y = -z
z = x
```

---

#### 2. `int.yaml` - Camera Intrinsic Parameters

- **Description**: Contains the intrinsic parameters of the camera, including focal length, principal point, and distortion coefficients, which define the internal geometry of the camera. The filename `int.yaml` is fixed, with parameters specific to the device serial number.

##### **Data Example**:
```yaml
FX: 1190.9380383925
FY: 1190.8862851737
CX: 955.6705012175
CY: 540.1090098440
K1: -0.0586809591
K2: -0.4292077180
P1: -0.0000209962
P2: 0.0000513478
K3: -0.0282192110
K4: 0.3687679523
K5: -0.5661097302
K6: -0.1486583365
RMS: 0.0095
```

- **Explanation**:

  - **FX, FY:** Focal lengths in the X and Y axes (in pixels).
  - **CX, CY:** Principal point (optical center) in the X and Y axes (in pixels).
  - **K1, K2, K3, K4, K5, K6:** Radial distortion coefficients, modeling lens distortion.
  - **P1, P2:** Tangential distortion coefficients, modeling distortion due to lens misalignment.
  - **RMS:** Root mean square error of the calibration process.
  
---

## Usage

- **Data Access**: Find the processed data in the `Samples/${bag_name}/` folder, and the corresponding camera and LiDAR parameters in the `ROVR_intrinsics_extrinsics/${device_serial}/` folder.
- **Repository**: [https://github.com/rovr-network/ROVR-Open-Dataset](https://github.com/rovr-network/ROVR-Open-Dataset)  
  > This repository currently contains only one sample ROS bag. The full dataset will be open-sourced by the end of August, with download links provided.

## Contact

For inquiries or commercial licensing, please contact: [support@rovr.network](mailto:support@rovr.network).
