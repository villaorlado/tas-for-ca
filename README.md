# Computational segementation of Wayang Kulit video recordings using a Cross-Attention Temporal Model

# Overview
This repository provides tools for implementing Temporal Action Segmentation (TAS) in cultural analytics research. It was developed to support the study of narrative units in video materials, demonstrated through an analysis of comic interludes in Javanese wayang kulit (shadow puppet theater) performances.
The repository implements the FACT (Frame-Action Cross-attention Temporal Modeling) framework, which combines convolutional processing for frame-level features with transformer-based processing for action dependencies. This hybrid approach is particularly well-suited for cultural materials where training data may be limited.
The pipeline consists of four main components:
- **Frame Extraction**: Tools for extracting thumbnails/frames from video materials
- **Annotation Interface**: A Streamlit-based interface for labeling video segments
- **FACT Model Implementation**: Code for training and inference using the FACT action segmentation model
- **Visualization Tools**: Methods to render and visualize the segmentation results

This approach enables researchers to identify meaningful temporal segments in video materials based on culturally significant action sequences rather than just technical features like shot boundaries.

# Installation
Run the command
```bash
pip install -r requirements.txt
```

# Quick guide for inference

**If you only have the videos, do the following**
1. Place your videos in *data/videos/*
2. Run the script
```bash
bash video_inference.sh
```
3. Check *data/prediction_visualisations* for results
<em>Note: If you changed the parameters in Step 3.1, the folder names used in Steps 5, 6.1, 6.2 in **video_inference.sh** would be different. Do adjust accordingly.</em>

**If you already have the thumbnails, do the following**
1. Organise the thumbnails in the following manner 
* data/thumbnails/**thumbnails_dir_name**/**video_id_0**/**thumbnail_0_frame_nb**
* data/thumbnails/**thumbnails_dir_name**/**video_id_0**/**thumbnail_1_frame_nb**
* data/thumbnails/**thumbnails_dir_name**/**video_id_0**/**thumbnail_2_frame_nb**
* data/thumbnails/**thumbnails_dir_name**/**video_id_1**/**thumbnail_0_frame_nb**
* data/thumbnails/**thumbnails_dir_name**/**video_id_1**/**thumbnail_1_frame_nb**
* data/thumbnails/**thumbnails_dir_name**/**video_id_1**/**thumbnail_2_frame_nb**
2. Modify the folder names in Steps 4, 5.1, 5.2 in **thumbnails_inference.sh**
3. Run the script
```bash
bash thumbnails_inference.sh
```
4. Check *data/prediction_visualisations* for results

