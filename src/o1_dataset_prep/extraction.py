import cv2
import numpy as np
import os
import typing
from tqdm import tqdm

def generate_image_thumbnails_from_video(video_filepath:str, 
                                         video_id:str, 
                                         output_dir:str, 
                                         seconds_per_frame:float, 
                                         output_resolution:tuple[int,int]=(320,240)):
    """
    [Usage]
        Extracts a keyframe from the video every {seconds_between_samples} seconds and saves it as a jpg file.

    [Arguments]
        video_filepath    - path to the video
        video_id          - video_id identifier (e.g. 4k7uwgFI9DA)
        output_dir        - path to the output directory
        seconds_per_frame - samples keyframes every {seconds_per_frame} seconds
        output_resolution - specifies the resolution of the output keyframes
        
    [Returns]
        nothing. Saves the keyframes in the output directory.
    """

    # Make the folder first if it doesnt exist
    folder_path = f"{output_dir}/video_{video_id}"
    if os.path.exists(output_dir) == False:
        os.makedirs(folder_path, exist_ok=False)

    # Get video metadata
    print(video_filepath)
    cap = cv2.VideoCapture(video_filepath)
    fps = cap.get(cv2.CAP_PROP_FPS)
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Video {video_id} - FPS: {fps} - Total Num Frames: {num_frames}")

    # Save frames every {seconds_per_frame} at resolution {output_resolution}
    for frame_nb in tqdm(range(0, num_frames, int(fps*seconds_per_frame))):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_nb)
        _, frame = cap.read()
        frame_resized = cv2.resize(frame, output_resolution)
        cv2.imwrite(f'{folder_path}/{str(frame_nb).zfill(7)}.jpg', frame_resized)

    # Cleanup
    cap.release()

def generate_np_arrays_from_images(image_dir_dir:str, 
                                   output_dir:str):
    """
    [Usage]
        Converts a directory containing the directory of images into a directory of numpy arrays. 
        This would be used for feeding into the FACT model.

    [Arguments]
        image_dir_dir - path to the directory containing the directory of images
        output_dir    - path to the output directory
        
    [Returns]
        nothing. Saves the numpy arrays in the output directory.
    """

    # Make the output folder first if it doesn't exist
    if os.path.exists(output_dir) == False:
        os.makedirs(output_dir, exist_ok=False) 

    # For each image directory, load the images and save them as numpy arrays
    frames_dir_list = os.listdir(image_dir_dir)
    frames_dir_list.sort()

    for images_dir in frames_dir_list:
        if images_dir.startswith('video_'):

            # Get the video ID
            video_id = images_dir.split('_')[1]

            # Convert the jpg images into numpy arrays
            all_frames_array = []
            for frame_name in os.listdir(images_dir):
                if frame_name.endswith('.jpg'):
                    image = cv2.imread(f'{images_dir}/{frame_name}')
                    image_array = np.array(image).flatten()
                    all_frames_array.append(image_array)

            np.save(f'{output_dir}/video_{video_id}.npy', all_frames_array)