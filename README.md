<div align="center">
  <img src="https://raw.githubusercontent.com/rovr-network/ROVR-Open-Dataset/main/images/rovrcar.jpg" alt="ROVR-Car" width="700"/>
</div>

# ROVR Open Dataset

[![arXiv](https://img.shields.io/badge/arXiv-2508.13977v1%20[cs.CV]-b31b1b)](https://arxiv.org/abs/2508.13977)
[![Project Page](https://img.shields.io/badge/Project%20Page-ROVR--Open--Dataset-blue)](https://xiandaguo.net/ROVR-Open-Dataset/)
[![Hugging Face 🤗](https://img.shields.io/badge/HuggingFace-ROVRNetwork-orange)](https://huggingface.co/ROVRNetwork)
[![Benchmark](https://img.shields.io/badge/Benchmark-ROVR%20Open%20Dataset-yellow)](https://drive.google.com/drive/folders/1nCT6grlveES2kYwYU6NPyjiF3rhJ-NZk?usp=sharing)


## Introduction
Welcome to the **ROVR Open Dataset** repository! This dataset is designed to empower autonomous driving and robotics research by providing rich, real-world data captured from ADAS cameras and LiDAR sensors. The dataset spans **50+ countries** with over **20 million kilometers** of driving data, making it ideal for training and developing advanced AI algorithms for depth estimation, object detection, and semantic segmentation.

<div align="center">
  <img src="https://raw.githubusercontent.com/rovr-network/ROVR-Open-Dataset/main/images/Exploded%20View.png" alt="LightCone" width="500"/>
</div>

## Key Features
- **Global Coverage:** 50+ countries with diverse driving environments and road scenarios.
- **High-Resolution Data:** Data from high-precision **ADAS cameras** and **LiDAR sensors**.
- **Real-World Scenarios:** Over **20M+ kilometers** of real-world driving data representing various environments and conditions.
- **Comprehensive Data Types:** Includes point clouds, monocular depth estimation, object detection, and semantic segmentation.

<div align="center">
  <img src="https://raw.githubusercontent.com/rovr-network/ROVR-Open-Dataset/main/images/Global%20coverage%20for%20scalable%20autonomy.png" alt="coverage" width="500"/>
</div>

## Dataset Overview
ROVR Open Dataset includes various data types to support different autonomous driving tasks:

- **LiDAR Point Clouds:** Dense 3D point clouds for precise depth estimation and scene analysis.
- **Monocular Depth Estimation:** High-precision depth information to aid autonomous driving perception.
- **Object Detection:** Real-time detection of vehicles, pedestrians, and obstacles.
- **Semantic Segmentation:** Pixel-level segmentation of roads, obstacles, and other features.
  
<table align="center">
  <tr>
    <td align="center" style="padding: 10px;">
      <img src="https://raw.githubusercontent.com/rovr-network/ROVR-Open-Dataset/main/images/points_cloud_uniform.gif" width="300"><br/>
      <strong>LiDAR Point Clouds</strong>
    </td>
    <td align="center" style="padding: 10px;">
      <img src="https://raw.githubusercontent.com/rovr-network/ROVR-Open-Dataset/main/images/monocular_depth_estimation_uniform.gif" width="300"><br/>
      <strong>Monocular Depth Estimation</strong>
    </td>
  </tr>
  <tr>
    <td align="center" style="padding: 10px;">
      <img src="https://raw.githubusercontent.com/rovr-network/ROVR-Open-Dataset/main/images/object_detection_uniform.gif" width="300"><br/>
      <strong>Object Detection</strong>
    </td>
    <td align="center" style="padding: 10px;">
      <img src="https://raw.githubusercontent.com/rovr-network/ROVR-Open-Dataset/main/images/semantic_segmentation_uniform.gif" width="300"><br/>
      <strong>Semantic Segmentation</strong>
    </td>
  </tr>
</table>

## ROVR Open Dataset Overview

### Dataset Volume
The first batch of the ROVR Open Dataset includes **1,363 clips**, each containing **30 seconds of data**, collected from diverse global environments to support autonomous driving research.

### Scene Coverage
The dataset spans three scene types, each with varied conditions to ensure comprehensive representation:

- **Highway**: High-speed road scenarios.
- **Urban**: City environments with complex traffic patterns.
- **Rural**: Less dense, open-road settings.

**Conditions**: Each scene type includes **Day**, **Night**, and **Rainy** conditions for robust scenario diversity.

### Dataset Split
The dataset is divided as follows:

- **Training Set**: 1,296 clips
- **Test Set**: 67 clips

### Annotations
- **Current**: Ground truth annotations are provided for **monocular depth estimation**.
- **Planned**: Annotations for **object detection** and **semantic segmentation** will be included in future releases.

### Future Releases
A second batch of data is planned for open-source release to further expand the dataset’s scope and utility.

## Challenges
We will be hosting global challenges to advance autonomous driving research. These challenges will focus on the following areas:

- **Monocular Depth Estimation (Coming Soon):** Depth estimation algorithms using camera and LiDAR ground truth.
- **Fusion Detection & Segmentation (Coming Soon):** Real-time vehicle and obstacle detection using camera and LiDAR data, along with pixel-level segmentation.

## Licensing

The dataset is available under the following licenses:

- **Open-Source License (CC BY-NC-SA 4.0):** Free for non-commercial research with attribution.
- **Commercial License (CC BY 4.0):** Full access for commercial use, with attribution required.

For detailed licensing information, please see [LICENSE.md](https://github.com/rovr-network/ROVR-Open-Dataset/blob/main/LICENSE.md).



## ROVR Network Open Dataset

### Getting Started
Explore, download, and contribute to **ROVR Open Dataset** to help shape the future of autonomous driving.

[![Access Dataset Samples](https://img.shields.io/badge/Access-Dataset%20Samples-blue)](https://github.com/rovr-network/ROVR-Open-Dataset/tree/main/Samples/20250517173254-1025040009-34-lUNe)

---

### Dataset Usage Rules
This dataset and its subsets can only be used after signing the [agreement](https://github.com/rovr-network/ROVR-Open-Dataset/blob/main/images/ROVR_Open_Dataset_Agreement.pdf).

Without permission, it is not allowed to forward, publish, or distribute this dataset or its subsets to any organization or individual in any way or by any means.

Any copy and sharing requests should be forwarded to the official contact email.

Please cite our paper if the **ROVR Open Dataset** is useful to your research.

---

### Full Dataset Access
All users can obtain and use this dataset and its subsets only after signing the Agreement and sending it to the official contact email.

For students, research groups, or research institutions who need to obtain this data, signatures of both the Responsible Party and the Point of Contact (POC) are required:

- **Responsible Party**: Tutor of the research group or a representative of the research institution, with authority to sign the agreement. Must be permanent personnel of the institution.
- **Point of Contact (POC)**: Individual with detailed knowledge of the dataset application. In some cases, the Responsible Party and the POC may be the same person.
- The homepage of the Responsible Party (or research group, laboratory, department, etc.) must be provided to prove the role.

Please send the signed Agreement in scanned copy format to the official contact email:
📧 [yuan.si@rovr.network](mailto:yuan.si@rovr.network)

Please CC the Responsible Party when sending the email.

**Email format for ROVR Open Dataset application**:

- **Subject**: ROVR Open Dataset Application
- **CC**: The email address of the Responsible Party
- **Attachment**: `ROVR_Open_Dataset_Agreement.pdf` (scanned copy)
---

### Citation
If you use the **ROVR Open Dataset** or related resources, please cite us as:

```bibtex
@article{guo2025rovr,
  title={ROVR-Open-Dataset: A Large-Scale Depth Dataset for Autonomous Driving},
  author={Guo, Xianda and Zhang, Ruijun and Duan, Yiqun and Wang, Ruilin and Zhou, Keyuan and Zheng, Wenzhao and Huang, Wenke and Xu, Gangwei and Horton, Mike and Si, Yuan and Zhao, Hao and Chen, Long},
  journal={arXiv preprint arXiv:2508.13977},
  year={2025}
}
```

## Join the Community

Contribute to the development of autonomous driving technologies by joining the ROVR community:

- [Visit our Official Website](https://rovr.network/#/) 
- [Follow us on X](https://x.com/ROVR_Network)
- [Join the Discussion on Discord](https://discord.com/invite/eUw3Hn4ruF)
- [Contribute on GitHub](https://github.com/rovr-network/ROVR-Open-Dataset/tree/main)

## Collaborators

We are proud to collaborate with the following partners, with more to be added in the future:

<table>
  <tr>
    <td align="center">
      <img src="https://raw.githubusercontent.com/rovr-network/ROVR-Open-Dataset/main/images/GeoDNET_logo.png" alt="GeoDNET Logo" height="80"/>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/rovr-network/ROVR-Open-Dataset/main/images/Tsinghua_logo.png" alt="Tsinghua Logo" height="80"/>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/rovr-network/ROVR-Open-Dataset/main/images/UC_Berkeley_logo.png" alt="UC Berkeley Logo" height="80"/>
    </td>
  </tr>
</table>

## Support & Documentation
For more information on how to get started, explore our documentation or contact us for support:

- [View the Documentation](https://rovr-network.gitbook.io/rovr-docs)
