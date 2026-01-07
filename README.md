# 🎥 Temporal Action Segmentation for the Analysis of Intangible Cultura Heritage

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

This repository provides a complete pipeline for collecting, annotating, and modeling **temporal action segmentation data**—with a special focus on **cultural analytics**. Our case study centers on *Wayang Kulit* (Indonesian shadow puppetry), showcasing how machine learning can be applied to analyze performance-based materials.

The project is structured into **three main modules**:
1. **YouTube Data Collection**  
2. **Interactive Labeling Interface**  
3. **Temporal Action Segmentation Model (FACT-based)**

---

## 📂 Project Structure Overview
```
├── 1_YouTubeAPI               # Data collection: Query and download YouTube videos
├── 2_labellingInterface       # Annotation: Svelte-based labeling tool for action segments
└── 3_FACT                     # Modeling: Temporal segmentation model training & inference
```

---

## 1 YouTube Data Collection (`1_YouTubeAPI`)
Tools for querying the **YouTube Data API** and downloading relevant videos, particularly performing arts materials like *Wayang Kulit*.

**Key Features:**
- Search videos by keywords and download metadata.
- Batch download YouTube videos using `yt-dlp`.

**Usage:**
- Configure API keys and search parameters.
- Download videos for dataset preparation.

📖 See detailed guide: [`1_YouTubeAPI/README.md`](1_YouTubeAPI/README.md)

---

## 2 Temporal Action Labeling Interface (`2_labellingInterface`)
An interactive **Svelte-based web app** that allows you to label temporal action segments directly on video timelines.

**Key Features:**
- Click-and-drag interface to create action segments.
- Edit or delete labels easily.
- (Planned) Export labeled data in JSON format for model training.

**Usage:**
- Run locally with `npm run dev`.
- Annotate videos with action labels like "Jump", "Sit", "Run".

📖 See detailed guide: [`2_labellingInterface/README.md`](2_labellingInterface/README.md)

---

## 3 Finetuning the FACT Model for Humanities Data (`3_FACT`)
Implements the **FACT (Frame-Action Cross-Attention Temporal Modeling)** architecture, adapting it for **humanities research** and **performing arts analysis**.

**Key Features:**
- Reproducible training on the **Breakfast dataset**.
- Example application to *Wayang Kulit* (dataset not distributed).
- Modular design: training, inference, and visualization.

**Usage:**
- Customize YAML configs for your dataset.
- Run training/inference pipelines with provided notebooks and scripts.

📖 See detailed guide: [`3_FACT/README.md`](3_FACT/README.md)

---

## 🌟 Project Goals
✅ Provide an end-to-end framework for **temporal action segmentation** in cultural heritage and performance studies.  
✅ Lower the barrier for humanities scholars to explore **machine learning applications**.  
✅ Offer reusable tools for dataset creation, labeling, and model training.

---

## 📌 Example Use Case: *Wayang Kulit* Performance Analysis
- **Collect** YouTube videos of *Wayang Kulit* performances.
- **Label** puppet movements, scene changes, or narrative actions.
- **Train** a model to segment new performance videos automatically.

---

## 📖 Citation (for FACT Model)
```bibtex
@inproceedings{
    lu2024fact,
    title={{FACT}: Frame-Action Cross-Attention Temporal Modeling for Efficient Supervised Action Segmentation},
    author={Zijia Lu and Ehsan Elhamifar},
    booktitle={Conference on Computer Vision and Pattern Recognition 2024},
    year={2024},
}
```

---

## 🤝 Acknowledgements
- FACT model from **CVPR 2024**
- Built with **SvelteKit**, **yt-dlp**, and **PyTorch**
- Focused on exploring ML for **cultural heritage and performing arts**

---

## 🔒 License
This project is licensed under the [MIT License](LICENSE).
