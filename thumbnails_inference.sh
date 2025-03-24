# Put all your videos in data/videos/ before running this script

# Step 1 - Create necessary directories if they don't exist
mkdir -p data/model_weights data/prediction_metrics data/prediction_results data/prediction_visualisations data/thumbnails data/videos data/videos_metadata

# Step 2 - Install the required packages
pip install -r requirements.txt

# Step 3 - Download model weights
wget -P "data/model_weights" wget https://huggingface.co/shawnliewhongwei/wayangkulit-segmentation/resolve/main/split1_network.iter-32.net

# Step 4 - Run inference
python3 -m src.o4_fact.src.infer --cfg_path "data/model_logs/split1_args.json" --thumbnails_dir "data/thumbnails/thumbnails_60secsPerFrame_320px240px" --mapping_path "data/model_logs/class_mapping.txt" --weights_path "data/model_weights/split1_network.iter-32.net" --results_output_path "data/prediction_results/thumbnails_60secsPerFrame_320px240px_preds.json" --overwrite_output_json

# Step 5.1 - Compute prediction metrics
python3 -m src.o5_results.generate_interlude_duration --results_path "data/prediction_results/thumbnails_60secsPerFrame_320px240px_preds.json" --output_metric_dir "data/prediction_metrics"

# Step 5.2 - Render the PDF visualisations
python3 -m src.o5_results.render_interlude_thumbnails --results_json_path "data/prediction_results/thumbnails_60secsPerFrame_320px240px_preds.json" --thumbnails_parent_dir "data/thumbnails/thumbnails_60secsPerFrame_320px240px/" --thumbnails_render_resolution 160 120 --num_cols 10 --output_pdf_dir "data/prediction_visualisations"