import argparse
import cv2
import os

def get_video_info(video_path):

	cap = cv2.VideoCapture(video_path)
	print(video_path)
	fps = cap.get(cv2.CAP_PROP_FPS)
	if fps == 0:
		raise ValueError('Could not get FPS from video')

	total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	duration = total_frames / fps

	return fps, total_frames, duration

def write_to_csv(video_id:str, fps:int, total_frames:int, duration:float, csv_output_dir:str):

	# Check if csv file exists. If not, create a new one
	try:
		with open(f'{csv_output_dir}/video_metadata.csv', 'r') as f:
			pass
	except FileNotFoundError:
		with open(f'{csv_output_dir}/video_metadata.csv', 'w') as f:
			f.write('video_path,fps,total_frames,duration (s)\n')

	# Write to csv file
	with open(f'{csv_output_dir}/video_metadata.csv', 'a') as f:
		f.write(f'{video_id},{fps},{total_frames},{duration}\n')

def write_video_info_to_csv(video_path:str, video_id:str, csv_output_dir:str):
	
	fps, total_frames, duration = get_video_info(video_path)
	write_to_csv(video_id, fps, total_frames, duration, csv_output_dir)


def write_video_info_to_csv_for_dir(video_dir:str, csv_output_dir:str):
	
	videos = os.listdir(video_dir)
	videos = [file for file in videos if file.endswith('.mp4')]
	videos.sort()

	for video in videos:
		video_path = f'{video_dir}/{video}'
		video_id = video.split('.')[0]
		write_video_info_to_csv(video_path, video_id, csv_output_dir)

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="Extract video metadata")
	parser.add_argument("--video_dir", type=str, required=True, help="Path to the video file")
	parser.add_argument("--csv_output_dir", type=str, required=True, help="Path to the output csv file")
	args = parser.parse_args()

	write_video_info_to_csv_for_dir(video_dir=args.video_dir, csv_output_dir=args.csv_output_dir)