# Finetuning FACT (for the Humanities)

This repository adapts the **FACT (Frame-Action Cross-Attention Temporal Modeling)** architecture from the [CVPR 2024 paper by Lu and Elhamifar](https://openaccess.thecvf.com/content/CVPR2024/html/Lu_FACT_Frame-Action_Cross-Attention_Temporal_Modeling_for_Efficient_Action_Segmentation_CVPR_2024_paper.html) for **temporal action segmentation** with a special focus on **humanities research**.

## 🎭 About This Project
Our adaptation showcases how **temporal action segmentation techniques**—commonly used in video understanding tasks—can also be applied to cultural heritage materials. Specifically, we explore:
- **Wayang Kulit (Indonesian shadow puppet theatre)** as a case study.  
  > *Note: Due to copyright restrictions, the Wayang Kulit dataset is not included.*
- The **Breakfast dataset**, a standard benchmark dataset in action segmentation, used here to demonstrate model training and evaluation.

The project offers a framework for researchers interested in applying machine learning to performing arts and other humanities data requiring **temporal modeling**.

---

## 📂 Project Structure
```
├── BreakfastActionDataset.ipynb        # Notebook: Applying model to Breakfast dataset
├── WayangKulit.ipynb                   # Notebook: Wayang Kulit case study (data not included)
├── src/
│   ├── configs/                       # Configurations (YAML, Python)
│   ├── models/                        # Model components & loss functions
│   ├── utils/                         # Dataset utilities, metrics, evaluation
│   ├── visualisation/                 # Visualization tools
│   ├── thumbnails_extractor.py
│   ├── train_and_infer.py             # Main training & inference pipeline
│   └── home.py
└── README.md
```

---

## 🚀 Getting Started

### 📥 Install Dependencies
```bash
pip install -r requirements.txt
```

(Optional) Install additional tools for visualization and evaluation:
```bash
pip install wandb matplotlib seaborn
```

---

## 🛠 Training Instructions

### 1️⃣ Prepare the Dataset
- **Breakfast Dataset**: Download features from [Zenodo link](https://zenodo.org/records/3625992#.Xiv9jGhKhPY) and place it in `data/breakfast`.
- Structure should look like:
```
data/
└── breakfast/
    ├── features/
    ├── groundTruth/
```

> For your own dataset (like Wayang Kulit), prepare:
> - Numpy feature files (.npy)
> - Ground-truth label files (.txt)
> - A dataset config `.yaml` in `src/configs/`

---

### 2️⃣ Configure Training
Modify or create a YAML config file in `src/configs/`. Example:
```yaml
dataset: breakfast
features_path: data/breakfast/features
gt_path: data/breakfast/groundTruth
split: split1
epochs: 50
learning_rate: 0.0005
batch_size: 1
```

---

### 3️⃣ Run Training
From the project root:
```bash
python3 -m src.train_and_infer --cfg_path src/configs/breakfast.yaml --mode train
```
Model checkpoints and logs will be saved automatically (default: `logs/`).

---

## 🔎 Inference Example

Once trained (or with downloaded weights), run inference like so:
```bash
python3 -m src.train_and_infer   --cfg_path src/configs/breakfast.yaml   --mode infer   --thumbnails_dir data/thumbnails_npy/thumbnails_60secsPerFrame_320px240px   --mapping_path data/model_logs/class_mapping.txt   --weights_path data/model_weights/split1_network.iter-32.net   --output_json_path data/prediction_results/07nov_preds.json
```

👉 **Note:** Update paths based on your environment.

---

## 📖 Notebooks
- `BreakfastActionDataset.ipynb`: Reproducible run on the Breakfast dataset
- `WayangKulit.ipynb`: Conceptual application to Wayang Kulit (no dataset included)

---

## 🎯 Project Highlights
✅ Designed for applying **temporal segmentation** in **humanities research**  
✅ Customizable for **performance analysis** of **traditional arts**  
✅ Modular pipeline for **training**, **inference**, and **visualization**  
✅ Includes example notebooks for quick experimentation

---

## 📄 Citation (Original FACT Paper)
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
- Original FACT model by Lu & Elhamifar (CVPR 2024)
- This adaptation explores machine learning applications for **cultural heritage** and **performance arts** studies.
