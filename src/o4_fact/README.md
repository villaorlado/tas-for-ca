# FACT: Frame-Action Cross-Attention Temporal Modeling for Efficient Action Segmentation
The FACT model is based on the [https://openaccess.thecvf.com/content/CVPR2024/html/Lu_FACT_Frame-Action_Cross-Attention_Temporal_Modeling_for_Efficient_Action_Segmentation_CVPR_2024_paper.html](paper) authored by authored by Lu and Elhamifar in 2024. The paper's corresponding GitHub repository is located [https://github.com/ZijiaLewisLu/CVPR2024-FACT](here). 

Over here, the repository contains our adaptation of the FACT architecture. Note that we have modified some of the code and thus would not be exactly similar to the code in the original repository.

# Inference
For inference, 

1. Download the model weights from [https://huggingface.co/shawnliewhongwei/wayangkulit-segmentation/tree/main](here).
2. Run the command (adjust the location of the model weights if necessary)
```bash
python3 -m.src --cfg_path "../../data/model_logs/split1_args.json" --thumbnails_dir "../../data/thumbnails_npy/thumbnails_60secsPerFrame_320px240px" --mapping_path "../../data/model_logs/class_mapping.txt" --weights_path "../../data/model_weights/split1_network.iter-32.net" --output_json_path "../../data/prediction_results/07nov_preds.json"
```

# Training 
To be completed

