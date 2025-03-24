import argparse
import cv2
import numpy as np
import os
from tqdm import tqdm

def extract_frames_every_n_seconds(video_path:str, 
								   thumbnails_output_dir:str, 
								   seconds_between_frames:float=15, 
								   resolution:tuple=(320,240)):
	"""
	Extract frames from a video every n seconds.

	[Arguments]
		video_path - path to the video file
		thumbnails_output_dir - directory to save the thumbnails
		seconds_between_frames - interval between frames
		resolution - resolution of the thumbnails
	
	[Returns]
		nothing
	"""

	# Create the output directory if it doesn't exist
	thumbnails_output_dir = f"{thumbnails_output_dir}"
	if not os.path.exists(thumbnails_output_dir):
		os.makedirs(thumbnails_output_dir)

	# Open the video file
	cap = cv2.VideoCapture(video_path)
	
	# Get video properties
	total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	fps = cap.get(cv2.CAP_PROP_FPS)
	frame_interval = int(fps * seconds_between_frames)  # Frame interval based on desired seconds

	# Counter
	for frame_nb in range(0, total_frames, frame_interval):

		# Get frame
		cap.set(cv2.CAP_PROP_POS_FRAMES, frame_nb)

		# Read frame
		success, frame = cap.read()
		if not success:
			continue

		# Resize
		frame = cv2.resize(frame, resolution)
		
		# Save frame
		cv2.imwrite(f"{thumbnails_output_dir}/{str(frame_nb).zfill(7)}.jpg", frame)

	cap.release()


def convert_images_to_np_array(thumbnails_parent_dir:str, 
							   thumbnails_npy_output_dir:str):
	"""
	Convert images to numpy array

	[Arguments]
		image_path - path to the image file

	[Returns]
		nothing. Writes to npy file
	"""

	# Create the output directory if it doesn't exist
	thumbnails_npy_output_dir = f"{thumbnails_npy_output_dir}"
	if not os.path.exists(thumbnails_npy_output_dir):
		os.makedirs(thumbnails_npy_output_dir)

	# Grab list of directories in the thumbnails directory
	thumbnails_dirs = os.listdir(thumbnails_parent_dir)
	thumbnails_dirs.sort()

	# Loop through every videos' thumbnails
	for video_id in thumbnails_dirs:
		
		# Read the thumbnails
		thumbnails = os.listdir(f"{thumbnails_parent_dir}/{video_id}")
		thumbnails.sort()
		
		# Read and flatten
		thumbnails_array = []
		for thumbnail in thumbnails:
			thumbnail_path = f"{thumbnails_parent_dir}/{video_id}/{thumbnail}"
			thumbnail_array = cv2.imread(thumbnail_path)
			thumbnails_array.append(thumbnail_array.flatten())

		# Save the thumbnails as npy
		np.save(f"{thumbnails_npy_output_dir}/{video_id}.npy", np.array(thumbnails_array))


def extract_frames_every_n_seconds_dir(videos_parent_dir:str,
									   thumbnails_output_parent_dir:str,
									   seconds_between_frames:float=15, 
									   resolution:tuple=(320,240)):
	

	# Go to videos_parent_dir and list all videos
	videos = [f for f in os.listdir(videos_parent_dir) if f.endswith(".mp4")]
	thumbnails_dir_name = f"thumbnails_{seconds_between_frames}secsPerFrame_{resolution[0]}px{resolution[1]}px"
	
	# Iterate over all videos
	for video in tqdm(videos):

		print(f"Processing video: {video}")

		# Get video ID
		video_id = video.split(".")[0]

		# Define local parameters
		video_path = f"{videos_parent_dir}/{video}"
		thumbnails_output_dir = f"{thumbnails_output_parent_dir}/{thumbnails_dir_name}/{video_id}"

		# Extract frames from video
		extract_frames_every_n_seconds(
			video_path=video_path,
			thumbnails_output_dir=thumbnails_output_dir,
			seconds_between_frames=seconds_between_frames,
			resolution=resolution
		)


if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="Extract frames from a video every n seconds.")
	parser.add_argument("--videos_parent_dir", type=str, required=True, help="Path to the directory containing all the videos")
	parser.add_argument("--thumbnails_output_parent_dir", type=str, required=True, help="Path to the directory to save the thumbnails")
	parser.add_argument("--seconds_between_frames", type=int, default=60, help="Interval between frames in seconds")
	parser.add_argument("--resolution", type=int, nargs=2, default=(320, 240), help="Resolution of the thumbnails")

	args = parser.parse_args()

	extract_frames_every_n_seconds_dir(
		videos_parent_dir=args.videos_parent_dir,
		thumbnails_output_parent_dir=args.thumbnails_output_parent_dir,
		seconds_between_frames=args.seconds_between_frames,
		resolution=tuple(args.resolution)
	)


