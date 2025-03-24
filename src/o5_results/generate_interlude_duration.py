import argparse
import csv
import json 
import re

def generate_interlude_durations(results_path:str, output_metric_dir:str):

    # Read prediction results
    with open(results_path,"r") as file:
        prediction_results = json.load(file)

    # Determine frames per second
    results_path = "data/prediction_results/thumbnails_60secsPerFrame_320px240px_preds.json"
    match = re.search(r"thumbnails_(.*?)secsPerFrame", results_path)
    if match:
        secsPerFrame = float(match.group(1))
    else:
        raise ValueError("Could not determine secsPerFrame!")

    # Check if metrics csv file exists
    output_metrics_path = f'{output_metric_dir}/interlude_durations.csv'
    try:
        with open(output_metrics_path, mode='r') as file:
            raise FileExistsError("File already exists!")
    except:
        pass

    # Write to csv file
    with open(output_metrics_path, mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(["video_id", "interlude_frames", "total_frames", "interlude_duration (mins)"])
        for video_id in prediction_results.keys():

            # Calculate number of interlude and total frames
            interlude_frames = sum(prediction_results[video_id]['pred'])
            total_frames = len(prediction_results[video_id]['pred'])
            interlude_duration = interlude_frames * secsPerFrame / 60

            # Write to csv file
            writer.writerow([video_id, interlude_frames, total_frames, interlude_duration])

if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(description='Generate interlude durations from prediction results.')
    parser.add_argument('--results_path', type=str, required=True, help='Path to prediction results json file.')
    parser.add_argument('--output_metric_dir', type=str, required=True, help='Path to output csv file.')
    args = parser.parse_args()

    generate_interlude_durations(results_path=args.results_path, output_metric_dir=args.output_metric_dir)
        